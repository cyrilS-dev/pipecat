import argparse
import asyncio
import os
import sys

import aiohttp
from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli
from loguru import logger

from pipecat.frames.frames import TextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.transports.services.livekit import LiveKitParams, LiveKitTransport

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

async def job_entrypoint(ctx: JobContext):
    async with aiohttp.ClientSession() as session:
        await ctx.connect()
        transport = LiveKitTransport(
            ctx.room, params=LiveKitParams(audio_out_enabled=True, audio_out_sample_rate=16000)
        )

        tts = CartesiaTTSService(
            api_key=os.getenv("CARTESIA_API_KEY"),
            voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",  # British Lady
        )

        runner = PipelineRunner()

        task = PipelineTask(Pipeline([tts, transport.output()]))

        await task.queue_frame(TextFrame("Hello there! How are you doing today? Would you like to talk about the weather?"))

        await runner.run(task)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(entrypoint_fnc=job_entrypoint)
    )