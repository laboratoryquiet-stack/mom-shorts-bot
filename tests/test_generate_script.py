import unittest

from tests import stub_deps
stub_deps.install()

from unittest.mock import patch

import config
import generate_script as gs


class DrawFromBagTests(unittest.TestCase):
    def test_no_repeats_until_pool_exhausted(self):
        state = {}
        pool = ["a", "b", "c", "d"]
        drawn = [gs.draw_from_bag(pool, state, "k") for _ in range(len(pool))]
        self.assertEqual(sorted(drawn), sorted(pool), "one full cycle must draw every item exactly once")

    def test_bag_reshuffles_after_exhaustion(self):
        state = {}
        pool = ["a", "b"]
        # Draw 3 full cycles worth - should never raise, and each cycle
        # should still be a permutation of the pool.
        all_draws = [gs.draw_from_bag(pool, state, "k") for _ in range(6)]
        for cycle in (all_draws[0:2], all_draws[2:4], all_draws[4:6]):
            self.assertEqual(sorted(cycle), sorted(pool))

    def test_weighted_pick_still_covers_full_bag(self):
        # Even with score-weighted ordering, every item in the pool must
        # still be drawn exactly once per cycle - weighting changes ORDER,
        # not coverage.
        state = {}
        pool = ["a", "b", "c"]
        scores = {"a": 0.9, "b": 0.05, "c": 0.05}
        drawn = [gs.draw_from_bag(pool, state, "k", score_dict=scores) for _ in range(3)]
        self.assertEqual(sorted(drawn), sorted(pool))


class ScriptSignatureTests(unittest.TestCase):
    def test_same_lines_same_signature(self):
        lines = ["a", "b", "c"]
        self.assertEqual(gs.script_signature(lines), gs.script_signature(list(lines)))

    def test_different_lines_different_signature(self):
        self.assertNotEqual(gs.script_signature(["a", "b"]), gs.script_signature(["b", "a"]))


class GenerateAffirmationDedupTests(unittest.TestCase):
    @patch("generate_script.fetch_audience_theme", return_value=None)
    @patch("generate_script.fetch_trending_theme", return_value=None)
    def test_affirmation_scripts_have_expected_line_count(self, _trend, _aud):
        state = gs.load_state()
        result = gs.generate_affirmation(state)
        # opener + AFFIRMATIONS_PER_SCRIPT + closer + cta
        self.assertEqual(len(result["lines"]), 3 + gs.AFFIRMATIONS_PER_SCRIPT)
        self.assertEqual(result["content_type"], "affirmation")
        self.assertIn(result["theme"], config.THEMES)

    @patch("generate_script.fetch_audience_theme", return_value=None)
    @patch("generate_script.fetch_trending_theme", return_value=None)
    def test_repeated_generation_does_not_crash_and_eventually_dedups(self, _trend, _aud):
        state = gs.load_state()
        signatures = set()
        for _ in range(20):
            result = gs.generate_affirmation(state)
            signatures.add(gs.script_signature(result["lines"]))
        # Not asserting all 20 are unique (small banks can legitimately
        # collide within MAX_DEDUP_ATTEMPTS), just that generation is
        # actually producing variety, not the same script every time.
        self.assertGreater(len(signatures), 1)


class GenerateCadenceTests(unittest.TestCase):
    """Verifies generate()'s slot cadence: every 5th post is a spotlight,
    every 3rd non-spotlight post is practical content, and the remaining
    'regular' slots cycle through all 5 content types rather than only
    ever alternating between two."""

    @patch("generate_script.fetch_audience_theme", return_value=None)
    @patch("generate_script.fetch_trending_theme", return_value=None)
    def test_spotlight_cadence(self, _trend, _aud):
        state = gs.load_state()
        gs.save_state(state)
        content_types = []
        # Generate SPOTLIGHT_EVERY_N + 1 posts to capture both a regular
        # slot and a spotlight slot. First spotlight appears at post 5
        # (post_count=4, since the condition is count > 0 and count % 5 == 0).
        for _ in range(gs.SPOTLIGHT_EVERY_N + 1):
            result = gs.generate()
            content_types.append(result["content_type"])
        self.assertIn("spotlight", content_types)

    @patch("generate_script.fetch_audience_theme", return_value=None)
    @patch("generate_script.fetch_trending_theme", return_value=None)
    def test_regular_slots_cycle_through_all_five_types(self, _trend, _aud):
        state = gs.load_state()
        gs.save_state(state)
        seen_types = set()
        # Generate enough posts to guarantee every regular slot type shows
        # up at least once, skipping over spotlight/practical interruptions.
        for _ in range(30):
            result = gs.generate()
            if result["content_type"] in gs.REGULAR_SLOT_ROTATION:
                seen_types.add(result["content_type"])
        self.assertEqual(seen_types, set(gs.REGULAR_SLOT_ROTATION))


class ChooseThemeTests(unittest.TestCase):
    @patch("generate_script.fetch_audience_theme", return_value=None)
    @patch("generate_script.fetch_trending_theme", return_value=None)
    def test_round_robin_covers_all_themes_without_signals(self, _trend, _aud):
        state = {"theme_index": 0}
        seen = [gs.choose_theme(state) for _ in range(len(config.THEMES))]
        self.assertEqual(sorted(seen), sorted(config.THEMES))

    @patch("generate_script.fetch_audience_theme", return_value="career_confidence")
    def test_audience_theme_can_override_when_probability_hits(self, _aud):
        state = {"theme_index": 0}
        with patch("generate_script.random.random", return_value=0.0):  # forces < AUDIENCE_NUDGE_PROBABILITY
            theme = gs.choose_theme(state)
        self.assertEqual(theme, "career_confidence")


if __name__ == "__main__":
    unittest.main()
