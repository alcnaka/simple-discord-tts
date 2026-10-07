import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import discord

from simple_discord_tts.app import TTSBot
from simple_discord_tts.cogs.read_queue_task import ReadQueueCog
from simple_discord_tts.exceptions import TTSInvalidRequest


class TestQueue(unittest.IsolatedAsyncioTestCase):
    async def test_flush_drains_existing_queue(self):
        bot = TTSBot(command_prefix="&", intents=discord.Intents.none())
        queue = bot.queue
        await queue.put("first")
        await queue.put("second")

        bot.flush_queue()

        self.assertIs(bot.queue, queue)
        self.assertTrue(queue.empty())
        await asyncio.wait_for(queue.join(), timeout=0.1)
        await queue.put("next")
        self.assertEqual(await queue.get(), "next")
        queue.task_done()
        await bot.close()

    async def test_waiting_consumer_receives_job_after_flush(self):
        bot = TTSBot(command_prefix="&", intents=discord.Intents.none())
        queue = bot.queue
        waiting_get = asyncio.create_task(queue.get())
        await asyncio.sleep(0)

        bot.flush_queue()
        await bot.queue.put("new job")

        self.assertEqual(await asyncio.wait_for(waiting_get, timeout=0.1), "new job")
        queue.task_done()
        await bot.close()

    async def test_voice_timeout_skips_job_and_next_job_can_be_read(self):
        channel = SimpleNamespace(id=2, guild=SimpleNamespace(id=1, voice_client=None))
        channel.connect = AsyncMock(side_effect=TimeoutError("handshake"))
        bot = SimpleNamespace(queue=asyncio.Queue())
        cog = ReadQueueCog(bot)
        await bot.queue.put(SimpleNamespace(voice_channel=channel, text="first"))
        await bot.queue.put(SimpleNamespace(voice_channel=channel, text="second"))

        await cog.read_queue.coro(cog)
        await cog.read_queue.coro(cog)

        self.assertEqual(channel.connect.await_count, 2)
        self.assertTrue(bot.queue.empty())
        await asyncio.wait_for(bot.queue.join(), timeout=0.1)

    async def test_invalid_tts_does_not_write_wav_or_stop_consumer(self):
        channel = SimpleNamespace(id=2, guild=SimpleNamespace(id=1))
        bot = SimpleNamespace(queue=asyncio.Queue())
        cog = ReadQueueCog(bot)
        await bot.queue.put(SimpleNamespace(voice_channel=channel, text="!!!"))
        await bot.queue.put(SimpleNamespace(voice_channel=channel, text="???"))

        with (
            patch.object(cog, "_voice_client", new=AsyncMock(return_value=object())),
            patch("simple_discord_tts.cogs.read_queue_task.VoiceClient", object),
            patch("simple_discord_tts.cogs.read_queue_task.tts", new=AsyncMock(side_effect=TTSInvalidRequest)),
            patch("simple_discord_tts.cogs.read_queue_task.NamedTemporaryFile") as temp_file,
        ):
            await cog.read_queue.coro(cog)
            await cog.read_queue.coro(cog)

        temp_file.assert_not_called()
        await asyncio.wait_for(bot.queue.join(), timeout=0.1)
