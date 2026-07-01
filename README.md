# Working Moms Motivation — Automated Shorts Bot

Fully automated pipeline: generates an affirmation script, narrates it with
free TTS, pulls free stock clips, stitches a vertical short with captions +
background music, and publishes to YouTube Shorts + Instagram Reels — 3×/day,
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

### 6. Add music + a caption font
- Drop 15-20 royalty-free mp3s into `music/`.
- Drop a free bold font (e.g. Montserrat-Bold, Google Fonts) into `assets/caption_font.ttf`.

### 7. Turn it on
The workflow in `.github/workflows/publish.yml` runs automatically 3×/day
once secrets are set. Trigger a test run manually from the Actions tab first
("Run workflow") before trusting the cron schedule.

## Known limitations to know about up front
- **YouTube quota**: default 10,000 units/day, uploads cost 1,600 each — 3/day (4,800) is safe, but don't push past ~6/day without requesting a quota increase (still free, just needs a Google form).
- **Instagram**: the Graph API requires the video to be at a public URL, not a direct upload — this repo works around that by briefly hosting each video as a GitHub Release asset.
- **Content originality**: the script generator uses a template bank (not a paid AI), so lines will start repeating after a few months — easy to extend by adding more entries to `config.py`.
- **First IG token**: long-lived Page tokens expire after ~60 days and need manual refresh (Meta doesn't offer a fully automatic free refresh without extra OAuth infra).
