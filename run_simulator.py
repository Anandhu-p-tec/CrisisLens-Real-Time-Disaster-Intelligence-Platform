import asyncio
import sys
from app.ingestion.stream_simulator import StreamSimulator
from app.pipeline.processor import CrisisProcessor
from app.core.config import settings

async def run():
    print(f'[Simulator] Starting crisis event stream (speed_factor={settings.SIMULATOR_SPEED_FACTOR})...', file=sys.stderr)
    p = CrisisProcessor()
    s = StreamSimulator(speed_factor=settings.SIMULATOR_SPEED_FACTOR)
    count = 0
    async for post in s.stream():
        await p.process(post)
        count += 1
        if count % 10 == 0:
            print(f'[Simulator] Processed {count} events...', file=sys.stderr)
    print(f'[Simulator] Completed! Total events: {count}', file=sys.stderr)

asyncio.run(run())
