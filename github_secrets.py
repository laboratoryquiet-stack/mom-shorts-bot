"""
Shared helper: writes a value into a GitHub repo's Actions secrets.
Used to auto-sync refreshed YouTube/Instagram tokens back to GitHub, so a
human never has to manually copy-paste an updated secret.

Requires a GitHub Personal Access Token (classic, "repo" scope) saved as the
GH_PAT secret — the default GITHUB_TOKEN Actions provides can't modify
secrets, only a PAT can.
"""
import base64
import os

import requests
from nacl import encoding, public


def update_github_secret(secret_name: str, secret_value: str):
    repo = os.environ["GITHUB_REPOSITORY"]
    pat = os.environ["GH_PAT"]
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
