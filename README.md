# Working Moms Motivation — Automated Shorts Bot

Fully automated pipeline: generates an affirmation script, narrates it with
free TTS, pulls free stock clips, stitches a vertical short with captions +
background music, and publishes to YouTube Shorts + Instagram Reels — 3×/day,

## Important fix: the video-build bug that likely caused "nothing posts"
An earlier version of `build_video.py` had a real bug in the zoom effect (`zoompan` filter) that could make a 5-second clip balloon into ~12 minutes of output, hanging or timing out the pipeline before it ever reached the upload step. This is fixed and verified with an actual ffmpeg render (confirmed: correct frame count, correct duration, ~4.5s render time for a 5-second segment). If you were on an older copy of this repo, replace `build_video.py` with this version.

## Three ways to run this now
- **`python post_youtube.py`** — posts to YouTube only. Fully independent of Instagram; use this if Instagram isn't set up yet.
- **`python post_instagram.py`** — posts to Instagram only. Fully independent of YouTube.
- **`python main.py`** — posts the SAME video to both platforms in one run (convenience option if you want identical content everywhere).

Note: `post_youtube.py` and `post_instagram.py` each generate their own content independently, so if you run both, they may post different scripts/themes on a given day (each pulls its own turn from the rotation). If you specifically want identical content on both platforms every time, use `main.py` instead.

The GitHub Actions workflow now runs `post_youtube.py` on the 3x/day schedule (since that's what's set up), and lets you manually trigger `post_instagram.py` or both from the Actions tab (use the "Run workflow" button and pick a target from the dropdown) once Instagram is ready.

## Stronger tags for discoverability
Hashtags/tags now combine broad discovery tags (`config.HASHTAGS`) with theme-specific tags (`config.THEME_HASHTAGS`) — broad tags get you into general feeds, specific tags put you in front of people actively searching that exact topic, who tend to be higher-intent viewers.

$0 running cost, hosted on GitHub Actions' free tier.

## What's actually free vs. what needs a one-time signup

Everything below is free, but a few require creating your own accounts/keys
(this is unavoidable — no one else can authorize posting to *your* channel):

| Step | Cost | What you do |
|---|---|---|
| Pexels stock video | Free | Sign up at pexels.com/api, get an API key |
| edge-tts narration | Free, no signup | Nothing needed |
| Background music | Free | Download ~15-20 tracks from YouTube Audio Library or Pixabay Music, drop mp3s in `music/` |
| ffmpeg stitching | Free | Runs on the GitHub Actions runner (preinstalled) |
| GitHub Actions hosting | Free (2,000 min/month tier) | Push this repo to GitHub |
| YouTube Data API | Free (quota-limited, 3/day is fine) | Google Cloud project + OAuth (one-time browser login) |
| Instagram Graph API | Free | Convert IG to Business account, link a Facebook Page, create a Meta developer app |

## Setup steps

### 1. Create the actual channel/page
- Create your YouTube channel and Instagram account (this part is you — I can't create accounts on your behalf).
- Convert the Instagram account to **Professional (Business or Creator)**.
- Create a Facebook Page and link it to that Instagram account (required by Instagram's API).

### 2. Get a Pexels API key
- pexels.com/api → sign up free → copy your API key.

### 3. Set up YouTube upload auth
- Go to console.cloud.google.com → new project → enable **YouTube Data API v3**.
- Create OAuth Client ID → Application type: **Desktop app** → download as `client_secret.json`, place it in this folder.
- Run locally once:
  ```
  pip install -r requirements.txt
  python upload_youtube.py --auth
  ```
  This opens a browser for you to log into the YouTube account, then creates `token.json`.

### 4. Set up Instagram Graph API
- developers.facebook.com → create an App (type: Business).
- Add the "Instagram Graph API" product.
- Generate a long-lived **Page Access Token** with `instagram_content_publish` permission, with your IG account added as a tester (development mode — no App Review needed for posting to your own account).
- Find your IG Business Account ID via the Graph API Explorer: `GET /me/accounts` → find your page → `instagram_business_account.id`.

### 5. Push this repo to GitHub and add secrets
Repo → Settings → Secrets and variables → Actions → New repository secret:

| Secret name | Value |
|---|---|
| `PEXELS_API_KEY` | your Pexels key |
| `YT_CLIENT_SECRET` | full contents of `client_secret.json` |
| `YT_TOKEN` | full contents of `token.json` |
| `IG_ACCESS_TOKEN` | your long-lived Page Access Token |
| `IG_USER_ID` | your IG Business Account ID |

`GITHUB_TOKEN` is provided automatically by Actions — nothing to add.

### 6. Add music (font is handled automatically now)
- Drop 15-20 royalty-free mp3s into `music/`.
- Captions now use word-by-word "karaoke" highlighting (synced to the real narration timing) rendered with DejaVu Sans, which the workflow installs automatically — no font file needed anymore.

### 7. Review the real-women spotlight bank
Every 5th post uses a fact-checked "real story" instead of the affirmation template (`config.SPOTLIGHT_STORIES`). Unlike the affirmation banks, this is **not** auto-generated — each entry was manually verified against sources before being added. If you want to add more names, verify the facts yourself first (or ask me to) rather than letting the bot improvise claims about real people. No images/video of the actual people are shown — just the same generic stock b-roll — to avoid likeness/rights issues.

### 8. Add the Instagram insights permission (needed for the learning loop)
When generating your Instagram access token, also grant `instagram_manage_insights` alongside `instagram_content_publish` — without it, `learn.py` can't read Instagram engagement data.

### 10. Set up affiliate monetization (optional, from day one)
- **Amazon Associates**: sign up free at affiliate-program.amazon.com. Once approved, set `AMAZON_ASSOCIATE_TAG` as a GitHub secret. YouTube descriptions get a real per-theme clickable link automatically, with the required FTC disclosure. Amazon requires 3 qualifying sales within 180 days of joining or the account can be closed — not guaranteed passive income from day one.
- **LTK (LikeToKnow.it)**: free, purpose-built for lifestyle/mom creators, often converts better than a generic Amazon link since it's a personal curated shop. Join at creator.shopltk.com, set `LTK_PROFILE_HANDLE` as a GitHub secret.
- **Instagram** captions still can't hold clickable links (a platform limitation) — keep one stable Amazon List or LTK profile link in your bio and point captions there ("shopping list in bio").
- **YouTube affiliate comment**: after each upload, the bot also posts a comment containing the affiliate link for extra visibility. One honest caveat — YouTube's API doesn't have a documented way to actually *pin* a comment (that's Studio-UI only), so this posts the comment but doesn't guarantee it's pinned; you'd tap "pin" manually in Studio if you want that.

### 11. Broaden your YouTube token scope + add Instagram comment permission (needed for the audience-listening feature)
The bot now reads comments on your own posts to figure out what your actual audience is engaging with (not a copied trend — your real audience):
- YouTube: rerun `python upload_youtube.py --auth` once — `upload_youtube.py`'s scopes now include `youtube.force-ssl` (comment reading) alongside the original upload scope, so this reissues `token.json` covering both. Re-copy the new `token.json` contents into the `YT_TOKEN` GitHub secret.
- Instagram: when generating your access token, also grant `instagram_manage_comments` alongside `instagram_content_publish` and `instagram_manage_insights`.

### 12. Turn it on
The workflow in `.github/workflows/publish.yml` runs automatically 3×/day
once secrets are set. Trigger a test run manually from the Actions tab first
("Run workflow") before trusting the cron schedule.

## The feedback loop — it learns from its own performance
`learn.py` runs daily and does the following:
1. Pulls real view/like/comment/save data for posts old enough to have stable stats (48h+), via YouTube's `videos.list` and Instagram's media insights endpoint
2. Scores each post by **engagement actions per view** (likes + comments + shares + saves, weighted, divided by views) — not raw view count, so it doesn't just chase whichever post happened to post at a lucky hour
3. Updates a running score per **theme** and per **hook line**, using an exponential moving average so recent results matter most without one outlier post swinging everything
4. `generate_script.py` then picks future themes/hooks using **epsilon-greedy selection**: most of the time it favors what's scored well, but it still explores other options ~30-40% of the time so it doesn't get stuck exploiting one early lucky winner while ignoring everything else

Meta's metric names on the insights endpoint do shift between API versions occasionally — if Instagram scoring silently stops working, check the current field names in Meta's insights docs before assuming the code broke.

**Be realistic about what this can and can't do.** This makes the system genuinely adaptive — it will stop repeating whatever isn't landing and lean into whatever is, based on real data, not guesses. It cannot guarantee growth, override the platforms' own ranking algorithms (which no one outside Meta/Google fully knows), or replace things that content-repetition can't fix — like the trending-audio and human-authenticity limitations covered above.

## Content-strategy features now built in
- **Sharper, specific hooks** instead of generic affirmations (config.py `OPENERS`)
- **Word-by-word karaoke captions**, synced to real narration timing — the single biggest retention lever on Shorts/Reels
- **Subtle Ken Burns zoom** on every clip instead of static shots
- **Consistent persona tagline** (`config.TAGLINE`) appended to every video — recognition through repetition
- **Calendar-aware theming** — leans into relevant themes during real-world months (back-to-school, Mother's Day, etc.)
- **Real-time trend nudge** — pulls today's top discussion titles from public working-mom subreddits (free, no API key) and biases theme selection toward what's actually being talked about right now, gracefully skipped if unavailable
- **Fact-checked real-women spotlight** every 5th post

## Content mix (as of the latest update)
Every ~15 posts now breaks down roughly as: 3 real-women spotlights, 5 practical-tips lists, 7 affirmation-template posts — biased further by real audience comments (highest priority), then general trend signal, then learned performance scores, then calendar relevance, then plain rotation.

**A note on positioning, not just code**: this account is fully automated — no shame in that, but I'd genuinely recommend presenting it as a "daily support resource for working moms" rather than implying it's one person's real personal diary. Audiences respond very well to useful, honest tools; discovering a "personal" account wasn't real tends to do real damage to trust. Worth deciding deliberately rather than by default.

## Known limitations to know about up front
- **YouTube quota**: default 10,000 units/day, uploads cost 1,600 each — 3/day (4,800) is safe, but don't push past ~6/day without requesting a quota increase (still free, just needs a Google form).
- **Instagram**: the Graph API requires the video to be at a public URL, not a direct upload — this repo works around that by briefly hosting each video as a GitHub Release asset.
- **Content originality**: `generate_script.py` now uses a "shuffle bag" per content pool (no repeats until the whole bank is exhausted) plus full-script duplicate detection, so repeats are spaced out far more than plain random choice. It's still a finite template bank, though — for permanent freshness you'd eventually want to expand `config.py`'s AFFIRMATIONS/OPENERS/CLOSERS lists periodically.
- **Instagram token refresh is now automated**: `refresh_instagram_token.py` runs weekly via the workflow and rewrites the `IG_ACCESS_TOKEN` GitHub secret before it expires. This needs two extra secrets: `META_APP_ID`, `META_APP_SECRET` (found in your Meta developer app's Settings → Basic), and a GitHub **Personal Access Token** (classic, "repo" scope — create at github.com/settings/tokens) saved as `GH_PAT`. Without `GH_PAT` you'd be back to refreshing the IG token by hand every ~60 days.
- **YouTube token expiry (the one real manual-interference risk)**: while your Google Cloud OAuth app is in **Testing** mode, Google expires the refresh token after 7 days — you'd have to rerun `python upload_youtube.py --auth` weekly. To make this truly hands-off, go to **Google Cloud Console → APIs & Services → OAuth consent screen → Publishing status → Publish App**. For a single personal-use app like this with only the `youtube.upload` scope, publishing usually does not require Google's manual verification process (verification is mainly triggered by *sensitive/restricted* scopes at higher user counts) — but Google's rules do shift occasionally, so confirm current requirements at the time you do this.
- **Monetization is not guaranteed** — see the note in our conversation: YouTube's policies restrict monetization for repetitious/mass-produced content, so treat this as an engagement/audience-building tool first, not a guaranteed income source.

## Automated token refresh — what's really automatable, honestly
- **Instagram**: fully automated already. `refresh_instagram_token.py` runs weekly and rewrites the `IG_ACCESS_TOKEN` secret. Needs `META_APP_ID`, `META_APP_SECRET`, and `GH_PAT` (a GitHub Personal Access Token, classic, "repo" scope, from github.com/settings/tokens — the default `GITHUB_TOKEN` Actions provides can't modify secrets).
- **YouTube**: also now automated for everything *except* the very first login. `upload_youtube.py` refreshes its own access token silently on every run using the stored refresh_token — no human needed for that. `refresh_youtube_token.py` additionally runs weekly to force a refresh and sync the result back into the `YT_TOKEN` secret, so it can never drift stale.
- **What genuinely can't be automated, by design, not by gap**: the first login for a set of scopes, and any time the scopes themselves change — both require a human clicking "Allow" in a browser once. This isn't a missing feature; a script that could silently mint its own first OAuth token without a human would be a real security hole. If either script above hits this case, it fails with a clear error message telling you to rerun `python upload_youtube.py --auth`, rather than pretending it succeeded.
- **The one manual step actually worth doing to minimize future interruptions**: publish your Google Cloud OAuth app out of "Testing" mode (APIs & Services -> OAuth consent screen -> Publishing status). While it's in Testing, Google force-expires the refresh token every 7 days no matter what — that's the most common reason you'd see a human-required error.
