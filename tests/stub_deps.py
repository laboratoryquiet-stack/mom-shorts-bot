"""
Injects lightweight MagicMock stand-ins into sys.modules for third-party
SDKs that require network/real credentials (Google APIs, edge-tts, PyNaCl)
so the test suite can import and exercise pure business logic without
those packages installed or any network access.

In real CI, requirements.txt + requirements-dev.txt install the real
packages, so this stubbing is purely a local/offline testing convenience -
it never runs against the real network either way since we only test pure
logic, never actual API calls.
"""
import sys
from unittest.mock import MagicMock

_STUB_MODULES = [
    "googleapiclient",
    "googleapiclient.discovery",
    "googleapiclient.http",
    "google",
    "google.auth",
    "google.auth.exceptions",
    "google.auth.transport",
    "google.auth.transport.requests",
    "google.oauth2",
    "google.oauth2.credentials",
    "google_auth_oauthlib",
    "google_auth_oauthlib.flow",
    "nacl",
    "nacl.encoding",
    "nacl.public",
    "edge_tts",
]


def install():
    for name in _STUB_MODULES:
        if name not in sys.modules:
            sys.modules[name] = MagicMock()
    # RefreshError needs to actually be an Exception subclass, since code
    # does `except RefreshError as e:` - a plain MagicMock can't be caught.
    class _FakeRefreshError(Exception):
        pass
    sys.modules["google.auth.exceptions"].RefreshError = _FakeRefreshError
