from __future__ import annotations

import asyncio
import logging

from app.core.logging import configure_logging
from app.repository.events import fetch_events
from app.reasoning.rag_retriever import RAGRetriever


async def main() -> None:
    configure_logging()
    logger = logging.getLogger(__name__)
    retriever = RAGRetriever()
    events = await fetch_events(limit=10000)
    if not events:
        logger.info("No events in database. Run the pipeline first.")
        return
    for event in events:
        retriever.add(post_id=event.post_id, text=event.text)
    retriever.persist()
    logger.info("FAISS index built with %d vectors", len(events))


if __name__ == "__main__":
    asyncio.run(main())
