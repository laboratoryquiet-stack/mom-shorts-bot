"""
Posts ONE video to YouTube Shorts only. Fully independent of Instagram —
run this on its own schedule/cron even if Instagram isn't set up yet.

Usage: python post_youtube.py
Requires env vars: PEXELS_API_KEY (plus client_secret.json/token.json on disk,
and optionally AMAZON_ASSOCIATE_TAG / LTK_PROFILE_HANDLE for affiliate links).
"""
from pipeline_core import build_video_asset
from upload_youtube import upload_short, post_affiliate_comment
from affiliate import youtube_description_addon, amazon_link_for_theme, DISCLOSURE
from log_post import log_post


def main():
    asset = build_video_asset()

    title = f"{asset['display_theme']} for Working Moms \U0001F49B #Shorts {asset['title_tags']}"
    description = asset["base_text"] + youtube_description_addon(asset["theme"])

    # Tags: mix broad discovery tags with theme-specific ones (same logic as
    # hashtags, since YouTube's tag field works similarly for search/suggested).
    tags = [
        "working mom", "motivation", "affirmations", "mom life", "shorts",
        asset["display_theme"].lower(),
    ]

    youtube_id = upload_short(asset["video_path"], title=title, description=description, tags=tags)
    print(f"✅ Posted to YouTube: https://youtube.com/shorts/{youtube_id}")

    affiliate_link = amazon_link_for_theme(asset["theme"])
    if affiliate_link:
        try:
            post_affiliate_comment(youtube_id, f"Something that might help: {affiliate_link}\n{DISCLOSURE}")
        except Exception as e:
            print("Affiliate comment post failed (non-fatal):", e)

    log_post(theme=asset["theme"], opener=asset["opener"], youtube_id=youtube_id, ig_media_id=None)


if __name__ == "__main__":
    main()
