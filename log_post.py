"""Shared state-logging helper, used by both post_youtube.py and
post_instagram.py so learn.py has a single consistent log to read from,
regardless of which platform(s) actually posted."""
import datetime
import json
import os

STATE_PATH = "state.json"


def log_post(theme, opener, youtube_id, ig_media_id):
    state = {}
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            state = json.load(f)
    post_log = state.setdefault("post_log", [])
    post_log.append({
        "post_number": state.get("post_count", len(post_log) + 1),
        "theme": theme,
        "opener": opener,
        "youtube_id": youtube_id,
        "ig_media_id": ig_media_id,
        "posted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scored": False,
    })
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)
