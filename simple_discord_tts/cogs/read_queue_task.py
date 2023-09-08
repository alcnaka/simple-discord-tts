import asyncio
import wave
from logging import getLogger
from tempfile import NamedTemporaryFile
from typing import Self

from discord import ClientException, FFmpegPCMAudio, PCMVolumeTransformer, VoiceClient
from discord.ext import commands, tasks
from discord.ext.commands import Context

from simple_discord_tts.app import TTSBot
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
        self.read_queue.start()

    @tasks.loop(seconds=1)
    async def read_queue(self: Self) -> None:
        ctx = await self.bot.queue.get()
        t = f"Reading queue: {ctx.voice_channel.name} {ctx.text}"
        logger.debug(t)
        try:
            voice_client = await ctx.voice_channel.connect()
        except ClientException:
            logger.info("already joined")
            logger.info(f"VoiceClientCount: {len(self.bot.voice_clients)}")
            voice_client = ctx.voice_channel.guild.voice_client
            if type(voice_client) != VoiceClient:
                logger.warning(voice_client)
                return
            if voice_client.channel != ctx.voice_channel:
                await voice_client.move_to(ctx.voice_channel)

        if type(voice_client) != VoiceClient:
            return

        try:
            with NamedTemporaryFile() as f:
                wav = await tts(ctx.text)
                f.write(wav)
                audio_source = FFmpegPCMAudio(f.name)
                audio_source = PCMVolumeTransformer(audio_source, 0.18)
                with wave.open(f.name) as wr:
                    pt = wr.getnframes() / wr.getframerate()

                voice_client.play(audio_source)
                await asyncio.sleep(pt + 0.2)
        except Exception:
            logger.exception("some errors in read_queue")

    @tasks.loop(seconds=1)
    async def auto_leave(self: Self) -> None:
        pass
