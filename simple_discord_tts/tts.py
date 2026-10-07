from logging import getLogger

import aiofiles
import httpx

from .exceptions import TTSBackendError, TTSBackendUnavailable, TTSInvalidRequest
from .settings import settings

logger = getLogger(__name__)


async def tts(t: str) -> bytes:
    data = {
        "voice": "mei_normal",
        "speed": 1,
        "pitch": 0,
        "vtype": 0.55,
        "syn_text": t,
        "normalize": True,
    }
    logger.debug("TTS request voice=%s text_len=%s", data["voice"], len(t))
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(settings.VOICE_BACKEND_URL, json=data)
    except httpx.RequestError as exc:
        logger.warning("TTS request failed error=%s text_len=%s", type(exc).__name__, len(t))
        raise TTSBackendUnavailable("TTS backend connection failed") from exc

    content_type = r.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    logger.debug("TTS response status=%s content_type=%s text_len=%s", r.status_code, content_type, len(t))
    if r.status_code == 422:
        logger.info("TTS input rejected status=422 text_len=%s", len(t))
        raise TTSInvalidRequest("TTS backend rejected input (status=422)")
    if r.status_code >= 500:
        logger.warning("TTS backend failure status=%s text_len=%s", r.status_code, len(t))
        raise TTSBackendUnavailable(f"TTS backend failed (status={r.status_code})")
    if not 200 <= r.status_code < 300:
        logger.warning("TTS request rejected status=%s text_len=%s", r.status_code, len(t))
        raise TTSBackendError(f"TTS backend rejected request (status={r.status_code})")
    if content_type not in {"audio/wav", "audio/wave", "audio/x-wav"}:
        logger.warning("TTS non-WAV response status=%s content_type=%s text_len=%s", r.status_code, content_type, len(t))
        raise TTSBackendError(f"TTS backend returned non-WAV content (content_type={content_type})")
    return r.content


async def main() -> None:
    voice_data = await tts("てすと")
    async with aiofiles.open("test.wav", mode="bw") as f:
        await f.write(voice_data)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
