from __future__ import annotations

import unittest

from deepreader_skill.parsers.twitter import TwitterParser


class TwitterParserFxTwitterNullMetricsTest(unittest.TestCase):
    def test_build_result_handles_null_metrics(self) -> None:
        parser = TwitterParser()
        data = {
            "tweet": {
                "author": {"name": "jack", "screen_name": "jack"},
                "created_at": "2006-03-21 20:50:14 UTC",
                "text": "just setting up my twttr",
                "likes": 42,
                "retweets": 7,
                "bookmarks": 0,
                "views": None,
                "replies": 3,
                "quote": {
                    "author": {"screen_name": "biz"},
                    "text": "quoted",
                    "likes": 5,
                    "retweets": 1,
                    "views": None,
                },
            }
        }

        result = parser._build_result_from_fxtwitter(
            "https://x.com/jack/status/20",
            data,
        )

        self.assertTrue(result.success)
        self.assertIn("👁", result.content)
        self.assertIn("n/a", result.content)


if __name__ == "__main__":
    unittest.main()
