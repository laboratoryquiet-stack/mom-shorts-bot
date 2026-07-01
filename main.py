"""
Full pipeline, run 3x/day by the GitHub Actions cron workflow:
topic -> script -> TTS -> stock clips -> stitched video -> host on GitHub
-> publish to YouTube Shorts + Instagram Reels.
"""
import os
import shutil

from config import VIDEO_KEYWORDS, HASHTAGS
from generate_script import generate
from tts import synthesize_lines
from fetch_clips import fetch_clips_for_script
from build_video import build_final_video
from host_video import publish_release_asset
from upload_youtube import upload_short
from upload_instagram import publish_reel


def main():
    if os.path.exists("tmp"):
        shutil.rmtree("tmp")
    os.makedirs("tmp", exist_ok=True)

    script = generate()
    lines = script["lines"]
    theme = script["theme"].replace("_", " ").title()

    print(f"Theme: {theme}")
    print("Lines:", lines)

    tts_lines = synthesize_lines(lines)
    clips = fetch_clips_for_script(VIDEO_KEYWORDS, count=len(lines))

    out_path = build_final_video(clips, tts_lines, out_path="output.mp4")
    print("Built video:", out_path)

    title = f"{theme} for Working Moms 💛 #Shorts"
    description = f"{' '.join(lines)}\n\n{HASHTAGS}"

    # YouTube: direct file upload
    upload_short(out_path, title=title, description=description,
                 tags=["working mom", "motivation", "affirmations"])

    # Instagram: needs a public URL, so host it on a GitHub Release first
    public_url = publish_release_asset(out_path)
    print("Hosted at:", public_url)
    publish_reel(public_url, caption=f"{description}")


if __name__ == "__main__":
    main()
