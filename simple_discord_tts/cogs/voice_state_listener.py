from logging import getLogger
from typing import Self

from discord import Member, VoiceChannel, VoiceState
from discord.ext import commands

from simple_discord_tts.app import TTSBot, TTSContext

logger = getLogger(__name__)


class VoiceStateListenerCog(commands.Cog):
    def __init__(self: Self, bot: TTSBot) -> None:
        logger.debug("VoiceStateListenCog is initialized")
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self: Self,
        member: Member,
        before: VoiceState,
        after: VoiceState,
    ) -> None:
        # Botの参加を読み上げないように
        if member.bot:
            return

        # 同一チャンネル内の動作は無視
        if before.channel == after.channel:
            return

        callme = member.display_name

        if after.channel is not None:
            bot_vc = after.channel.guild.voice_client
            if (
                bot_vc
                and after.channel == bot_vc.channel
                and type(after.channel) == VoiceChannel
            ):
                t = f"{callme} が参加しました。"
                logger.debug(t)
                tts_ctx = TTSContext(voice_channel=after.channel, text=t)
                await self.bot.queue.put(tts_ctx)

        if after.channel is None and before.channel is not None:
            bot_vc = before.channel.guild.voice_client
            if (
                bot_vc
                and before.channel == bot_vc.channel
                and type(before.channel) == VoiceChannel
            ):
                t = f"{callme} が切断しました。"
                logger.debug(t)
                tts_ctx = TTSContext(voice_channel=before.channel, text=t)
                await self.bot.queue.put(tts_ctx)

        if before.channel is not None and after.channel is not None:
            bot_vc = before.channel.guild.voice_client
            if (
                bot_vc
                and before.channel == bot_vc.channel
                and type(before.channel) == VoiceChannel
            ):
                t = f"{callme} が移動しました。"
                logger.debug(t)
                tts_ctx = TTSContext(voice_channel=before.channel, text=t)
                await self.bot.queue.put(tts_ctx)
