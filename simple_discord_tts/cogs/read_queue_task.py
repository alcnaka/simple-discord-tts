import asyncio
import wave
from logging import getLogger
from tempfile import NamedTemporaryFile
from typing import Self

from discord import DiscordException, FFmpegPCMAudio, PCMVolumeTransformer, VoiceChannel, VoiceClient
from discord.ext import commands, tasks
from discord.ext.commands import Context

from simple_discord_tts.app import TTSBot
from simple_discord_tts.exceptions import (
    TTSBackendError,
    TTSBackendUnavailable,
    TTSInvalidRequest,
)
from simple_discord_tts.tts import tts

logger = getLogger(__name__)


class ReadQueueCog(commands.Cog):
    def __init__(self: Self, bot: TTSBot) -> None:
        self.bot = bot

    @commands.command()
    async def reload(self: Self, _: Context) -> None:
        self.read_queue.stop()
        self.read_queue.start()

    @commands.Cog.listener()
    async def on_ready(self: Self) -> None:
        if not self.read_queue.is_running():
            self.read_queue.start()

    async def _voice_client(self: Self, channel: VoiceChannel) -> VoiceClient | None:
        voice_client = channel.guild.voice_client
        try:
            if isinstance(voice_client, VoiceClient):
                if not voice_client.is_connected():
                    # Release a stale client before starting another handshake.
                    await voice_client.disconnect(force=True)
                elif voice_client.channel != channel:
                    await voice_client.move_to(channel)
                    return voice_client
                else:
                    return voice_client
            return await channel.connect()
        except (TimeoutError, DiscordException, OSError) as exc:
            logger.warning(
                "Voice connection failed guild=%s channel=%s error=%s detail=%s",
                channel.guild.id,
                channel.id,
                type(exc).__name__,
                exc,
            )
            return None

    @tasks.loop(seconds=1)
    async def read_queue(self: Self) -> None:
        ctx = await self.bot.queue.get()
        try:
            logger.debug(
                "Reading queue guild=%s channel=%s text_len=%s qsize=%s",
                ctx.voice_channel.guild.id,
                ctx.voice_channel.id,
                len(ctx.text),
                self.bot.queue.qsize(),
            )
            voice_client = await self._voice_client(ctx.voice_channel)
            if not isinstance(voice_client, VoiceClient):
                return
            wav = await tts(ctx.text)
            with NamedTemporaryFile() as f:
                f.write(wav)
                f.flush()
                audio_source = FFmpegPCMAudio(f.name)
                audio_source = PCMVolumeTransformer(audio_source, 0.18)
                with wave.open(f.name) as wr:
                    pt = wr.getnframes() / wr.getframerate()

                voice_client.play(audio_source)
                await asyncio.sleep(pt + 0.2)
        except TTSInvalidRequest:
            logger.info(
                "Skipping unsynthesizable text guild=%s channel=%s text_len=%s",
                ctx.voice_channel.guild.id,
                ctx.voice_channel.id,
                len(ctx.text),
            )
        except (TTSBackendUnavailable, TTSBackendError) as exc:
            logger.warning(
                "TTS failed guild=%s channel=%s error=%s",
                ctx.voice_channel.guild.id,
                ctx.voice_channel.id,
                type(exc).__name__,
            )
        except Exception:
            logger.exception(
                "Queue job failed guild=%s channel=%s",
                ctx.voice_channel.guild.id,
                ctx.voice_channel.id,
            )
        finally:
            self.bot.queue.task_done()

    @tasks.loop(seconds=1)
    async def auto_leave(self: Self) -> None:
        pass
