"""
Instagram's Graph API requires video_url to be a PUBLICLY reachable URL
(it fetches the file itself — it won't accept a raw upload).
Free trick: create a GitHub Release in this repo and attach the mp4 as an
asset. GitHub gives it a permanent public download URL, at zero cost.

Requires: GITHUB_TOKEN (Actions provides this automatically) and
GITHUB_REPOSITORY (also auto-provided by Actions, e.g. "user/repo").
"""
import os
import time
import requests

API_ROOT = "https://api.github.com"


def _headers():
    token = os.environ["GITHUB_TOKEN"]
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}


def publish_release_asset(file_path: str) -> str:
    repo = os.environ["GITHUB_REPOSITORY"]  # "owner/repo"
    tag = f"short-{int(time.time())}"

    r = requests.post(
        f"{API_ROOT}/repos/{repo}/releases",
        headers=_headers(),
        json={"tag_name": tag, "name": tag, "draft": False, "prerelease": False},
        timeout=30,
    )
    r.raise_for_status()
    release = r.json()
    upload_url = release["upload_url"].split("{")[0]

    with open(file_path, "rb") as f:
        data = f.read()
    r2 = requests.post(
        upload_url,
        headers={**_headers(), "Content-Type": "video/mp4"},
        params={"name": os.path.basename(file_path)},
        data=data,
        timeout=120,
    )
    r2.raise_for_status()
    asset = r2.json()
    return asset["browser_download_url"]
