import httpx
from logging import getLogger

from .settings import settings
from .exceptions import TTSException

logger = getLogger(__name__)

async def tts(t: str) -> bytes:
    data = {
        "voice": "mei_normal",
        "speed": 1,
        "pitch": 0,
        "vtype": 0.55,
        "syn_text": t,
        "normalize": True
    }
    r = httpx.post(settings.VOICE_BACKEND_URL, json=data)
    if r.status_code != 200:
        logger.warning(f'TTS Request Failed ({ r.status_code }: {r.text})')
    return r.content


async def main() -> None:
    voice_data = await tts("てすと")
    with open('test.wav', mode='bw') as f:
        f.write(voice_data)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
