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

    @commands.command()
    async def reload(self, ctx) -> None:
        self.read_queue.stop()
        self.read_queue.start()

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
            logger.info(f'VoiceClientCount: {len(self.bot.voice_clients)}')
            voice_client = self.bot.voice_clients[0]
            if type(voice_client) != VoiceClient:
                logger.warning(voice_client)
                return
            if voice_client.channel != ctx.voice_channel:
                await voice_client.move_to(ctx.voice_channel)

        if type(voice_client) != VoiceClient:
            return

        try:
            with NamedTemporaryFile() as f:
                wav = (await tts(ctx.text))
                f.write(wav)
                audio_source = FFmpegPCMAudio(f.name)
                audio_source = PCMVolumeTransformer(audio_source, 0.18)
                with wave.open(f.name) as wr:
                    pt = wr.getnframes() / wr.getframerate()

                voice_client.play(audio_source)
                await asyncio.sleep(pt + 0.2)
        except Exception:
            logger.exception('some errors in read_queue')


    @tasks.loop(seconds=1)
    async def auto_leave(self) -> None:
        pass
