"""
Pulls real performance data for previously published posts, so the pipeline
can learn what's actually working instead of just rotating blindly.

YouTube: uses videos.list statistics (free, same OAuth token as upload).
Instagram: uses the Graph API media insights endpoint — NOTE this requires
the `instagram_manage_insights` permission in addition to
`instagram_content_publish` on your access token (add it when generating
the token in Meta's Graph API Explorer / App Review settings).

Metric names on Meta's API do shift between versions — if Instagram stats
start failing, check the current field names at
developers.facebook.com/docs/instagram-api/guides/insights before assuming
the code is broken.
"""
import os

import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from upload_youtube import SCOPES as YT_SCOPES
GRAPH_ROOT = "https://graph.facebook.com/v19.0"


def get_youtube_stats(video_ids):
    if not video_ids:
        return {}
    creds = Credentials.from_authorized_user_file("token.json", YT_SCOPES)
    youtube = build("youtube", "v3", credentials=creds)
    stats = {}
    # API allows up to 50 IDs per call
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        resp = youtube.videos().list(part="statistics", id=",".join(batch)).execute()
        for item in resp.get("items", []):
            s = item["statistics"]
            stats[item["id"]] = {
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
            }
    return stats


def get_instagram_stats(media_ids):
    access_token = os.environ.get("IG_ACCESS_TOKEN")
    stats = {}
    for media_id in media_ids:
        try:
            resp = requests.get(
                f"{GRAPH_ROOT}/{media_id}/insights",
                params={"metric": "plays,likes,comments,shares,saved", "access_token": access_token},
                timeout=30,
            )
            resp.raise_for_status()
            data = {d["name"]: d["values"][0]["value"] for d in resp.json().get("data", [])}
            stats[media_id] = {
                "views": data.get("plays", 0),
                "likes": data.get("likes", 0),
                "comments": data.get("comments", 0),
                "shares": data.get("shares", 0),
                "saves": data.get("saved", 0),
            }
        except Exception as e:
            print(f"Instagram insights fetch failed for {media_id}: {e}")
    return stats


def engagement_score(stats: dict) -> float:
    """
    Simple, transparent scoring: engagement actions per view, not raw views —
    this avoids just favoring whichever post happened to post at a lucky time,
    and instead rewards content that made people actually react.
    """
    views = max(stats.get("views", 0), 1)
    actions = stats.get("likes", 0) + stats.get("comments", 0) * 3 + stats.get("shares", 0) * 5 + stats.get("saves", 0) * 4
    return actions / views
