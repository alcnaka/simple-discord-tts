import unittest
from unittest.mock import patch

import httpx

from simple_discord_tts.exceptions import TTSBackendError, TTSBackendUnavailable, TTSInvalidRequest
from simple_discord_tts.tts import tts


class TestTTS(unittest.IsolatedAsyncioTestCase):
    async def _request(self, handler):
        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        with patch("simple_discord_tts.tts.httpx.AsyncClient", return_value=client):
            return await tts("テスト")

    async def test_wav_response(self):
        wav = b"RIFFtestWAVE"
        result = await self._request(
            lambda _: httpx.Response(200, content=wav, headers={"content-type": "audio/wav"})
        )
        self.assertEqual(result, wav)

    async def test_no_phoneme_is_invalid_request(self):
        with self.assertRaises(TTSInvalidRequest):
            await self._request(lambda _: httpx.Response(422, json={"detail": "no phoneme"}))

    async def test_server_failure_is_unavailable(self):
        with self.assertRaises(TTSBackendUnavailable):
            await self._request(lambda _: httpx.Response(500, text="failure"))

    async def test_non_audio_success_is_rejected(self):
        with self.assertRaises(TTSBackendError):
            await self._request(lambda _: httpx.Response(200, json={"message": "unexpected"}))

    async def test_connect_timeout_is_unavailable(self):
        def timeout(request):
            raise httpx.ConnectTimeout("timed out", request=request)

        with self.assertRaises(TTSBackendUnavailable):
            await self._request(timeout)

    async def test_read_timeout_is_unavailable(self):
        def timeout(request):
            raise httpx.ReadTimeout("timed out", request=request)

        with self.assertRaises(TTSBackendUnavailable):
            await self._request(timeout)
