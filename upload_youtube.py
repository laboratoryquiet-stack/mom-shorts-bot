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

import os

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",  # needed to read comments for audience_comments.py
]


def get_authenticated_service():
    """
    Loads token.json and returns an authenticated YouTube client.

    Automatic refresh: as long as token.json contains a refresh_token (it
    does, since we request offline access), the google-auth library
    automatically exchanges it for a fresh short-lived access token on every
    run — no human involvement needed for this part, indefinitely.

    The ONLY things that force a human back into a browser are:
    1. The very first login for a given set of scopes (unavoidable by
       design — a script silently minting its own first token would be a
       real security hole, not a missing feature).
    2. Changing the requested SCOPES list (adding/removing a permission
       always invalidates the old token and needs fresh consent — this is
       what happened when force-ssl was added).
    3. Your Google Cloud OAuth app being left in "Testing" publishing status,
       which makes Google force-expire the refresh token after 7 days. This
       is the one truly worth fixing once, so the bot never needs a human
       again: Google Cloud Console -> APIs & Services -> OAuth consent
       screen -> Publishing status -> Publish App.

    If a human DOES need to re-auth, this fails with a clear message rather
    than a cryptic RefreshError deep in a library stack trace.
    """
    if not os.path.exists("token.json"):
        raise RuntimeError(
            "token.json not found. Run `python upload_youtube.py --auth` once "
            "locally, then save its contents as the YT_TOKEN GitHub secret."
        )
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Persist the refreshed token so subsequent steps/commits see it too.
            with open("token.json", "w") as f:
                f.write(creds.to_json())
        return build("youtube", "v3", credentials=creds)
    except RefreshError as e:
        raise RuntimeError(
            "YouTube auth needs a human to re-login — this happens if scopes "
            "changed, access was revoked, or your Google Cloud OAuth app is "
            "still in 'Testing' mode (forces expiry every 7 days; fix by "
            "publishing the app in the OAuth consent screen settings). "
            "Fix: delete token.json, rerun `python upload_youtube.py --auth`, "
            "and update the YT_TOKEN GitHub secret with the new contents. "
            f"Original error: {e}"
        ) from e


def run_local_auth_flow():
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=0)
    with open("token.json", "w") as f:
        f.write(creds.to_json())
    print("Saved token.json — copy its contents into the YT_TOKEN GitHub secret.")


def upload_short(video_path: str, title: str, description: str, tags=None, cover_path: str = None):
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
    video_id = response.get("id")
    print("YouTube upload complete:", video_id)

    if cover_path:
        try:
            youtube.thumbnails().set(
                videoId=video_id, media_body=MediaFileUpload(cover_path, mimetype="image/jpeg")
            ).execute()
            print("Custom cover thumbnail set.")
        except Exception as e:
            # Custom thumbnails require a phone-verified channel, and
            # Shorts-specific cover support via the API isn't guaranteed -
            # this should never block the upload itself, which already
            # succeeded above.
            print(f"Cover thumbnail upload failed (non-fatal - video is still posted): {e}")

    return video_id


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
