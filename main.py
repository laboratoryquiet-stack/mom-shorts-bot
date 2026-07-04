"""
Combined mode: ONE video posted to BOTH YouTube and Instagram (same content
on both platforms). If you'd rather run them independently — e.g. YouTube
only, or on different schedules — use post_youtube.py / post_instagram.py
instead. This script is just the "same content everywhere" convenience option.
"""
import os

from pipeline_core import build_video_asset
from host_video import publish_release_asset
from upload_youtube import upload_short, post_affiliate_comment
from upload_instagram import publish_reel
from affiliate import youtube_description_addon, instagram_caption_addon, amazon_link_for_theme, DISCLOSURE
from log_post import log_post


def main():
    asset = build_video_asset()

    title = f"{asset['display_theme']} for Working Moms \U0001F49B #Shorts {asset['title_tags']}"
    youtube_description = asset["base_text"] + youtube_description_addon(asset["theme"])
    instagram_caption = asset["base_text"] + instagram_caption_addon()
    tags = ["working mom", "motivation", "affirmations", "mom life", "shorts",
            asset["display_theme"].lower()]

    youtube_id = upload_short(asset["video_path"], title=title, description=youtube_description, tags=tags)
    print(f"✅ Posted to YouTube: https://youtube.com/shorts/{youtube_id}")

    affiliate_link = amazon_link_for_theme(asset["theme"])
    if affiliate_link:
        try:
            post_affiliate_comment(youtube_id, f"Something that might help: {affiliate_link}\n{DISCLOSURE}")
        except Exception as e:
            print("Affiliate comment post failed (non-fatal):", e)

    ig_media_id = None
    if os.environ.get("IG_ACCESS_TOKEN") and os.environ.get("IG_USER_ID"):
        try:
            public_url = publish_release_asset(asset["video_path"])
            print("Hosted at:", public_url)
            ig_media_id = publish_reel(public_url, caption=instagram_caption)
            print(f"✅ Posted to Instagram: media id {ig_media_id}")
        except Exception as e:
            print("Instagram posting failed (non-fatal, YouTube post still succeeded):", e)
    else:
        print("Instagram not configured (IG_ACCESS_TOKEN/IG_USER_ID missing) — skipping, YouTube-only post.")

    log_post(theme=asset["theme"], opener=asset["opener"], youtube_id=youtube_id, ig_media_id=ig_media_id)


if __name__ == "__main__":
    main()
