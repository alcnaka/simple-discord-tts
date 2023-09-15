from logging import getLogger

import aiofiles
import httpx

from .settings import settings

logger = getLogger(__name__)


HTTP_OK = 200


async def tts(t: str) -> bytes:
    data = {
        "voice": "mei_normal",
        "speed": 1,
        "pitch": 0,
        "vtype": 0.55,
        "syn_text": t,
        "normalize": True,
    }
    logger.debug("tts: %s", str(data))
    async with httpx.AsyncClient() as client:
        r = await client.post(settings.VOICE_BACKEND_URL, json=data)
        if r.status_code != HTTP_OK:
            logger.warning("TTS Request Failed (%s: %s)", r.status_code, r.text)
    return r.content


async def main() -> None:
    voice_data = await tts("てすと")
    async with aiofiles.open("test.wav", mode="bw") as f:
        await f.write(voice_data)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
