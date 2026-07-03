"""
Turns each post's theme into a relevant Amazon Associates link — no manual
link curation needed, just sign up for the (free) Amazon Associates program
and set your tag once.

Sign-up: affiliate-program.amazon.com (free). After approval you get an
associate tag like "yoursite-20" — set it as the AMAZON_ASSOCIATE_TAG
GitHub secret.

Important, read before relying on this for income:
- Amazon requires 3 qualifying sales within 180 days of joining or they can
  close the account — it is not a guaranteed passive setup from day one.
- FTC disclosure is legally required on affiliate content, not optional —
  this module always appends a disclosure line, don't remove it.
- Double-check Amazon's current Associates Program Operating Agreement for
  any platform-specific restrictions before relying on this long-term;
  affiliate program rules do change.
"""
import os
import urllib.parse

from config import AMAZON_KEYWORDS

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases. #ad"


def amazon_link_for_theme(theme: str) -> str:
    tag = os.environ.get("AMAZON_ASSOCIATE_TAG")
    if not tag:
        return ""
    keyword = AMAZON_KEYWORDS.get(theme, "gifts for working moms")
    query = urllib.parse.quote_plus(keyword)
    return f"https://www.amazon.com/s?k={query}&tag={tag}"


def ltk_profile_link() -> str:
    """
    LTK (LikeToKnow.it / ltk.app) is a free, popular affiliate platform
    specifically built for lifestyle/mom content creators — often converts
    better than generic Amazon search links because it's a curated shop
    front tied to your personal brand. Free to join at creator.shopltk.com.
    Unlike the per-theme Amazon links, LTK works as ONE stable profile link
    (like the Instagram bio pattern) rather than a per-post dynamic link.
    """
    handle = os.environ.get("LTK_PROFILE_HANDLE")
    if not handle:
        return ""
    return f"https://www.shopltk.com/explore/{handle}"


def youtube_description_addon(theme: str) -> str:
    """YouTube descriptions support real clickable links — include directly."""
    amazon = amazon_link_for_theme(theme)
    ltk = ltk_profile_link()
    lines = []
    if amazon:
        lines.append(f"🛍️ Something that might help: {amazon}")
    if ltk:
        lines.append(f"🛍️ My full shop: {ltk}")
    if not lines:
        return ""
    return "\n\n" + "\n".join(lines) + f"\n{DISCLOSURE}"


def instagram_caption_addon() -> str:
    """
    Instagram captions do NOT support clickable links — only the bio link
    does. Keep ONE stable link in your bio (either your Amazon "List" or
    your LTK profile — LTK is purpose-built for exactly this "shop my
    picks from Instagram" use case) rather than trying to change it per post.
    """
    return f"\n\n🛍️ Shopping list in bio\n{DISCLOSURE}"
