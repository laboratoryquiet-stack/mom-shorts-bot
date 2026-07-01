"""
Free text-to-speech via edge-tts (Microsoft Edge's neural voices, no API key).
Generates one mp3 per script line and returns each clip's duration via ffprobe,
so build_video.py can sync captions/visuals precisely.
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


async def _synth(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, VOICE, rate="-5%")
    await communicate.save(out_path)


def synthesize_lines(lines, workdir="tmp"):
    os.makedirs(workdir, exist_ok=True)
    clips = []
    for i, line in enumerate(lines):
        out_path = os.path.join(workdir, f"line_{i}.mp3")
        asyncio.run(_synth(line, out_path))
        duration = get_duration(out_path)
        clips.append({"text": line, "audio": out_path, "duration": duration})
    return clips


if __name__ == "__main__":
    demo = synthesize_lines(["This is a test line.", "Second line here."])
    print(demo)
