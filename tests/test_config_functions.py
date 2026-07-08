import unittest

from tests import stub_deps
stub_deps.install()

import config


class BuildHashtagsTests(unittest.TestCase):
    def test_respects_count_limit(self):
        tags = config.build_hashtags("time_management", count=3)
        self.assertEqual(len(tags.split()), 3)

    def test_theme_tags_come_first(self):
        tags = config.build_hashtags("time_management", count=1)
        self.assertEqual(tags, config.THEME_HASHTAGS["time_management"][0])

    def test_no_duplicate_tags(self):
        tags = config.build_hashtags("time_management", count=20).split()
        self.assertEqual(len(tags), len(set(tags)))

    def test_unknown_theme_still_returns_general_tags(self):
        tags = config.build_hashtags("not_a_real_theme", count=3)
        self.assertEqual(len(tags.split()), 3)

    def test_none_theme_does_not_crash(self):
        tags = config.build_hashtags(None, count=3)
        self.assertEqual(len(tags.split()), 3)


class TopTitleHashtagsTests(unittest.TestCase):
    def test_accepts_theme_argument(self):
        # Regression test: top_title_hashtags() used to take zero arguments
        # while pipeline_core.py called it with one, crashing every run.
        result = config.top_title_hashtags("time_management")
        self.assertIsInstance(result, str)
        self.assertIn("#workingmom", result)

    def test_works_with_no_argument(self):
        result = config.top_title_hashtags()
        self.assertIsInstance(result, str)


class NormalizedWeightsTests(unittest.TestCase):
    def test_sums_to_one(self):
        weights = config.get_normalized_weights({"a": 3, "b": 1})
        self.assertAlmostEqual(sum(weights.values()), 1.0)

    def test_empty_input_returns_empty(self):
        self.assertEqual(config.get_normalized_weights({}), {})

    def test_all_zero_falls_back_to_uniform(self):
        weights = config.get_normalized_weights({"a": 0, "b": 0})
        self.assertAlmostEqual(weights["a"], 0.5)
        self.assertAlmostEqual(weights["b"], 0.5)

    def test_negative_scores_are_clamped(self):
        weights = config.get_normalized_weights({"a": -5, "b": 5})
        self.assertEqual(weights["a"], 0.0)
        self.assertAlmostEqual(weights["b"], 1.0)


if __name__ == "__main__":
    unittest.main()
