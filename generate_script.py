"""
Generates a short script (list of caption lines) for one video.
Pure combinatorics over config.py banks -> free forever, no LLM API required.

Anti-repeat strategy:
1. "Shuffle bag" per pool (openers-per-theme, affirmations, closers, CTAs):
   each pool is shuffled into a queue and drawn from front-to-back with NO
   repeats until the entire bag is exhausted, then reshuffled - guaranteeing
   maximum spacing between repeats of any single line.
2. Full-script "signature" history: the exact line combination generated is
   hashed and checked against the last 200 posts. If a generated combo
   collides with a recent one, it reshuffles and tries again (affirmation
   posts only - the other content types are curated, not combinatorial, so
   collision is a non-issue there).

IMPORTANT: all anti-repeat/learning state lives in state.json. If your
deploy environment doesn't persist state.json between runs (e.g. a CI job
that starts from a fresh checkout every time), none of this actually works -
every run looks like the first run ever. See README's "State persistence"
section - the shipped GitHub Actions workflow commits state.json back to
the repo after every run specifically to avoid this.

Content type rotation (regular, non-spotlight/non-practical slots):
affirmation -> support -> humor -> myth_bust -> this_or_that -> (repeat)
Not everything is a mantra; variety is deliberate, both for the audience
and because a single repeating format that isn't clearing retention just
means the same failure repeated daily.

Theme selection order of preference (for combinatorial/affirmation posts):
1. If your own audience's comments (audience_comments.py) surface a theme,
   lean into it most of the time (highest-signal source - it's literally
   what your viewers are telling you).
2. Otherwise, if today's broader discussion (trending_topics.py) surfaces a
   theme, lean into it about half the time.
3. Otherwise, if learn.py has accumulated performance scores, weight theme
   selection toward what's actually been working.
4. Otherwise, if the current calendar month has a boosted theme list
   (config.CALENDAR_THEME_BOOST), pick from there.
5. Otherwise, fall back to plain round-robin rotation through THEMES.

Every script ends with a CTA drawn from config.CTA_POOL (comments/saves are
weighted heavily by the 2026 Shorts algorithm - so this rotates instead of
using one fixed line every time, though the pool still leans on the
original brand tagline as one of its options for consistency).
"""
import datetime
import hashlib
import json
import os
import random

from config import (
    THEMES, OPENERS, AFFIRMATIONS, CLOSERS, CTA_POOL,
    CALENDAR_THEME_BOOST, SPOTLIGHT_STORIES, FALLBACK_TAG,
    TIP_CONTENT, SUPPORT_CONTENT, HUMOR_CONTENT, MYTH_BUST_CONTENT,
    HACK_DEMO_CONTENT, THIS_OR_THAT_CONTENT, get_normalized_weights,
)
from trending_topics import fetch_trending_theme
from audience_comments import fetch_audience_theme

STATE_PATH = "state.json"
SIGNATURE_HISTORY_SIZE = 200
MAX_DEDUP_ATTEMPTS = 10
AFFIRMATIONS_PER_SCRIPT = 2    # tuned short on purpose - see README "Why 30s" note
SPOTLIGHT_EVERY_N = 5          # 1 in 5 posts is a real-women spotlight
TIP_EVERY_N = 3                # 1 in 3 non-spotlight posts is practical content (tips/hack)
TREND_NUDGE_PROBABILITY = 0.5  # how often a detected trend overrides plain rotation
AUDIENCE_NUDGE_PROBABILITY = 0.6  # audience comments are weighted higher than general trends
REGULAR_SLOT_ROTATION = ["affirmation", "support", "humor", "myth_bust", "this_or_that"]


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {
        "theme_index": 0,
        "spotlight_index": 0,
        "bags": {},
        "recent_signatures": [],
        "post_count": 0,
    }


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def draw_from_bag(pool, state, pool_key, score_dict=None):
    """Shuffle-bag draw: no repeats until the whole pool has been used once.
    If a score_dict is given, the pick within the current bag is weighted
    toward higher-performing items (still guarantees full coverage - it just
    changes the ORDER within each cycle, favoring winners sooner)."""
    bags = state.setdefault("bags", {})
    bag = bags.get(pool_key)
    if not bag:
        bag = pool[:]
        random.shuffle(bag)
    if score_dict:
        item = weighted_pick(bag, score_dict, explore_rate=0.4)
        bag.remove(item)
    else:
        item = bag.pop()
    bags[pool_key] = bag
    return item


def script_signature(lines):
    joined = "|".join(lines)
    return hashlib.sha256(joined.encode()).hexdigest()


def weighted_pick(items, score_dict, explore_rate=0.3):
    """
    Epsilon-greedy selection: most of the time, favor items with a higher
    learned performance score; some of the time, pick freely so the system
    keeps exploring instead of tunnel-visioning on one early lucky winner.
    Items with no score yet default to a neutral weight so they still get a
    fair shot.
    """
    if random.random() < explore_rate or not score_dict:
        return random.choice(items)
    weights = [max(score_dict.get(item, 0.05), 0.01) for item in items]
    return random.choices(items, weights=weights, k=1)[0]


def choose_theme(state):
    audience = fetch_audience_theme()
    if audience and random.random() < AUDIENCE_NUDGE_PROBABILITY:
        return audience

    trending = fetch_trending_theme()
    if trending and random.random() < TREND_NUDGE_PROBABILITY:
        return trending

    theme_scores = state.get("theme_scores", {})
    if theme_scores:
        normalized = get_normalized_weights(theme_scores)
        return weighted_pick(THEMES, normalized)

    month = datetime.date.today().month
    boosted = CALENDAR_THEME_BOOST.get(month)
    if boosted and random.random() < 0.5:
        return random.choice(boosted)

    theme = THEMES[state["theme_index"] % len(THEMES)]
    state["theme_index"] += 1
    return theme


def pick_cta(state):
    return draw_from_bag(CTA_POOL, state, "cta")


def generate_spotlight(state):
    idx = state["spotlight_index"] % len(SPOTLIGHT_STORIES)
    state["spotlight_index"] += 1
    story = SPOTLIGHT_STORIES[idx]
    lines = [
        f"Real story: {story['name']}.",
        *story["lines"],
        random.choice(CLOSERS),
        pick_cta(state),
    ]
    return {"theme": FALLBACK_TAG, "opener": None, "lines": lines,
             "content_type": "spotlight"}


def generate_practical(state):
    """Alternates between a multi-tip list (TIP_CONTENT) and a single
    concrete hack (HACK_DEMO_CONTENT) each time this slot comes up, so
    'practical' posts aren't all the same shape either."""
    use_hack = state.get("practical_toggle", 0) % 2 == 1
    state["practical_toggle"] = state.get("practical_toggle", 0) + 1

    if use_hack:
        idx = state.get("hack_index", 0) % len(HACK_DEMO_CONTENT)
        state["hack_index"] = idx + 1
        item = HACK_DEMO_CONTENT[idx]
        body_lines = item["lines"]
        content_type = "hack_demo"
    else:
        idx = state.get("tip_index", 0) % len(TIP_CONTENT)
        state["tip_index"] = idx + 1
        item = TIP_CONTENT[idx]
        body_lines = item["tips"]
        content_type = "tips"

    lines = [item["hook"], *body_lines, random.choice(CLOSERS), pick_cta(state)]
    return {"theme": item["theme"], "opener": item["hook"], "lines": lines,
             "content_type": content_type}


def generate_support(state):
    idx = state.get("support_index", 0) % len(SUPPORT_CONTENT)
    state["support_index"] = idx + 1
    support_set = SUPPORT_CONTENT[idx]
    lines = [support_set["hook"], *support_set["lines"], random.choice(CLOSERS), pick_cta(state)]
    return {"theme": support_set["theme"], "opener": support_set["hook"], "lines": lines,
             "content_type": "support"}


def generate_humor(state):
    idx = state.get("humor_index", 0) % len(HUMOR_CONTENT)
    state["humor_index"] = idx + 1
    item = HUMOR_CONTENT[idx]
    lines = [item["hook"], *item["lines"], pick_cta(state)]
    return {"theme": item["theme"], "opener": item["hook"], "lines": lines,
             "content_type": "humor"}


def generate_myth_bust(state):
    idx = state.get("myth_index", 0) % len(MYTH_BUST_CONTENT)
    state["myth_index"] = idx + 1
    item = MYTH_BUST_CONTENT[idx]
    lines = [item["hook"], *item["lines"], pick_cta(state)]
    return {"theme": item["theme"], "opener": item["hook"], "lines": lines,
             "content_type": "myth_bust"}


def generate_this_or_that(state):
    idx = state.get("tot_index", 0) % len(THIS_OR_THAT_CONTENT)
    state["tot_index"] = idx + 1
    item = THIS_OR_THAT_CONTENT[idx]
    # Deliberately no extra CTA line appended here - the question itself is
    # the call to action, and tacking on another line dilutes it.
    lines = [item["hook"], *item["lines"]]
    return {"theme": item["theme"], "opener": item["hook"], "lines": lines,
             "content_type": "this_or_that"}


def generate_affirmation(state):
    history = state.setdefault("recent_signatures", [])
    lines = None
    theme = choose_theme(state)
    opener_scores = state.get("opener_scores", {})

    candidate = None
    for _ in range(MAX_DEDUP_ATTEMPTS):
        opener = draw_from_bag(OPENERS[theme], state, f"opener::{theme}", score_dict=opener_scores)
        affirmations = [draw_from_bag(AFFIRMATIONS, state, "affirmations")
                         for _ in range(AFFIRMATIONS_PER_SCRIPT)]
        closer = draw_from_bag(CLOSERS, state, "closers")
        cta = pick_cta(state)
        candidate = [opener, *affirmations, closer, cta]
        sig = script_signature(candidate)
        if sig not in history:
            lines = candidate
            history.append(sig)
            break
    else:
        lines = candidate
        history.append(script_signature(candidate))

    if len(history) > SIGNATURE_HISTORY_SIZE:
        del history[: len(history) - SIGNATURE_HISTORY_SIZE]

    return {"theme": theme, "opener": opener, "lines": lines,
             "content_type": "affirmation"}


_REGULAR_SLOT_GENERATORS = {
    "affirmation": generate_affirmation,
    "support": generate_support,
    "humor": generate_humor,
    "myth_bust": generate_myth_bust,
    "this_or_that": generate_this_or_that,
}


def generate():
    state = load_state()
    count = state["post_count"]

    if count > 0 and count % SPOTLIGHT_EVERY_N == 0:
        result = generate_spotlight(state)
    elif count > 0 and count % TIP_EVERY_N == 0:
        result = generate_practical(state)
    else:
        parity = state.get("regular_slot_parity", 0) % len(REGULAR_SLOT_ROTATION)
        state["regular_slot_parity"] = state.get("regular_slot_parity", 0) + 1
        slot = REGULAR_SLOT_ROTATION[parity]
        result = _REGULAR_SLOT_GENERATORS[slot](state)

    result["post_number"] = state["post_count"] + 1
    state["post_count"] += 1
    save_state(state)
    return result


if __name__ == "__main__":
    import pprint
    pprint.pprint(generate())
