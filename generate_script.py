"""
Generates a short script (list of caption lines) for one video.
Pure combinatorics over config.py banks -> free forever, no LLM API required.

Anti-repeat strategy:
1. "Shuffle bag" per pool (openers-per-theme, affirmations, closers): each
   pool is shuffled into a queue and drawn from front-to-back with NO repeats
   until the entire bag is exhausted, then reshuffled — guaranteeing maximum
   spacing between repeats of any single line (much stronger than plain
   random.choice, which can repeat the same line two posts in a row).
2. Full-script "signature" history: the exact 5-line combination generated is
   hashed and checked against the last 200 posts. If a generated combo
   collides with a recent one (rare, but possible on small banks), it
   reshuffles the affirmation picks and tries again, up to 10 attempts.

Theme selection order of preference:
1. Every SPOTLIGHT_EVERY_N posts -> a fact-checked real-woman spotlight story
   (config.SPOTLIGHT_STORIES), not a template combination.
2. Otherwise, if today's real-world discussion (trending_topics.py) surfaces
   a clear theme, lean into it ~50% of the time (still leaves room for
   rotation so the account doesn't only ever chase trends).
3. Otherwise, if the current calendar month has a boosted theme list
   (config.CALENDAR_THEME_BOOST), pick from there.
4. Otherwise, fall back to plain round-robin rotation through THEMES.

Every script ends with the same persona tagline (config.TAGLINE) — a fixed
sign-off used on every single video, the way a jingle or sign-off phrase
builds recognition over time.
"""
import datetime
import hashlib
import json
import os
import random

from config import (
    THEMES, OPENERS, AFFIRMATIONS, CLOSERS, TAGLINE,
    CALENDAR_THEME_BOOST, SPOTLIGHT_STORIES, FALLBACK_TAG,
    TIP_CONTENT,
)
from trending_topics import fetch_trending_theme
from audience_comments import fetch_audience_theme

STATE_PATH = "state.json"
SIGNATURE_HISTORY_SIZE = 200
MAX_DEDUP_ATTEMPTS = 10
SPOTLIGHT_EVERY_N = 5          # 1 in 5 posts is a real-women spotlight
TIP_EVERY_N = 3                # 1 in 3 posts (that isn't a spotlight) is a practical-tips list
TREND_NUDGE_PROBABILITY = 0.5  # how often a detected trend overrides plain rotation
AUDIENCE_NUDGE_PROBABILITY = 0.6  # audience comments are weighted higher than general trends


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
    toward higher-performing items (still guarantees full coverage — it just
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
        return weighted_pick(THEMES, theme_scores)

    month = datetime.date.today().month
    boosted = CALENDAR_THEME_BOOST.get(month)
    if boosted and random.random() < 0.5:
        return random.choice(boosted)

    theme = THEMES[state["theme_index"] % len(THEMES)]
    state["theme_index"] += 1
    return theme


def generate_spotlight(state):
    idx = state["spotlight_index"] % len(SPOTLIGHT_STORIES)
    state["spotlight_index"] += 1
    story = SPOTLIGHT_STORIES[idx]
    lines = [
        f"Real story: {story['name']}.",
        *story["lines"],
        random.choice(CLOSERS),
        TAGLINE,
    ]
    return {"theme": FALLBACK_TAG, "opener": None, "lines": lines, "post_number": state["post_count"] + 1}


def generate_tips(state):
    idx = state.get("tip_index", 0) % len(TIP_CONTENT)
    state["tip_index"] = idx + 1
    tip_set = TIP_CONTENT[idx]
    lines = [tip_set["hook"], *tip_set["tips"], random.choice(CLOSERS), TAGLINE]
    return {"theme": tip_set["theme"], "opener": tip_set["hook"], "lines": lines,
            "post_number": state["post_count"] + 1}


def generate():
    state = load_state()
    count = state["post_count"]

    # Periodic real-women spotlight, bypasses the template system entirely.
    if count > 0 and count % SPOTLIGHT_EVERY_N == 0:
        result = generate_spotlight(state)
        state["post_count"] += 1
        save_state(state)
        return result

    # Periodic practical-tips list (curated, not template-mixed).
    if count > 0 and count % TIP_EVERY_N == 0:
        result = generate_tips(state)
        state["post_count"] += 1
        save_state(state)
        return result

    history = state.setdefault("recent_signatures", [])
    lines = None
    theme = choose_theme(state)
    opener_scores = state.get("opener_scores", {})

    for _ in range(MAX_DEDUP_ATTEMPTS):
        opener = draw_from_bag(OPENERS[theme], state, f"opener::{theme}", score_dict=opener_scores)
        affirmations = [draw_from_bag(AFFIRMATIONS, state, "affirmations") for _ in range(3)]
        closer = draw_from_bag(CLOSERS, state, "closers")
        candidate = [opener, *affirmations, closer, TAGLINE]
        sig = script_signature(candidate)
        if sig not in history:
            lines = candidate
            history.append(sig)
            break
    else:
        # Extremely unlikely with the current bank sizes, but fail safe rather
        # than loop forever: accept the last candidate anyway.
        lines = candidate
        history.append(sig)

    if len(history) > SIGNATURE_HISTORY_SIZE:
        del history[: len(history) - SIGNATURE_HISTORY_SIZE]

    state["post_count"] += 1
    save_state(state)

    return {
        "theme": theme,
        "opener": opener,
        "lines": lines,
        "post_number": state["post_count"],
    }


if __name__ == "__main__":
    import pprint
    pprint.pprint(generate())
