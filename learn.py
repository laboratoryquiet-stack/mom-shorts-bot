"""
Run daily (separate cron job) to close the feedback loop:
1. Look at posts from the last ~2 weeks that are old enough to have stable
   stats (48h+) and haven't been scored yet.
2. Pull real view/like/comment/save data for each.
3. Update a running performance score per theme and per opener line, using
   an exponential moving average so recent performance matters most but one
   lucky/unlucky post can't swing things wildly.
4. generate_script.py reads these scores to bias future picks toward what's
   actually working (see choose_theme() and weighted_pick()).

This makes the system adapt to ITS OWN results over time. It cannot
guarantee views or "beat the algorithm" — no one outside the platforms
knows the full ranking logic — but it does mean the account stops repeating
whatever isn't working and leans into whatever is.
"""
import datetime
import json
import os

from analytics import get_youtube_stats, get_instagram_stats, engagement_score

STATE_PATH = "state.json"
MIN_AGE_HOURS = 48
EMA_ALPHA = 0.3  # weight given to each new data point vs. history


def load_state():
    if not os.path.exists(STATE_PATH):
        # First-ever run before any post has been logged - nothing to score
        # yet. Returning an empty-but-valid state lets main() print its
        # normal "nothing due yet" message instead of crashing the cron job.
        return {"post_log": [], "theme_scores": {}, "opener_scores": {}}
    with open(STATE_PATH) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def update_score(score_dict, key, new_value):
    if key not in score_dict:
        score_dict[key] = new_value
    else:
        score_dict[key] = (1 - EMA_ALPHA) * score_dict[key] + EMA_ALPHA * new_value


def main():
    state = load_state()
    post_log = state.setdefault("post_log", [])
    theme_scores = state.setdefault("theme_scores", {})
    opener_scores = state.setdefault("opener_scores", {})

    now = datetime.datetime.now(datetime.timezone.utc)
    due_entries = []
    for entry in post_log:
        if entry.get("scored"):
            continue
        posted_at = datetime.datetime.fromisoformat(entry["posted_at"])
        if (now - posted_at).total_seconds() >= MIN_AGE_HOURS * 3600:
            due_entries.append(entry)

    if not due_entries:
        print("No posts old enough to score yet.")
        return

    yt_ids = [e["youtube_id"] for e in due_entries if e.get("youtube_id")]
    ig_ids = [e["ig_media_id"] for e in due_entries if e.get("ig_media_id")]

    yt_stats = get_youtube_stats(yt_ids)
    ig_stats = get_instagram_stats(ig_ids)

    for entry in due_entries:
        scores = []
        if entry.get("youtube_id") in yt_stats:
            scores.append(engagement_score(yt_stats[entry["youtube_id"]]))
        if entry.get("ig_media_id") in ig_stats:
            scores.append(engagement_score(ig_stats[entry["ig_media_id"]]))
        if not scores:
            continue  # stats not available yet (video processing, API hiccup) — try again next run

        avg_score = sum(scores) / len(scores)
        update_score(theme_scores, entry["theme"], avg_score)
        if entry.get("opener"):
            update_score(opener_scores, entry["opener"], avg_score)
        entry["scored"] = True
        entry["final_score"] = avg_score
        print(f"Scored post {entry['post_number']} ({entry['theme']}): {avg_score:.4f}")

    # keep the log from growing forever
    if len(post_log) > 500:
        state["post_log"] = post_log[-500:]

    save_state(state)
    print("Theme scores:", theme_scores)


if __name__ == "__main__":
    main()
