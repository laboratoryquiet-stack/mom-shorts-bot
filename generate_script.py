"""
Generates a short script (list of caption lines) for one video.
Pure combinatorics over config.py banks -> free forever, no LLM API required.
Tracks used combinations in state.json so repeats are avoided until the pool
is exhausted (which takes a very long time given the bank sizes).
"""
import json
import os
import random
from config import THEMES, OPENERS, AFFIRMATIONS, CLOSERS

STATE_PATH = "state.json"


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"theme_index": 0, "used_openers": {}, "used_affirmations": [], "post_count": 0}


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def pick_unused(pool, used_list):
    remaining = [x for x in pool if x not in used_list]
    if not remaining:
        used_list.clear()
        remaining = pool[:]
    choice = random.choice(remaining)
    used_list.append(choice)
    return choice


def generate():
    state = load_state()

    theme = THEMES[state["theme_index"] % len(THEMES)]
    state["theme_index"] += 1

    used_openers_for_theme = state["used_openers"].setdefault(theme, [])
    opener = pick_unused(OPENERS[theme], used_openers_for_theme)

    # 3 affirmation lines per video, no immediate repeats
    lines = [opener]
    for _ in range(3):
        aff = pick_unused(AFFIRMATIONS, state["used_affirmations"])
        lines.append(aff)
    lines.append(random.choice(CLOSERS))

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
