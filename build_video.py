"""
Assembles the final vertical short using ffmpeg only (no moviepy — lighter,
faster, and ffmpeg ships preinstalled on GitHub Actions ubuntu runners).

Pipeline:
1. Each stock clip is trimmed to its line's narration duration, scaled/cropped
   to 1080x1920, and given a slow zoom (Ken Burns effect) so nothing sits on
   a static frame — constant subtle motion is one of the biggest retention
   levers on short-form video.
2. Segments are concatenated into a silent video.
3. Word-by-word "karaoke" captions (captions.py) are burned on top via
   ffmpeg's subtitles filter, synced to the narration's real word timings.
4. Narration audio is concatenated and mixed with background music (ducked
   underneath), then muxed onto the captioned video.
"""
import glob
import os
import random
import subprocess

from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS
from captions import build_ass


def build_segment(clip_path, duration, out_path):
    """Trim + scale/crop + subtle zoom (no captions here — captions are burned
    globally afterward so they can span line boundaries cleanly)."""
    frames = max(1, int(duration * FPS))
    zoom_expr = "zoom+0.0015"
    vf = (
        f"scale={VIDEO_WIDTH*2}:{VIDEO_HEIGHT*2}:force_original_aspect_ratio=increase,"
        f"crop={VIDEO_WIDTH*2}:{VIDEO_HEIGHT*2},"
        f"zoompan=z='{zoom_expr}':d={frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}"
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


def burn_captions(video_path, ass_path, out_path):
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"subtitles={ass_path}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        out_path,
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
    clips: list of paths from fetch_clips.fetch_clips_for_script
    tts_lines: list of dicts from tts.synthesize_lines:
               {text, audio, duration, words: [{word, start, duration}]}
    """
    os.makedirs(workdir, exist_ok=True)

    segment_paths = []
    for i, line in enumerate(tts_lines):
        clip = clips[i % len(clips)]
        seg_out = os.path.join(workdir, f"seg_{i}.mp4")
        build_segment(clip, line["duration"], seg_out)
        segment_paths.append(seg_out)

    silent_video = os.path.join(workdir, "silent.mp4")
    concat_segments(segment_paths, silent_video)

    ass_path = build_ass(tts_lines, out_path=os.path.join(workdir, "captions.ass"))
    captioned_video = os.path.join(workdir, "captioned.mp4")
    burn_captions(silent_video, ass_path, captioned_video)

    narration_full = os.path.join(workdir, "narration_full.mp3")
    concat_audio([l["audio"] for l in tts_lines], narration_full)

    mux_with_audio(captioned_video, narration_full, out_path)
    return out_path
