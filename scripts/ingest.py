from __future__ import annotations
import asyncio
import argparse
import logging
from app.core.logging import configure_logging
from app.ingestion.stream_simulator import StreamSimulator
from app.pipeline.processor import CrisisProcessor


async def run(n_events: int, speed_factor: float) -> None:
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting ingestion: n_events=%d speed_factor=%.1f", n_events, speed_factor)
    processor = CrisisProcessor()
    simulator = StreamSimulator(speed_factor=speed_factor)
    count = 0
    async for post in simulator.stream():
        record = await processor.process(post)
        count += 1
        logger.info(
            "[%d/%d] post=%s labels=%s severity=%.2f location=%s",
            count,
            n_events,
            record.post_id,
            record.labels,
            record.severity,
            record.location_raw or "unresolved",
        )
        if count >= n_events:
            break
    await processor.aclose()
    logger.info("Ingestion complete. %d events processed.", count)


def main() -> None:
    parser = argparse.ArgumentParser(description="CrisisLens event ingestion runner")
    parser.add_argument("--events", type=int, default=50, help="Number of events to ingest")
    parser.add_argument("--speed", type=float, default=2.0, help="Simulator speed factor")
    args = parser.parse_args()
    asyncio.run(run(n_events=args.events, speed_factor=args.speed))


if __name__ == "__main__":
    main()
