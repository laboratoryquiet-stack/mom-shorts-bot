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
"""
import hashlib
import json
import os
import random
from config import THEMES, OPENERS, AFFIRMATIONS, CLOSERS

STATE_PATH = "state.json"
SIGNATURE_HISTORY_SIZE = 200
MAX_DEDUP_ATTEMPTS = 10


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {
        "theme_index": 0,
        "bags": {},              # pool_key -> list[str] remaining items in current shuffle
        "recent_signatures": [],  # hashes of recently generated full scripts
        "post_count": 0,
    }


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def draw_from_bag(pool, state, pool_key):
    """Shuffle-bag draw: no repeats until the whole pool has been used once."""
    bags = state.setdefault("bags", {})
    bag = bags.get(pool_key)
    if not bag:
        bag = pool[:]
        random.shuffle(bag)
    item = bag.pop()
    bags[pool_key] = bag
    return item


def script_signature(lines):
    joined = "|".join(lines)
    return hashlib.sha256(joined.encode()).hexdigest()


def generate():
    state = load_state()

    theme = THEMES[state["theme_index"] % len(THEMES)]
    state["theme_index"] += 1

    history = state.setdefault("recent_signatures", [])
    lines = None

    for _ in range(MAX_DEDUP_ATTEMPTS):
        opener = draw_from_bag(OPENERS[theme], state, f"opener::{theme}")
        affirmations = [draw_from_bag(AFFIRMATIONS, state, "affirmations") for _ in range(3)]
        closer = draw_from_bag(CLOSERS, state, "closers")
        candidate = [opener, *affirmations, closer]
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
        "lines": lines,
        "post_number": state["post_count"],
    }


if __name__ == "__main__":
    import pprint
    pprint.pprint(generate())
