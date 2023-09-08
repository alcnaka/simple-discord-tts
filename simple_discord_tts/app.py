import asyncio
from logging import getLogger
from typing import Self

import discord
from discord import Message, VoiceChannel
from discord.ext import commands
from pydantic import BaseModel, ConfigDict

from .settings import settings
from .text import clean_text

logger = getLogger(__name__)


class TTSContext(BaseModel):
    voice_channel: VoiceChannel
    text: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


class TTSBot(commands.Bot):
    def __init__(self: Self, command_prefix: str, intents: discord.Intents) -> None:
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.queue: asyncio.Queue[TTSContext] = asyncio.Queue()
        self.listen_channel_id = settings.LISTEN_CHANNEL_ID

        self.max_tts_len = 50

    def flush_queue(self: Self) -> None:
        self.queue: asyncio.Queue[TTSContext] = asyncio.Queue()

    async def on_ready(self: Self) -> None:
        logger.info("------")
        logger.info("Logged in as")
        if self.user:
            logger.info("NAME: " + self.user.name)
            logger.info("ID: " + str(self.user.id))
        if (channel := self.get_channel(settings.LISTEN_CHANNEL_ID)) and (
            isinstance(channel, discord.abc.GuildChannel)
        ):
            logger.info("ListenChannel: " + channel.name)
        logger.info("------")

    def is_tts_message(self: Self, message: Message) -> bool:
        """無視するメッセージを定義."""
        if message.author == self.user:
            return False
        if message.channel.id != self.listen_channel_id:
            return False
        if len(message.content) > self.max_tts_len:
            return False
        if message.mentions:
            return False
        return True

    async def on_message(
        self: Self,
        message: Message,
    ) -> None:
        """キュー入れとか."""
        if not self.is_tts_message(message):
            return None

        if message.content.startswith(
            self.command_prefix,  # type: ignore[reportGeneralTypeIssues]
        ):
            # コマンドの実行に回す
            return await super().on_message(message)

        # VCに参加しているユーザーか
        if not (
            type(message.author) == discord.Member
            and message.author.voice
            and (voice_channel := message.author.voice.channel)
            and type(voice_channel) == VoiceChannel
        ):
            await message.reply("VCに参加してね")
            return None

        cleaned_text = clean_text(message.clean_content)

        if len(cleaned_text) == 0:
            return None

        ctx = TTSContext(voice_channel=voice_channel, text=cleaned_text)
        await self.queue.put(ctx)
        print(self.queue.qsize())
        return None
