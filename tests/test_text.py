from unittest import TestCase

from simple_discord_tts.text import clean_url


class TestCleanUrl(TestCase):
    def test_normal(self):
        assert clean_url("https://example.com") == ""

    def test_path(self):
        assert clean_url("https://example.com/test/path") == ""

    def test_query(self):
        assert clean_url("https://example.com/test/path?key=value") == ""

    def test_query2(self):
        assert clean_url("https://example.com/test/path?key=value asdf") == "asdf"
