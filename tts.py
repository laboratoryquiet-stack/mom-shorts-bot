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

# Distinct voices by content register, not one voice/pace for everything:
# - AFFIRMATION_VOICE: brighter, a touch more energetic — motivational content
# - SUPPORT_VOICE: warmer, calmer, more mature — reads like an older, wise,
#   comforting presence. Picked from Microsoft's documented voice
#   characteristics (Michelle is described as warm/mature/calm) — I can't
#   play audio in this environment to confirm by ear, so if it's not quite
#   right once you actually hear it, swap the name below; nothing else
#   needs to change.
# - HUMOR_VOICE: same base voice as affirmation but noticeably faster/
#   brighter, matching a punchline's pacing rather than a mantra's.
#
# Pacing note: rates were tightened from the original -5%/-13% because
# current (2026) Shorts retention thresholds reportedly reward shorter,
# tighter videos over slow contemplative pacing — a slow reading style
# increases total runtime past the point where average-view-duration %
# clears the algorithm's push-wider gate. If your own analytics data
# suggests otherwise for your audience, these are the first values worth
# A/B testing — change ONE profile at a time and compare in YouTube
# Studio's retention curve before changing another.
VOICE_PROFILES = {
    "affirmation": {
        "voice": os.environ.get("AFFIRMATION_VOICE", "en-US-JennyNeural"),
        "rate": "-2%",
        "pitch": "+0Hz",
    },
    "support": {
        "voice": os.environ.get("SUPPORT_VOICE", "en-US-MichelleNeural"),
        "rate": "-8%",
        "pitch": "-2Hz",
    },
    "humor": {
        "voice": os.environ.get("HUMOR_VOICE", os.environ.get("AFFIRMATION_VOICE", "en-US-JennyNeural")),
        "rate": "+8%",
        "pitch": "+2Hz",
    },
}

DEFAULT_PROFILE = "affirmation"  # used for tips/spotlight/myth_bust/this_or_that/anything not explicitly mapped above


def get_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


async def _synth_with_words(text: str, out_path: str, voice: str, rate: str, pitch: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
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


def synthesize_lines(lines, workdir="tmp", content_type=None):
    """Returns a list of dicts: {text, audio, duration, words: [{word,start,duration}]}.
    content_type picks the voice profile ("affirmation" or "support") — anything else falls back to the default (affirmation) profile."""
    profile = VOICE_PROFILES.get(content_type, VOICE_PROFILES[DEFAULT_PROFILE])
    os.makedirs(workdir, exist_ok=True)
    clips = []
    for i, line in enumerate(lines):
        out_path = os.path.join(workdir, f"line_{i}.mp3")
        words = asyncio.run(_synth_with_words(
            line,
            out_path,
            profile["voice"],
            profile["rate"],
            profile["pitch"]
        ))
        duration = get_duration(out_path)
        clips.append({"text": line, "audio": out_path, "duration": duration, "words": words})
    return clips


if __name__ == "__main__":
    demo = synthesize_lines(["This is a test line.", "Second line here."])
    print(demo)
