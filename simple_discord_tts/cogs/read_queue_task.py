import asyncio
from logging import getLogger
from tempfile import NamedTemporaryFile
import wave

from discord.ext import commands, tasks
from discord import Message, ClientException, VoiceClient, FFmpegPCMAudio, PCMVolumeTransformer

from simple_discord_tts.app import TTSContext, TTSBot
from simple_discord_tts.tts import tts

logger = getLogger(__name__)

class ReadQueueCog(commands.Cog):
    def __init__(self, bot: TTSBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.read_queue.start()

    @tasks.loop(seconds=1)
    async def read_queue(self) -> None:
        ctx = await self.bot.queue.get()
        try:
            voice_client = await ctx.voice_channel.connect()
        except ClientException as e:
            logger.info('already joined')
            voice_client = self.bot.voice_clients[0]
            if type(voice_client) != VoiceClient:
                logger.warning(voice_client)
                return
            if voice_client.channel != ctx.voice_channel:
                await voice_client.move_to(ctx.voice_channel)

        if type(voice_client) != VoiceClient:
            return

        with NamedTemporaryFile() as f:
            wav = (await tts(ctx.text))
            f.write(wav)
            audio_source = FFmpegPCMAudio(f.name)
            audio_source = PCMVolumeTransformer(audio_source, 0.18)

            voice_client.play(audio_source)
            with wave.open(f.name) as wr:
                pt = wr.getnframes() / wr.getframerate()
            await asyncio.sleep(pt + 0.2)


    @tasks.loop(seconds=1)
    async def auto_leave(self) -> None:
        pass
