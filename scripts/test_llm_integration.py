import asyncio
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(name)s | %(message)s')

from app.ingestion.schema import RawPostSchema
from app.pipeline.processor import CrisisProcessor
from app.repository.events import fetch_event_by_id


async def test():
    print("=== TESTING LLM INTEGRATION ===")
    p = CrisisProcessor()
    post = RawPostSchema(
        post_id="llm_test_full",
        text="Severe flooding in Wayanad, hundreds trapped at Meppadi bridge, rescue needed urgently",
        platform="simulator",
        created_at=datetime.now(tz=timezone.utc)
    )
    print(f"\n[1] Processing event: {post.post_id}")
    print(f"    Severity threshold: 0.6")
    record = await p.process(post)
    print(f"\n[2] Processing complete")
    print(f"    Severity: {record.severity:.3f}")
    print(f"    Labels: {record.labels}")
    if record.reasoning:
        print(f"    Reasoning: {record.reasoning[:80]}...")
    else:
        print(f"    Reasoning: NONE")
    if record.recommended_action:
        print(f"    Action: {record.recommended_action[:80]}...")
    else:
        print(f"    Action: NONE")
    
    print(f"\n[3] Fetching from database...")
    fetched = await fetch_event_by_id(post.post_id)
    if fetched:
        print(f"    Found in DB: reasoning={'YES' if fetched.reasoning else 'NO'}")
        if fetched.reasoning:
            print(f"    DB reasoning: {fetched.reasoning[:80]}...")
        else:
            print(f"    DB reasoning: NONE")
    else:
        print(f"    NOT FOUND IN DB")
    
    await p.aclose()


if __name__ == "__main__":
    asyncio.run(test())
