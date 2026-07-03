"""
Free text-to-speech via edge-tts (Microsoft Edge's neural voices, no API key).
Generates one mp3 per script line AND captures per-word timing (via edge-tts's
WordBoundary events) so build_video.py can render word-by-word "karaoke"
captions synced to the narration — the single biggest lever for retention on
Shorts/Reels, versus static boxed captions.
"""
import asyncio
import json
import os
import subprocess

import edge_tts

VOICE = "en-US-JennyNeural"  # warm, natural female voice; swap to en-US-AriaNeural etc. if desired


def get_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


async def _synth_with_words(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, VOICE, rate="-5%")
    words = []
    with open(out_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "word": chunk["text"],
                    "start": chunk["offset"] / 10_000_000,      # 100ns units -> seconds
                    "duration": chunk["duration"] / 10_000_000,
                })
    return words


def synthesize_lines(lines, workdir="tmp"):
    """Returns a list of dicts: {text, audio, duration, words: [{word,start,duration}]}."""
    os.makedirs(workdir, exist_ok=True)
    clips = []
    for i, line in enumerate(lines):
        out_path = os.path.join(workdir, f"line_{i}.mp3")
        words = asyncio.run(_synth_with_words(line, out_path))
        duration = get_duration(out_path)
        clips.append({"text": line, "audio": out_path, "duration": duration, "words": words})
    return clips


if __name__ == "__main__":
    demo = synthesize_lines(["This is a test line.", "Second line here."])
    print(demo)
