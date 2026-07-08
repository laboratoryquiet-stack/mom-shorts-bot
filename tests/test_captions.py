import os
import tempfile
import unittest

from tests import stub_deps
stub_deps.install()

import captions


class FormatAssTimeTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(captions.format_ass_time(0), "0:00:00.00")

    def test_sub_minute(self):
        self.assertEqual(captions.format_ass_time(12.34), "0:00:12.34")

    def test_over_a_minute(self):
        self.assertEqual(captions.format_ass_time(75.5), "0:01:15.50")

    def test_over_an_hour(self):
        self.assertEqual(captions.format_ass_time(3661.0), "1:01:01.00")


class BuildAssTests(unittest.TestCase):
    def test_produces_one_dialogue_event_per_line(self):
        tts_lines = [
            {"text": "Hello there", "duration": 2.0,
             "words": [{"word": "Hello", "start": 0.0, "duration": 0.5},
                       {"word": "there", "start": 0.5, "duration": 0.5}]},
            {"text": "Second line", "duration": 1.5,
             "words": [{"word": "Second", "start": 0.0, "duration": 0.5},
                       {"word": "line", "start": 0.5, "duration": 0.5}]},
        ]
        with tempfile.TemporaryDirectory() as d:
            out_path = os.path.join(d, "test.ass")
            captions.build_ass(tts_lines, out_path=out_path)
            content = open(out_path).read()
        self.assertEqual(content.count("Dialogue:"), 2)

    def test_handles_missing_word_timings_gracefully(self):
        # words=[] (e.g. edge-tts returned no WordBoundary events) must not
        # crash - falls back to one karaoke block for the whole line.
        tts_lines = [{"text": "No word timings here", "duration": 2.0, "words": []}]
        with tempfile.TemporaryDirectory() as d:
            out_path = os.path.join(d, "test.ass")
            result_path = captions.build_ass(tts_lines, out_path=out_path)
            content = open(result_path).read()
        self.assertIn("No word timings here", content)

    def test_curly_braces_in_words_are_stripped(self):
        # Raw { or } in a word would corrupt the ASS override-tag syntax.
        tts_lines = [{"text": "test", "duration": 1.0,
                      "words": [{"word": "{weird}", "start": 0.0, "duration": 1.0}]}]
        with tempfile.TemporaryDirectory() as d:
            out_path = os.path.join(d, "test.ass")
            captions.build_ass(tts_lines, out_path=out_path)
            content = open(out_path).read()
        self.assertNotIn("{weird}", content)
        self.assertIn("weird", content)


if __name__ == "__main__":
    unittest.main()
