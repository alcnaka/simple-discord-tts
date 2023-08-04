import discord
import asyncio
import logging

from .cogs import all_cogs
from .app import TTSBot
from .settings import settings


async def prepare_bot() -> TTSBot:
    intents = discord.Intents.all()
    bot = TTSBot(
        command_prefix = '&',
        intents = intents,
    )
    for cog in all_cogs:
        await bot.add_cog(cog(bot))
    return bot

def main() -> None:

    bot = asyncio.run(prepare_bot())
    bot.run(token = settings.DISCORD_TOKEN, )


def setup_logger() -> None:
    logger = logging.getLogger('simple_discord_tts')
    logger.setLevel(logging.INFO)

if __name__ == "__main__":
    import logging
    # logging.basicConfig(level=logging.INFO)
    main()
