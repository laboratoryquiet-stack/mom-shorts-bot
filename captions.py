"""
Builds a .ass subtitle file with word-by-word "karaoke" highlighting —
each word lights up as it's spoken, synced via edge-tts's word timings.
This is burned onto the video with ffmpeg's subtitles filter in build_video.py.

Style: bold white base text, words light up in yellow as they're spoken
(the standard CapCut/TikTok-style caption look), centered, large, with a
heavy outline for legibility over any background clip.
"""
from config import VIDEO_WIDTH, VIDEO_HEIGHT

# ASS colors are &HAABBGGRR (alpha, blue, green, red)
HIGHLIGHT_COLOR = "&H0000FFFF"  # yellow (already-spoken words)
BASE_COLOR = "&H00FFFFFF"       # white (not-yet-spoken words)
OUTLINE_COLOR = "&H00000000"    # black outline
FONT_NAME = "DejaVu Sans"       # preinstalled on Ubuntu GitHub Actions runners

HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {VIDEO_WIDTH}
PlayResY: {VIDEO_HEIGHT}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,{FONT_NAME},76,{HIGHLIGHT_COLOR},{BASE_COLOR},{OUTLINE_COLOR},&H64000000,1,0,0,0,100,100,2,0,1,5,2,5,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def format_ass_time(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:01d}:{m:02d}:{s:05.2f}"


def build_ass(tts_lines, out_path="tmp/captions.ass"):
    """
    tts_lines: list of dicts from tts.synthesize_lines, each with
    'duration' and 'words': [{word, start, duration}] (start/duration are
    relative to that line's own audio, in seconds).
    Produces one Dialogue event per line, with \\kf karaoke tags per word so
    the whole line is visible and words highlight progressively as spoken.
    """
    events = []
    cumulative = 0.0
    for line in tts_lines:
        start = cumulative
        end = cumulative + line["duration"]
        words = line["words"] or [{"word": line["text"], "start": 0, "duration": line["duration"]}]

        parts = []
        for w in words:
            dur_cs = max(1, round(w["duration"] * 100))  # centiseconds for \kf
            safe_word = w["word"].replace("{", "").replace("}", "")
            parts.append(f"{{\\kf{dur_cs}}}{safe_word} ")
        text = "".join(parts).strip()

        events.append(
            f"Dialogue: 0,{format_ass_time(start)},{format_ass_time(end)},Karaoke,,0,0,0,,{text}"
        )
        cumulative = end

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(events) + "\n")

    return out_path
