#!/usr/bin/env python3
"""
予算変換ロジックをデバッグ
"""
import asyncio
from app.api.endpoints.matching import get_matching_parameters

async def debug_budget_conversion():
    """予算変換ロジックをデバッグ"""
    print("=" * 80)
    print("🔍 予算変換ロジックデバッグ")
    print("=" * 80)

    try:
        budget = "1,000万円未満"
        target_segments = "女性20-34歳"
        industry = "ファッション"

        print(f"入力値:")
        print(f"  budget: {budget}")
        print(f"  target_segments: {target_segments}")
        print(f"  industry: {industry}")

        max_budget, target_segment_id, image_item_ids = await get_matching_parameters(
            budget, target_segments, industry
        )

        print(f"\n変換結果:")
        print(f"  max_budget: {max_budget}円")
        print(f"  max_budget / 10000: {max_budget / 10000}万円")
        print(f"  target_segment_id: {target_segment_id}")
        print(f"  image_item_ids: {image_item_ids}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_budget_conversion())