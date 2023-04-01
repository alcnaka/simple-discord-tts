from logging import getLogger
import asyncio

from discord.ext import commands
from discord import Message, VoiceChannel
import discord
from pydantic import BaseModel, validator

from .settings import settings

logger = getLogger(__name__)


class TTSContext(BaseModel):
    voice_channel: VoiceChannel
    text: str

    class Config:
        arbitrary_types_allowed = True


class TTSBot(commands.Bot):

    def __init__(self, command_prefix: str, intents: discord.Intents) -> None:
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.queue: asyncio.Queue[TTSContext] = asyncio.Queue()
        self.listen_channel_id = settings.LISTEN_CHANNEL_ID

        self.max_tts_len = 50

    def flush_queue(self) -> None:
        self.queue: asyncio.Queue[TTSContext] = asyncio.Queue()

    async def on_ready(self) -> None:
        logger.info('------')
        logger.info('Logged in as')
        if self.user:
            logger.info('NAME: ' + self.user.name)
            logger.info('ID: ' + str(self.user.id))
        if (channel := self.get_channel(settings.LISTEN_CHANNEL_ID)) and (isinstance(channel, discord.abc.GuildChannel)):
            logger.info("ListenChannel: " + channel.name)
        logger.info('------')

    def is_tts_message(self, message: Message) -> bool:
        """無視するメッセージを定義"""
        if message.author == self.user:
            return False
        if message.channel.id != self.listen_channel_id:
            return False
        if len(message.content) > self.max_tts_len:
            return False
        if message.mentions:
            return False
        return True

    async def on_message(self, message: Message, ) -> None:
        """キュー入れとか"""
        if not self.is_tts_message(message):
            return

        if message.content.startswith(self.command_prefix):  # type: ignore
            # コマンドの実行に回す
            return await super().on_message(message)

        # VCに参加しているユーザーか
        if not (type(message.author) == discord.Member
                and message.author.voice
                and (voice_channel := message.author.voice.channel)
                and type(voice_channel) == VoiceChannel
        ):
            await message.reply('VCに参加してね')
            return

        ctx = TTSContext(voice_channel = voice_channel, text = message.clean_content)
        await self.queue.put(ctx)
        print(self.queue.qsize())
