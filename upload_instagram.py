"""
Publishes a Reel to Instagram via the Instagram Graph API (free).

One-time setup (manual — see README):
1. Convert your Instagram account to a Professional (Business/Creator) account.
2. Create a Facebook Page and link it to the Instagram account.
3. Create a Meta developer App at developers.facebook.com, add "Instagram Graph API".
4. Generate a long-lived Page Access Token with instagram_content_publish permission.
5. Get your IG Business Account ID (via /me/accounts -> page -> instagram_business_account).
Store IG_ACCESS_TOKEN and IG_USER_ID as GitHub Actions secrets.

Note: for personal/single-account use like this, Meta's standard App Review is
not required — "development mode" access with the account added as a tester
is sufficient. Full App Review is only needed to publish on OTHER people's accounts.
"""
import os
import time
import requests

GRAPH_ROOT = "https://graph.facebook.com/v19.0"


def publish_reel(video_url: str, caption: str) -> str:
    access_token = os.environ["IG_ACCESS_TOKEN"]
    ig_user_id = os.environ["IG_USER_ID"]

    # Step 1: create a media container
    r = requests.post(
        f"{GRAPH_ROOT}/{ig_user_id}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": access_token,
        },
        timeout=60,
    )
    r.raise_for_status()
    creation_id = r.json()["id"]

    # Step 2: poll until the container finishes processing
    status_url = f"{GRAPH_ROOT}/{creation_id}"
    for _ in range(30):
        status_resp = requests.get(
            status_url, params={"fields": "status_code", "access_token": access_token}, timeout=30
        )
        status_resp.raise_for_status()
        status_code = status_resp.json().get("status_code")
        if status_code == "FINISHED":
            break
        if status_code == "ERROR":
            raise RuntimeError("Instagram failed to process the video container.")
        time.sleep(10)
    else:
        raise TimeoutError("Instagram container never finished processing.")

    # Step 3: publish
    pub = requests.post(
        f"{GRAPH_ROOT}/{ig_user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": access_token},
        timeout=60,
    )
    pub.raise_for_status()
    media_id = pub.json()["id"]
    print("Instagram Reel published:", media_id)
    return media_id
