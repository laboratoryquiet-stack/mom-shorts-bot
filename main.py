"""
Full pipeline, run 3x/day by the GitHub Actions cron workflow:
topic -> script -> TTS -> stock clips -> stitched video -> host on GitHub
-> publish to YouTube Shorts + Instagram Reels -> log metadata for learn.py.
"""
import datetime
import json
import os
import shutil

from config import VIDEO_KEYWORDS, HASHTAGS
from generate_script import generate
from tts import synthesize_lines
from fetch_clips import fetch_clips_for_script
from build_video import build_final_video
from host_video import publish_release_asset
from upload_youtube import upload_short, post_affiliate_comment
from upload_instagram import publish_reel
from affiliate import youtube_description_addon, instagram_caption_addon, amazon_link_for_theme, DISCLOSURE

STATE_PATH = "state.json"


def log_post(theme, opener, youtube_id, ig_media_id):
    state = {}
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            state = json.load(f)
    post_log = state.setdefault("post_log", [])
    post_log.append({
        "post_number": state.get("post_count", len(post_log) + 1),
        "theme": theme,
        "opener": opener,
        "youtube_id": youtube_id,
        "ig_media_id": ig_media_id,
        "posted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scored": False,
    })
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def main():
    if os.path.exists("tmp"):
        shutil.rmtree("tmp")
    os.makedirs("tmp", exist_ok=True)

    script = generate()
    lines = script["lines"]
    theme = script["theme"]
    opener = script.get("opener")
    display_theme = theme.replace("_", " ").title()

    print(f"Theme: {display_theme}")
    print("Lines:", lines)

    tts_lines = synthesize_lines(lines)
    clips = fetch_clips_for_script(VIDEO_KEYWORDS, count=len(lines))

    out_path = build_final_video(clips, tts_lines, out_path="output.mp4")
    print("Built video:", out_path)

    title = f"{display_theme} for Working Moms \U0001F49B #Shorts"
    base_description = f"{' '.join(lines)}\n\n{HASHTAGS}"
    youtube_description = base_description + youtube_description_addon(theme)
    instagram_caption = base_description + instagram_caption_addon()

    youtube_id = upload_short(out_path, title=title, description=youtube_description,
                               tags=["working mom", "motivation", "affirmations"])

    affiliate_link = amazon_link_for_theme(theme)
    if affiliate_link:
        try:
            post_affiliate_comment(youtube_id, f"Something that might help: {affiliate_link}\n{DISCLOSURE}")
        except Exception as e:
            print("Affiliate comment post failed (non-fatal):", e)

    public_url = publish_release_asset(out_path)
    print("Hosted at:", public_url)
    ig_media_id = publish_reel(public_url, caption=instagram_caption)

    log_post(theme, opener, youtube_id, ig_media_id)


if __name__ == "__main__":
    main()
