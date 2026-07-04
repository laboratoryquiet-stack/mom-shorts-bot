"""
Shared pipeline core: topic -> script -> TTS -> stock clips -> stitched
video. Used by both post_youtube.py and post_instagram.py so the two
platforms don't duplicate this logic, but each platform script runs fully
independently — one can run/fail/be disabled without affecting the other.
"""
import os
import shutil

from config import VIDEO_KEYWORDS, build_hashtags, top_title_hashtags
from generate_script import generate
from tts import synthesize_lines
from fetch_clips import fetch_clips_for_script
from build_video import build_final_video


def build_video_asset(workdir="tmp", out_path="output.mp4"):
    """Runs the full free content pipeline and returns everything the
    per-platform upload scripts need."""
    if os.path.exists(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir, exist_ok=True)

    script = generate()
    lines = script["lines"]
    theme = script["theme"]
    opener = script.get("opener")
    display_theme = theme.replace("_", " ").title()

    print(f"Theme: {display_theme}")
    print("Lines:", lines)

    tts_lines = synthesize_lines(lines)
    clips = fetch_clips_for_script(VIDEO_KEYWORDS, count=len(lines))

    video_path = build_final_video(clips, tts_lines, workdir=workdir, out_path=out_path)
    print("Built video:", video_path)

    hashtags = build_hashtags(theme)
    title_tags = top_title_hashtags(theme)
    base_text = f"{' '.join(lines)}\n\n{hashtags}"

    return {
        "video_path": video_path,
        "theme": theme,
        "opener": opener,
        "display_theme": display_theme,
        "lines": lines,
        "hashtags": hashtags,
        "title_tags": title_tags,
        "base_text": base_text,
    }
