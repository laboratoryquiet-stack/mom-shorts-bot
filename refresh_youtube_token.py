"""
YouTube's refresh_token lets google-auth mint fresh access tokens
automatically forever (handled already inside upload_youtube.py's
get_authenticated_service() on every run) — that part needs no human.

This script is the belt-and-suspenders piece: it forces a refresh right now
and writes the resulting token.json back into the YT_TOKEN GitHub secret, so
even if Google ever rotates the underlying value, the stored secret never
drifts out of sync with what's actually valid.

This does NOT and cannot handle the cases that genuinely require a human:
- The very first login for a set of scopes
- A scopes change (like when force-ssl was added)
- Your OAuth app being stuck in "Testing" mode, which forces expiry every
  7 days regardless of refresh attempts — fix that once by publishing the
  app (Google Cloud Console -> OAuth consent screen -> Publishing status),
  and this script covers everything from there.
If a human-required case is hit, this fails with a clear message rather
than silently doing nothing.
"""
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from upload_youtube import SCOPES
from github_secrets import update_github_secret


def main():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    try:
        creds.refresh(Request())
    except RefreshError as e:
        raise RuntimeError(
            "YouTube token refresh failed — this needs a human to re-login "
            "(scopes changed, access revoked, or the OAuth app is still in "
            "'Testing' mode forcing 7-day expiry). Rerun "
            "`python upload_youtube.py --auth` locally and update the "
            f"YT_TOKEN secret manually. Original error: {e}"
        ) from e

    update_github_secret("YT_TOKEN", creds.to_json())
    print("YouTube token refreshed and GitHub secret synced.")


if __name__ == "__main__":
    main()
