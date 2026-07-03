"""
Posts ONE Reel to Instagram only. Fully independent of YouTube — run this on
its own schedule/cron once Instagram is set up, without needing YouTube to
be configured at all.

Usage: python post_instagram.py
Requires env vars: PEXELS_API_KEY, IG_ACCESS_TOKEN, IG_USER_ID, GITHUB_TOKEN
(for the free video-hosting-via-Release trick Instagram's API requires).
"""
from pipeline_core import build_video_asset
from host_video import publish_release_asset
from upload_instagram import publish_reel
from affiliate import instagram_caption_addon
from log_post import log_post


def main():
    asset = build_video_asset()

    caption = asset["base_text"] + instagram_caption_addon()

    public_url = publish_release_asset(asset["video_path"])
    print("Hosted at:", public_url)

    ig_media_id = publish_reel(public_url, caption=caption)
    print(f"✅ Posted to Instagram: media id {ig_media_id}")

    log_post(theme=asset["theme"], opener=asset["opener"], youtube_id=None, ig_media_id=ig_media_id)


if __name__ == "__main__":
    main()
