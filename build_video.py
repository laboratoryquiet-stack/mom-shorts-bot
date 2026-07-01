"""
Assembles the final vertical short using ffmpeg only (no moviepy — lighter,
faster, and ffmpeg ships preinstalled on GitHub Actions ubuntu runners).

Steps per line: trim a stock clip to the narration's duration, scale/crop to
1080x1920, burn the caption text on top.
Then: concat all line-segments, mix narration audio with background music
(music ducked under narration), mux audio+video.
"""
import glob
import os
import random
import subprocess
import textwrap

from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS

FONT_PATH = "assets/caption_font.ttf"  # drop any free .ttf (e.g. Montserrat-Bold) here


def wrap_caption(text, width=22):
    return "\n".join(textwrap.wrap(text, width=width))


def build_segment(clip_path, duration, caption, out_path):
    wrapped = wrap_caption(caption).replace("'", "\u2019").replace(":", "\\:")
    drawtext = (
        f"drawtext=fontfile={FONT_PATH}:text='{wrapped}':"
        f"fontcolor=white:fontsize=64:line_spacing=14:"
        f"box=1:boxcolor=black@0.45:boxborderw=30:"
        f"x=(w-text_w)/2:y=(h-text_h)/2:shadowcolor=black:shadowx=2:shadowy=2"
    )
    vf = (
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},{drawtext}"
    )
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", clip_path,
        "-t", str(duration), "-vf", vf, "-an",
        "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p",
        out_path,
    ], check=True)


def concat_segments(segment_paths, out_path):
    list_file = "tmp/concat_list.txt"
    with open(list_file, "w") as f:
        for p in segment_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
        "-c", "copy", out_path,
    ], check=True)


def concat_audio(audio_paths, out_path):
    list_file = "tmp/audio_concat_list.txt"
    with open(list_file, "w") as f:
        for p in audio_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
        "-c", "copy", out_path,
    ], check=True)


def pick_music():
    tracks = glob.glob("music/*.mp3")
    if not tracks:
        return None
    return random.choice(tracks)


def mux_with_audio(video_path, narration_path, out_path):
    music = pick_music()
    if music:
        # duck music under narration, loop music to cover full length, mix down
        filter_complex = (
            "[1:a]volume=1.0[narr];"
            "[2:a]volume=0.12[music];"
            "[narr][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path, "-i", narration_path,
            "-stream_loop", "-1", "-i", music,
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-shortest", out_path,
        ], check=True)
    else:
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path, "-i", narration_path,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-shortest", out_path,
        ], check=True)


def build_final_video(clips, tts_lines, workdir="tmp", out_path="output.mp4"):
    """
    clips: list of paths from fetch_clips.fetch_clips_for_script (>= len(tts_lines) ideally)
    tts_lines: list of dicts from tts.synthesize_lines: {text, audio, duration}
    """
    os.makedirs(workdir, exist_ok=True)
    segment_paths = []
    for i, line in enumerate(tts_lines):
        clip = clips[i % len(clips)]
        seg_out = os.path.join(workdir, f"seg_{i}.mp4")
        build_segment(clip, line["duration"], line["text"], seg_out)
        segment_paths.append(seg_out)

    silent_video = os.path.join(workdir, "silent.mp4")
    concat_segments(segment_paths, silent_video)

    narration_full = os.path.join(workdir, "narration_full.mp3")
    concat_audio([l["audio"] for l in tts_lines], narration_full)

    mux_with_audio(silent_video, narration_full, out_path)
    return out_path
