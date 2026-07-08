import os
import tempfile
import unittest

from tests import stub_deps
stub_deps.install()

import learn


class LoadStateTests(unittest.TestCase):
    def test_missing_state_file_returns_safe_default_instead_of_crashing(self):
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as d:
            os.chdir(d)
            try:
                # No state.json exists in this empty temp dir.
                state = learn.load_state()
                self.assertEqual(state["post_log"], [])
                self.assertEqual(state["theme_scores"], {})
            finally:
                os.chdir(cwd)


class UpdateScoreTests(unittest.TestCase):
    def test_first_value_sets_score_directly(self):
        scores = {}
        learn.update_score(scores, "career_confidence", 0.5)
        self.assertEqual(scores["career_confidence"], 0.5)

    def test_subsequent_values_use_ema(self):
        scores = {"career_confidence": 0.5}
        learn.update_score(scores, "career_confidence", 1.0)
        expected = (1 - learn.EMA_ALPHA) * 0.5 + learn.EMA_ALPHA * 1.0
        self.assertAlmostEqual(scores["career_confidence"], expected)

    def test_ema_weights_recent_but_not_completely(self):
        scores = {"x": 0.0}
        learn.update_score(scores, "x", 1.0)
        # Should move toward 1.0 but not jump all the way there in one step.
        self.assertGreater(scores["x"], 0.0)
        self.assertLess(scores["x"], 1.0)


class EngagementScoreIntegrationTests(unittest.TestCase):
    def test_engagement_score_used_consistently(self):
        from analytics import engagement_score
        stats = {"views": 100, "likes": 10, "comments": 2, "shares": 1, "saves": 3}
        score = engagement_score(stats)
        expected = (10 + 2 * 3 + 1 * 5 + 3 * 4) / 100
        self.assertAlmostEqual(score, expected)

    def test_zero_views_does_not_divide_by_zero(self):
        from analytics import engagement_score
        score = engagement_score({"views": 0, "likes": 5})
        self.assertIsInstance(score, float)  # must not raise ZeroDivisionError


if __name__ == "__main__":
    unittest.main()
