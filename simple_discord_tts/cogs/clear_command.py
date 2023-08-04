from datetime import datetime, timedelta
from logging import getLogger

from discord.ext import commands, tasks
from discord import Message, TextChannel

from simple_discord_tts.app import TTSBot

logger = getLogger(__name__)

class ClearCog(commands.Cog):
    def __init__(self, bot: TTSBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.auto_clear.start()

    @tasks.loop(minutes=1)
    async def auto_clear(self) -> None:
        await self._clear()

    async def _clear(self) -> None:
        """10分以上前のテキストを削除"""
        logger.debug('clear start')
        channel = self.bot.get_channel(self.bot.listen_channel_id)
        before = datetime.now() - timedelta(minutes=10)
        if type(channel) == TextChannel:
            msgs = [m async for m in channel.history(before=before)]
            if len(msgs):
                logger.debug(f'try to delete messages: {len(msgs)}')
            await channel.delete_messages(msgs)
        logger.debug('clear end')

    @commands.command()
    async def clear(self, ctx) -> None:
        logger.debug('command: clear')
        await self._clear()
        logger.debug('command: clear')

    @commands.command()
    async def clear_all(self, ctx) -> None:
        """全テキストを削除"""
        logger.debug('command: clear_all start')
        channel = self.bot.get_channel(self.bot.listen_channel_id)
        two_weeks_ago = datetime.now() - timedelta(days=14)
        if type(channel) == TextChannel:
            try:
                msgs = [m async for m in channel.history(after=two_weeks_ago)]
                logger.debug(f'try to delete messages: {len(msgs)}')
                await channel.delete_messages(msgs)
            except Exception:
                logger.exception('メッセージの削除中に例外が発生しました。')
            # TODO: レートリミットに引っかかる
            # [await m.delete() async for m in channel.history()]
        logger.debug('command: clear_all end')
