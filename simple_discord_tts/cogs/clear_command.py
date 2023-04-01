from datetime import datetime, timedelta
from logging import getLogger

from discord.ext import commands
from discord import Message, TextChannel

from simple_discord_tts.app import TTSBot

logger = getLogger(__name__)

class ClearCog(commands.Cog):
    def __init__(self, bot: TTSBot) -> None:
        self.bot = bot

    @commands.command()
    async def clear(self, ctx) -> None:
        """ListenChannel の10分以上前のテキストを削除"""
        channel = self.bot.get_channel(self.bot.listen_channel_id)
        before = datetime.now() - timedelta(minutes=10)
        if type(channel) == TextChannel:
            msgs = [m async for m in channel.history(before=before)]
            await channel.delete_messages(msgs)

    @commands.command()
    async def clear_all(self, ctx) -> None:
        """ListenChannel の全テキストを削除"""
        channel = self.bot.get_channel(self.bot.listen_channel_id)
        if type(channel) == TextChannel:
            msgs = [m async for m in channel.history()]
            await channel.delete_messages(msgs)
