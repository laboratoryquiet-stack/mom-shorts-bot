"""
Instagram/Facebook long-lived Page tokens last ~60 days but CAN be refreshed
before they expire via Meta's token refresh endpoint. This script refreshes
the token and writes the new value back into the GitHub repo's Actions
secret — so you never have to do it by hand.

Requires GH_PAT (GitHub Personal Access Token, classic, "repo" scope) —
Actions' default GITHUB_TOKEN can't modify secrets, only a PAT can.

Run on a schedule (weekly is plenty) — Meta allows refreshing a token any
time before it expires, extending it another ~60 days each time.
"""
import os

import requests

from github_secrets import update_github_secret

GRAPH_ROOT = "https://graph.facebook.com/v19.0"


def refresh_long_lived_token(current_token: str, app_id: str, app_secret: str) -> str:
    r = requests.get(
        f"{GRAPH_ROOT}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": current_token,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def main():
    current_token = os.environ["IG_ACCESS_TOKEN"]
    app_id = os.environ["META_APP_ID"]
    app_secret = os.environ["META_APP_SECRET"]

    new_token = refresh_long_lived_token(current_token, app_id, app_secret)
    update_github_secret("IG_ACCESS_TOKEN", new_token)
    print("Instagram token refreshed and GitHub secret updated.")


if __name__ == "__main__":
    main()
