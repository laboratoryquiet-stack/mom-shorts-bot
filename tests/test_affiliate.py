import unittest
from unittest.mock import patch

from tests import stub_deps
stub_deps.install()

import affiliate
import config


class AmazonLinkTests(unittest.TestCase):
    def test_falls_back_to_keyword_search_when_no_specific_product(self):
        # SPECIFIC_PRODUCTS ships empty by default (user fills it in), so
        # every theme should currently fall back to a keyword search URL.
        for theme in config.THEMES:
            with self.subTest(theme=theme):
                link = affiliate.amazon_link_for_theme(theme)
                self.assertTrue(link.startswith("https://www.amazon.com/s?k="))
                self.assertIn("tag=", link)

    def test_uses_specific_product_when_available(self):
        fake_products = {"time_management": [{"label": "Test Planner", "asin": "B000000000"}]}
        with patch.object(affiliate, "SPECIFIC_PRODUCTS", fake_products):
            link = affiliate.amazon_link_for_theme("time_management")
            self.assertIn("B000000000", link)
            self.assertTrue(link.startswith("https://www.amazon.com/dp/"))

    def test_label_matches_selected_product(self):
        fake_products = {"time_management": [{"label": "Test Planner", "asin": "B000000000"}]}
        with patch.object(affiliate, "SPECIFIC_PRODUCTS", fake_products):
            label = affiliate.amazon_label_for_theme("time_management")
            self.assertEqual(label, "Test Planner")

    def test_unknown_theme_does_not_crash(self):
        # A theme string that exists nowhere in config should still degrade
        # gracefully to the generic default keyword search, never KeyError.
        link = affiliate.amazon_link_for_theme("totally_made_up_theme")
        self.assertTrue(link.startswith("https://www.amazon.com/s?k="))

    def test_tag_env_override(self):
        with patch.dict("os.environ", {"AMAZON_ASSOCIATE_TAG": "custom-tag-20"}):
            link = affiliate.amazon_link_for_theme("time_management")
            self.assertIn("tag=custom-tag-20", link)


class DisclosureTests(unittest.TestCase):
    def test_youtube_addon_includes_disclosure(self):
        addon = affiliate.youtube_description_addon("time_management")
        self.assertIn(affiliate.DISCLOSURE, addon)

    def test_instagram_addon_includes_disclosure(self):
        addon = affiliate.instagram_caption_addon()
        self.assertIn(affiliate.DISCLOSURE, addon)


class LtkLinkTests(unittest.TestCase):
    def test_empty_without_handle(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(affiliate.ltk_profile_link(), "")

    def test_builds_link_with_handle(self):
        with patch.dict("os.environ", {"LTK_PROFILE_HANDLE": "mystyle"}):
            self.assertEqual(affiliate.ltk_profile_link(), "https://www.shopltk.com/explore/mystyle")


if __name__ == "__main__":
    unittest.main()
