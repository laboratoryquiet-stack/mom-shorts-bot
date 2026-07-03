"""
Free, keyless trend signal: pulls today's top post titles from public
working-mom subreddits' JSON endpoints (no login/API key required for
read-only public data) and extracts keywords, so the theme selector can
lean into whatever's actually being talked about right now.

This is intentionally a *nudge*, not a hard override — if the request fails
(no network, Reddit rate-limits, etc.) it fails silently and the pipeline
falls back to normal rotation. Never let a trend-fetch failure break a post.
"""
import re
from collections import Counter

import requests

SUBREDDITS = ["workingmoms", "Mommit", "WorkingMomStyle"]
HEADERS = {"User-Agent": "mom-shorts-bot/1.0 (personal, non-commercial)"}

# Map keywords found in trending post titles -> theme keys from config.THEMES
KEYWORD_THEME_MAP = {
    "guilt": "morning_guilt",
    "school": "morning_guilt",
    "daycare": "morning_guilt",
    "time": "time_management",
    "schedule": "time_management",
    "burnout": "exhaustion_relief",
    "tired": "exhaustion_relief",
    "exhausted": "exhaustion_relief",
    "self care": "self_care_permission",
    "boundaries": "asking_for_help",
    "help": "asking_for_help",
    "perfect": "letting_go_of_perfect",
    "mess": "letting_go_of_perfect",
    "career": "career_confidence",
    "promotion": "career_confidence",
    "work": "career_confidence",
    "identity": "identity_beyond_mom",
    "myself": "identity_beyond_mom",
}


def fetch_trending_theme(timeout=8):
    """Returns a theme key nudged by today's real discussion, or None on any failure."""
    counter = Counter()
    try:
        for sub in SUBREDDITS:
            resp = requests.get(
                f"https://www.reddit.com/r/{sub}/top.json",
                params={"t": "day", "limit": 15},
                headers=HEADERS,
                timeout=timeout,
            )
            resp.raise_for_status()
            posts = resp.json()["data"]["children"]
            for post in posts:
                title = post["data"].get("title", "").lower()
                for keyword, theme in KEYWORD_THEME_MAP.items():
                    if re.search(rf"\b{re.escape(keyword)}\b", title):
                        counter[theme] += 1
        if not counter:
            return None
        return counter.most_common(1)[0][0]
    except Exception:
        return None  # network unavailable, rate-limited, schema changed, etc. -> just skip


if __name__ == "__main__":
    print(fetch_trending_theme())
