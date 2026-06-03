#!/usr/bin/env python
"""Debug LLM integration in pipeline."""
import asyncio
import logging
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s | %(name)s | %(message)s'
)

from app.ingestion.schema import RawPostSchema
from app.pipeline.processor import CrisisProcessor

async def main():
    print("=" * 70)
    print("DEBUGGING LLM INTEGRATION")
    print("=" * 70)
    
    print("\n[1/3] Creating processor...")
    try:
        processor = CrisisProcessor()
        print("✓ Processor created")
    except Exception as e:
        print(f"✗ Failed to create processor: {e}")
        return
    
    print("\n[2/3] Creating test post...")
    post = RawPostSchema(
        post_id="llm_debug_001",
        text="Severe flooding in Wayanad, Kerala. Hundreds of families stranded on rooftops. Rescue teams urgently needed.",
        platform="simulator",
        created_at=datetime.now(tz=timezone.utc),
    )
    print(f"✓ Post created: {post.post_id}")
    
    print("\n[3/3] Processing through pipeline...")
    try:
        record = await processor.process(post)
        print(f"✓ Event processed")
        print(f"\n  severity: {record.severity:.3f}")
        print(f"  labels: {record.labels}")
        print(f"  reasoning: {record.reasoning[:100] if record.reasoning else 'NULL'}")
        print(f"  action: {record.recommended_action[:100] if record.recommended_action else 'NULL'}")
        print(f"  human_override: {record.human_override}")
    except Exception as e:
        print(f"✗ Failed to process: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await processor.aclose()
        print("\n✓ Processor closed")

if __name__ == "__main__":
    asyncio.run(main())
