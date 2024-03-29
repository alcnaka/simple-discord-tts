import asyncio
from logging import getLogger
from typing import Self

import discord
from discord import Message, VoiceChannel
from discord.ext import commands
from pydantic import BaseModel, ConfigDict

from .attachment import extract_filetypes
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
            logger.info("NAME: %s", self.user.name)
            logger.info("ID: %s", str(self.user.id))
        if (channel := self.get_channel(settings.LISTEN_CHANNEL_ID)) and (
            isinstance(channel, discord.abc.GuildChannel)
        ):
            logger.info("ListenChannel: %s", channel.name)
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

        # 絵文字等を除いたテキストを取得
        cleaned_text = clean_text(message.clean_content)

        # 添付ファイルから読み上げ内容を取得
        attachment_text = extract_filetypes([a.filename for a in message.attachments])

        tts_text = cleaned_text + attachment_text

        # 読み上げる中身が無いときは何もしない
        if len(tts_text) == 0:
            logger.debug("empty message")
            return None

        ctx = TTSContext(voice_channel=voice_channel, text=tts_text)
        logger.debug("queing: %s", str(ctx))
        await self.queue.put(ctx)
        logger.debug("queued (qsize: %s)", self.queue.qsize)
        return None
