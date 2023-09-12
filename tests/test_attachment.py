import unittest

from simple_discord_tts.attachment import judge_filetype


class TestJudgeFiletype(unittest.TestCase):
    def test_image(self):
        assert judge_filetype("test.jpg") == "画像"

    def test_video(self):
        assert judge_filetype("test.mov") == "動画"

    def test_audio(self):
        assert judge_filetype("test.mp3") == "音声"
