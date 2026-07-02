"""
Instagram/Facebook long-lived Page tokens last ~60 days but CAN be refreshed
before they expire via Meta's token refresh endpoint. This script refreshes
the token and writes the new value back into the GitHub repo's Actions
secret — so you never have to do it by hand.

Requires one extra one-time setup item beyond the main README:
- A GitHub Personal Access Token (classic) with "repo" scope, saved as the
  GitHub secret GH_PAT. (Actions' default GITHUB_TOKEN can't modify secrets,
  a PAT is required for that one operation.)

Run this on a schedule (weekly is plenty, added to the workflow) — Meta
allows refreshing a token any time before it expires, extending it another
~60 days each time.
"""
import base64
import os

import requests
from nacl import encoding, public

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


def update_github_secret(repo: str, pat: str, secret_name: str, secret_value: str):
    headers = {"Authorization": f"Bearer {pat}", "Accept": "application/vnd.github+json"}

    key_resp = requests.get(
        f"https://api.github.com/repos/{repo}/actions/secrets/public-key",
        headers=headers, timeout=30,
    )
    key_resp.raise_for_status()
    key_data = key_resp.json()

    public_key = public.PublicKey(key_data["key"].encode(), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode())
    encrypted_b64 = base64.b64encode(encrypted).decode()

    put_resp = requests.put(
        f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}",
        headers=headers,
        json={"encrypted_value": encrypted_b64, "key_id": key_data["key_id"]},
        timeout=30,
    )
    put_resp.raise_for_status()


def main():
    current_token = os.environ["IG_ACCESS_TOKEN"]
    app_id = os.environ["META_APP_ID"]
    app_secret = os.environ["META_APP_SECRET"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pat = os.environ["GH_PAT"]

    new_token = refresh_long_lived_token(current_token, app_id, app_secret)
    update_github_secret(repo, pat, "IG_ACCESS_TOKEN", new_token)
    print("Instagram token refreshed and GitHub secret updated.")


if __name__ == "__main__":
    main()
