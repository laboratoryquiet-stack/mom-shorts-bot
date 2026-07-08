"""
This file exists because of a real incident: config.py drifted out of sync
with generate_script.py (missing constants, wrong data shapes, a literal
placeholder opener string that would have gone out in a real video) and the
project crashed in deploy as a result.

These tests assert STRUCTURAL invariants across config.py so that kind of
drift fails a test locally instead of failing a scheduled GitHub Actions
run in production.
"""
import unittest

from tests import stub_deps
stub_deps.install()

import config


class ThemeCompletenessTests(unittest.TestCase):
    """Every theme in config.THEMES must have real content everywhere the
    pipeline looks it up by key, or generate_script.py raises KeyError at
    runtime the moment that theme is chosen (which, with random rotation,
    WILL eventually happen for every theme)."""

    def test_every_theme_has_openers(self):
        for theme in config.THEMES:
            with self.subTest(theme=theme):
                self.assertIn(theme, config.OPENERS, f"{theme} missing from OPENERS")
                self.assertGreaterEqual(
                    len(config.OPENERS[theme]), 3,
                    f"{theme} has fewer than 3 openers - shuffle bag needs real variety",
                )

    def test_every_theme_has_hashtags(self):
        for theme in config.THEMES:
            with self.subTest(theme=theme):
                self.assertIn(theme, config.THEME_HASHTAGS, f"{theme} missing from THEME_HASHTAGS")
                self.assertGreater(len(config.THEME_HASHTAGS[theme]), 0)

    def test_every_theme_has_amazon_keyword_fallback(self):
        for theme in config.THEMES:
            with self.subTest(theme=theme):
                self.assertIn(theme, config.AMAZON_KEYWORDS, f"{theme} missing from AMAZON_KEYWORDS")

    def test_fallback_tag_has_hashtags_and_keywords(self):
        # FALLBACK_TAG (spotlight) is used as asset["theme"] for spotlight
        # posts, so it needs the same coverage as a regular theme.
        self.assertIn(config.FALLBACK_TAG, config.THEME_HASHTAGS)
        self.assertIn(config.FALLBACK_TAG, config.AMAZON_KEYWORDS)

    def test_calendar_boost_only_references_real_themes(self):
        for month, boosted_list in config.CALENDAR_THEME_BOOST.items():
            with self.subTest(month=month):
                self.assertIsInstance(month, int)
                self.assertTrue(1 <= month <= 12)
                for theme in boosted_list:
                    self.assertIn(theme, config.THEMES, f"month {month} boosts unknown theme {theme}")


class ContentBankShapeTests(unittest.TestCase):
    """Every curated content bank must have the exact dict shape
    generate_script.py indexes into (theme/hook/tips/lines) - a flat list
    of strings here (an earlier bug) crashes with 'string indices must be
    integers' the moment that bank is drawn from."""

    def _assert_theme_hook_body(self, bank, body_key, min_body_len=1):
        self.assertGreater(len(bank), 0, "content bank must not be empty")
        for entry in bank:
            with self.subTest(entry=entry.get("hook", entry)):
                self.assertIsInstance(entry, dict, "entry must be a dict, not a bare string")
                self.assertIn("theme", entry)
                self.assertIn(entry["theme"], config.THEMES, f"unknown theme {entry['theme']!r}")
                self.assertIn("hook", entry)
                self.assertIsInstance(entry["hook"], str)
                self.assertIn(body_key, entry)
                self.assertGreaterEqual(len(entry[body_key]), min_body_len)

    def test_tip_content_shape(self):
        self._assert_theme_hook_body(config.TIP_CONTENT, "tips")

    def test_support_content_shape(self):
        self._assert_theme_hook_body(config.SUPPORT_CONTENT, "lines")

    def test_humor_content_shape(self):
        self._assert_theme_hook_body(config.HUMOR_CONTENT, "lines")

    def test_myth_bust_content_shape(self):
        self._assert_theme_hook_body(config.MYTH_BUST_CONTENT, "lines")

    def test_hack_demo_content_shape(self):
        self._assert_theme_hook_body(config.HACK_DEMO_CONTENT, "lines")

    def test_this_or_that_content_shape(self):
        self._assert_theme_hook_body(config.THIS_OR_THAT_CONTENT, "lines")

    def test_spotlight_stories_shape(self):
        self.assertGreater(len(config.SPOTLIGHT_STORIES), 0)
        for story in config.SPOTLIGHT_STORIES:
            with self.subTest(story=story.get("name")):
                self.assertIsInstance(story, dict)
                self.assertIn("name", story)
                self.assertIn("lines", story)
                self.assertGreaterEqual(len(story["lines"]), 1)


class NoPlaceholderTextTests(unittest.TestCase):
    """Catches the exact prior incident: a literal placeholder string left
    in OPENERS that would have been spoken/captioned in a real video."""

    PLACEHOLDER_MARKERS = [
        "your list", "placeholder", "todo", "fixme", "lorem ipsum",
        "opener text string", "xxx", "insert text",
    ]

    def _assert_no_placeholders(self, texts):
        for text in texts:
            lowered = text.lower()
            for marker in self.PLACEHOLDER_MARKERS:
                self.assertNotIn(
                    marker, lowered,
                    f"placeholder text leaked into shippable content: {text!r}",
                )

    def test_openers_have_no_placeholders(self):
        for theme, openers in config.OPENERS.items():
            with self.subTest(theme=theme):
                self._assert_no_placeholders(openers)

    def test_affirmations_closers_ctas_have_no_placeholders(self):
        self._assert_no_placeholders(config.AFFIRMATIONS)
        self._assert_no_placeholders(config.CLOSERS)
        self._assert_no_placeholders(config.CTA_POOL)

    def test_all_content_banks_have_no_placeholders(self):
        for bank, body_key in [
            (config.TIP_CONTENT, "tips"),
            (config.SUPPORT_CONTENT, "lines"),
            (config.HUMOR_CONTENT, "lines"),
            (config.MYTH_BUST_CONTENT, "lines"),
            (config.HACK_DEMO_CONTENT, "lines"),
            (config.THIS_OR_THAT_CONTENT, "lines"),
        ]:
            for entry in bank:
                self._assert_no_placeholders([entry["hook"], *entry[body_key]])


class TrendingTopicsThemeConsistencyTests(unittest.TestCase):
    """trending_topics.py and audience_comments.py can hand choose_theme() a
    theme value pulled from a keyword map that lives in a DIFFERENT file
    from config.py's THEMES list - these must stay in sync or generate_script
    crashes with a KeyError the first time a real-world trend gets detected."""

    def test_keyword_theme_map_only_targets_real_themes(self):
        import trending_topics
        for keyword, theme in trending_topics.KEYWORD_THEME_MAP.items():
            with self.subTest(keyword=keyword, theme=theme):
                self.assertIn(theme, config.THEMES, f"trending_topics maps {keyword!r} to unknown theme {theme!r}")


if __name__ == "__main__":
    unittest.main()
