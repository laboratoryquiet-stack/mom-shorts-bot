"""
Listens to YOUR OWN audience — not a copied trend, but what people are
actually saying under your posts — and nudges future theme selection toward
whatever they're engaging with most.

Deliberately does NOT quote or display anyone's specific comment text on
screen (avoids consent/privacy issues with using someone's words without
permission). It only extracts keywords to bias which THEME gets picked next,
the same mechanism as trending_topics.py.

Requires broader permissions than the initial setup:
- YouTube: your OAuth token needs the `youtube.force-ssl` scope (not just
  `youtube.upload`) to read comments. Add it to upload_youtube.py's SCOPES
  and rerun `python upload_youtube.py --auth` once to reissue token.json
  with both scopes.
- Instagram: your access token needs `instagram_manage_comments` in addition
  to `instagram_content_publish` and `instagram_manage_insights`.

Fails silently on any error — a comments-fetch hiccup should never block a
scheduled post.
"""
import os
from collections import Counter

import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from trending_topics import KEYWORD_THEME_MAP

from upload_youtube import SCOPES as YT_SCOPES
GRAPH_ROOT = "https://graph.facebook.com/v19.0"


def _youtube_comment_texts(max_videos=5, max_comments_per_video=20):
    creds = Credentials.from_authorized_user_file("token.json", YT_SCOPES)
    youtube = build("youtube", "v3", credentials=creds)

    channel_resp = youtube.channels().list(part="id", mine=True).execute()
    channel_id = channel_resp["items"][0]["id"]

    search_resp = youtube.search().list(
        part="id", channelId=channel_id, order="date", maxResults=max_videos, type="video"
    ).execute()
    video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]

    texts = []
    for vid in video_ids:
        try:
            resp = youtube.commentThreads().list(
                part="snippet", videoId=vid, order="relevance", maxResults=max_comments_per_video
            ).execute()
            for item in resp.get("items", []):
                texts.append(item["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
        except Exception:
            continue  # comments disabled on that video, etc.
    return texts


def _instagram_comment_texts(max_media=5, max_comments_per_media=20):
    access_token = os.environ["IG_ACCESS_TOKEN"]
    ig_user_id = os.environ["IG_USER_ID"]

    media_resp = requests.get(
        f"{GRAPH_ROOT}/{ig_user_id}/media",
        params={"fields": "id", "limit": max_media, "access_token": access_token},
        timeout=30,
    )
    media_resp.raise_for_status()
    media_ids = [m["id"] for m in media_resp.json().get("data", [])]

    texts = []
    for media_id in media_ids:
        resp = requests.get(
            f"{GRAPH_ROOT}/{media_id}/comments",
            params={"fields": "text", "limit": max_comments_per_media, "access_token": access_token},
            timeout=30,
        )
        if resp.ok:
            texts.extend(c["text"] for c in resp.json().get("data", []))
    return texts


def fetch_audience_theme():
    """Returns a theme key nudged by real comments on your own posts, or None."""
    all_texts = []
    try:
        all_texts.extend(_youtube_comment_texts())
    except Exception:
        pass
    try:
        all_texts.extend(_instagram_comment_texts())
    except Exception:
        pass

    if not all_texts:
        return None

    counter = Counter()
    for text in all_texts:
        lowered = text.lower()
        for keyword, theme in KEYWORD_THEME_MAP.items():
            if keyword in lowered:
                counter[theme] += 1

    if not counter:
        return None
    return counter.most_common(1)[0][0]


if __name__ == "__main__":
    print(fetch_audience_theme())
