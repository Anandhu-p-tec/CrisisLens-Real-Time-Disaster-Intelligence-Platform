import asyncio
import sys
import traceback
from app.ingestion.stream_simulator import StreamSimulator
from app.pipeline.processor import CrisisProcessor

async def run():
    print('[Simulator] Starting crisis event stream...', file=sys.stderr)
    p = CrisisProcessor()
    s = StreamSimulator(speed_factor=2.0)
    count = 0
    async for post in s.stream():
        try:
            await p.process(post)
            count += 1
            if count % 3 == 0:
                print(f'[Simulator] ✓ Processed {count} events', file=sys.stderr)
        except Exception as e:
            print(f'[Simulator] Error: {type(e).__name__}: {e}', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            if count >= 5:
                break
    print(f'[Simulator] Completed: {count} events', file=sys.stderr)

asyncio.run(run())
