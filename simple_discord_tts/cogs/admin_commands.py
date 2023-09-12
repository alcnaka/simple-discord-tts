import sys
from logging import getLogger
from typing import Never, Self

from discord import Member
from discord.ext import commands
from discord.ext.commands import Cog, CommandError, Context

logger = getLogger(__name__)


class AdminCommands(Cog):
    """管理者用コマンド."""

    async def cog_check(self: Self, ctx: Context) -> bool:
        """Guildの管理者かどうかをチェック."""
        author = ctx.author
        if type(author) == Member:
            return author.guild_permissions.administrator
        return False

    async def cog_command_error(self: Self, ctx: Context, _error: CommandError) -> None:
        """管理者以外が実行した際は返信."""
        await ctx.reply("管理者用コマンドです。")

    @commands.command()
    async def restart(self: Self, ctx: Context) -> Never:
        """再起動用コマンド.

        終了コード1で返すだけなので、上位側で適切に再起動設定が必要
        """
        logger.debug("command: restart ignited")
        await ctx.reply("再起動します")
        sys.exit(1)
