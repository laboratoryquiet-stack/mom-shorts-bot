"""
Fetches free stock video clips from Pexels (https://www.pexels.com/api/).
Sign up free at pexels.com/api -> get an API key -> set env var PEXELS_API_KEY.
"""
import os
import random
import requests

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
SEARCH_URL = "https://api.pexels.com/videos/search"


def search_and_download(keyword: str, out_path: str, min_duration=4):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": keyword, "orientation": "portrait", "per_page": 10}
    resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    videos = resp.json().get("videos", [])
    # filter to vertical, reasonably short clips
    candidates = [v for v in videos if v["duration"] >= min_duration]
    if not candidates:
        candidates = videos
    if not candidates:
        raise RuntimeError(f"No Pexels results for keyword: {keyword}")

    video = random.choice(candidates)
    # pick the highest-res vertical file available
    files = sorted(video["video_files"], key=lambda f: f.get("height", 0), reverse=True)
    vertical_files = [f for f in files if f.get("height", 0) >= f.get("width", 1)]
    chosen = (vertical_files or files)[0]

    r = requests.get(chosen["link"], stream=True, timeout=60)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return out_path


def fetch_clips_for_script(keywords, workdir="tmp", count=5):
    os.makedirs(workdir, exist_ok=True)
    chosen_keywords = random.sample(keywords, k=min(count, len(keywords)))
    paths = []
    for i, kw in enumerate(chosen_keywords):
        out_path = os.path.join(workdir, f"clip_{i}.mp4")
        search_and_download(kw, out_path)
        paths.append(out_path)
    return paths


if __name__ == "__main__":
    from config import VIDEO_KEYWORDS
    print(fetch_clips_for_script(VIDEO_KEYWORDS, count=2))
