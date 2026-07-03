"""
Uploads a video to YouTube as a Short via the YouTube Data API v3 (free).

One-time setup (you do this manually — see README):
1. Create a Google Cloud project, enable "YouTube Data API v3".
2. Create OAuth 2.0 Client ID (Desktop app), download client_secret.json.
3. Run this file locally once (`python upload_youtube.py --auth`) to do the
   browser login and generate token.json.
4. Store both files' contents as GitHub Actions secrets:
   YT_CLIENT_SECRET (contents of client_secret.json)
   YT_TOKEN (contents of token.json)
   The workflow writes them back to disk before running.

Quota note: default quota is 10,000 units/day; each upload costs 1,600 units,
so 3 uploads/day (4,800 units) is well within the free daily limit.
"""
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",  # needed to read comments for audience_comments.py
]


def get_authenticated_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("youtube", "v3", credentials=creds)


def run_local_auth_flow():
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=0)
    with open("token.json", "w") as f:
        f.write(creds.to_json())
    print("Saved token.json — copy its contents into the YT_TOKEN GitHub secret.")


def upload_short(video_path: str, title: str, description: str, tags=None):
    youtube = get_authenticated_service()
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags or [],
            "categoryId": "22",  # People & Blogs
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
    print("YouTube upload complete:", response.get("id"))
    return response.get("id")


def post_affiliate_comment(video_id: str, comment_text: str):
    """
    Posts a top-level comment containing the affiliate link (comments allow
    clickable links). Requires the youtube.force-ssl scope, already added
    to SCOPES above.

    Honest limitation: YouTube's Data API does NOT have a documented,
    reliable endpoint for pinning a comment — pinning is a YouTube Studio UI
    action only. This function posts the comment (which does work, and
    channel-owner comments are often shown near the top by YouTube's own
    sorting), but it does not guarantee a pinned position. If you want it
    truly pinned, that's a 5-second manual tap in YouTube Studio after each
    post — I won't pretend the API does it automatically.
    """
    youtube = get_authenticated_service()
    insert_resp = youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {"snippet": {"textOriginal": comment_text}},
            }
        },
    ).execute()
    comment_id = insert_resp["snippet"]["topLevelComment"]["id"]
    print("Posted affiliate comment:", comment_id)
    return comment_id


if __name__ == "__main__":
    import sys
    if "--auth" in sys.argv:
        run_local_auth_flow()
