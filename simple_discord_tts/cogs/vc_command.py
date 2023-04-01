from datetime import datetime, timedelta
from logging import getLogger

from discord.ext import commands
from discord import Message, TextChannel

from simple_discord_tts.app import TTSBot

logger = getLogger(__name__)

class ControlCommand(commands.Cog):
    def __init__(self, bot: TTSBot) -> None:
        self.bot = bot

    @commands.command()
    async def leave(self, ctx) -> None:
        if vc := self.bot.voice_clients:
            await vc[0].disconnect(force=True)
