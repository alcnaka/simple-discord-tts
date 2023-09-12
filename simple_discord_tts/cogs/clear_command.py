from datetime import datetime, timedelta
from logging import getLogger
from typing import Self

from discord import TextChannel
from discord.errors import Forbidden
from discord.ext import commands, tasks
from discord.ext.commands import Context
from zoneinfo import ZoneInfo

from simple_discord_tts.app import TTSBot

logger = getLogger(__name__)

JST = ZoneInfo("Asia/Tokyo")


class ClearCog(commands.Cog):
    def __init__(self: Self, bot: TTSBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self: Self) -> None:
        self.auto_clear.start()

    @tasks.loop(minutes=1)
    async def auto_clear(self: Self) -> None:
        await self._clear()

    async def _clear(self: Self, before_minutes: float = 10) -> None:
        """10分以上前のテキストを削除."""
        logger.debug("clear start(offset: %s minutes)", before_minutes)
        channel = self.bot.get_channel(self.bot.listen_channel_id)
        before = datetime.now(JST) - timedelta(minutes=before_minutes)
        two_weeks_ago = datetime.now(JST) - timedelta(days=14)
        if type(channel) == TextChannel:
            msgs = [
                m async for m in channel.history(before=before, after=two_weeks_ago)
            ]
            if len(msgs):
                logger.debug("try to delete messages: %s", len(msgs))
            try:
                await channel.delete_messages(msgs)
            except Forbidden:
                logger.exception("Don't have permission")
        logger.debug("clear end")

    @commands.command()
    async def clear(self: Self, _: Context) -> None:
        logger.debug("command: clear")
        await self._clear()
        logger.debug("command: clear")

    @commands.command()
    async def clear_all(self: Self, _: Context) -> None:
        """全テキストを削除."""
        logger.debug("command: clear_all start")
        await self._clear(before_minutes=0)
        logger.debug("command: clear_all end")
