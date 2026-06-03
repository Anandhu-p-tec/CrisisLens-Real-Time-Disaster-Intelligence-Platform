import asyncio
import sys
from app.ingestion.stream_simulator import StreamSimulator
from app.pipeline.processor import CrisisProcessor
from app.core.config import settings

async def run():
    print(f'[Simulator] Starting crisis event stream (speed_factor=3.0)...', file=sys.stderr)
    p = CrisisProcessor()
    s = StreamSimulator(speed_factor=3.0)
    count = 0
    async for post in s.stream():
        try:
            await p.process(post)
            count += 1
            if count % 5 == 0:
                print(f'[Simulator] Processed {count} events...', file=sys.stderr)
        except Exception as e:
            print(f'[Simulator] Error processing event {count+1}: {e}', file=sys.stderr)
    print(f'[Simulator] Completed! Total events: {count}', file=sys.stderr)

try:
    asyncio.run(run())
except KeyboardInterrupt:
    print('[Simulator] Interrupted', file=sys.stderr)
except Exception as e:
    print(f'[Simulator] Fatal error: {e}', file=sys.stderr)
