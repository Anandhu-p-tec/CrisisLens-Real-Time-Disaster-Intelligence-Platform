from __future__ import annotations

import asyncio
import logging
import statistics
import time

from app.core.logging import configure_logging
from app.ingestion.stream_simulator import StreamSimulator
from app.pipeline.processor import CrisisProcessor

N_SAMPLES = 20


async def main() -> None:
    configure_logging()
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    processor = CrisisProcessor()
    simulator = StreamSimulator(speed_factor=1000.0)
    latencies: list[float] = []
    print(f"Benchmarking pipeline over {N_SAMPLES} posts...")
    async for post in simulator.stream():
        start = time.perf_counter()
        try:
            await processor.process(post)
        except Exception as exc:
            print(f"  Error on {post.post_id}: {exc}")
        elapsed = time.perf_counter() - start
        latencies.append(elapsed)
        print(f"  [{len(latencies)}/{N_SAMPLES}] {post.post_id} — {elapsed:.3f}s")
        if len(latencies) >= N_SAMPLES:
            break
    await processor.aclose()
    print("\n=== Latency Report ===")
    print(f"  Mean:   {statistics.mean(latencies):.3f}s")
    print(f"  Median: {statistics.median(latencies):.3f}s")
    print(f"  P95:    {sorted(latencies)[int(0.95 * len(latencies))]:.3f}s")
    print(f"  Min:    {min(latencies):.3f}s")
    print(f"  Max:    {max(latencies):.3f}s")


if __name__ == "__main__":
    asyncio.run(main())
