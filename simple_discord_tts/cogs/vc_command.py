from logging import getLogger
from typing import Self

from discord.ext import commands
from discord.ext.commands import Context

from simple_discord_tts.app import TTSBot

logger = getLogger(__name__)


class ControlCommand(commands.Cog):
    def __init__(self: Self, bot: TTSBot) -> None:
        self.bot = bot

    @commands.command()
    async def leave(self: Self, _: Context) -> None:
        if vc := self.bot.voice_clients:
            self.bot.flush_queue()
            await vc[0].disconnect(force=True)
