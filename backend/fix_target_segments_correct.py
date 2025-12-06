#!/usr/bin/env python3
"""ターゲット層マスタを正しい8セグメントに修正（フォーム仕様準拠）"""

import asyncio
import sys
from pathlib import Path

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, delete
from app.db.connection import init_db, get_session_maker
from app.models import TargetSegment

# グローバル変数でセッションメーカーを保持
AsyncSessionLocal = None

async def get_async_session():
    """非同期セッション取得"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

# 正しいターゲット層データ（フォーム仕様準拠 + VRファイル名準拠）
CORRECT_TARGET_SEGMENTS_DATA = [
    # 男性ターゲット
    {
        "id": 1,
        "code": "M1219",
        "name": "男性12-19歳",
        "gender": "男性",
        "age_range": "12-19歳",
        "display_order": 1
    },
    {
        "id": 2,
        "code": "M2034",
        "name": "男性20-34歳",
        "gender": "男性",
        "age_range": "20-34歳",
        "display_order": 2
    },
    {
        "id": 3,
        "code": "M3549",
        "name": "男性35-49歳",
        "gender": "男性",
        "age_range": "35-49歳",
        "display_order": 3
    },
    {
        "id": 4,
        "code": "M5069",
        "name": "男性50-69歳",
        "gender": "男性",
        "age_range": "50-69歳",
        "display_order": 4
    },

    # 女性ターゲット
    {
        "id": 5,
        "code": "F1219",
        "name": "女性12-19歳",
        "gender": "女性",
        "age_range": "12-19歳",
        "display_order": 5
    },
    {
        "id": 6,
        "code": "F2034",
        "name": "女性20-34歳",
        "gender": "女性",
        "age_range": "20-34歳",
        "display_order": 6
    },
    {
        "id": 7,
        "code": "F3549",
        "name": "女性35-49歳",
        "gender": "女性",
        "age_range": "35-49歳",
        "display_order": 7
    },
    {
        "id": 8,
        "code": "F5069",
        "name": "女性50-69歳",
        "gender": "女性",
        "age_range": "50-69歳",
        "display_order": 8
    }
]

async def clear_target_segments():
    """既存のターゲット層データをクリア"""
    print("\n🧹 Clearing existing target_segments data...")

    async with await get_async_session() as session:
        await session.execute(delete(TargetSegment))
        await session.commit()
        print("✅ Target_segments data cleared")

async def seed_correct_target_segments():
    """正しいターゲット層データを投入"""
    print("\n📥 Seeding correct target_segments data (form specification compliant)...")

    async with await get_async_session() as session:
        for segment_data in CORRECT_TARGET_SEGMENTS_DATA:
            segment = TargetSegment(**segment_data)
            session.add(segment)

        await session.commit()
        print(f"✅ Target_segments seeded: {len(CORRECT_TARGET_SEGMENTS_DATA)} records")

        return len(CORRECT_TARGET_SEGMENTS_DATA)

async def verify_seeding():
    """投入結果の検証"""
    print("\n🔍 Verifying correct target_segments data...")

    async with await get_async_session() as session:
        result = await session.execute(select(TargetSegment).order_by(TargetSegment.display_order))
        segments = result.scalars().all()

        print(f"📊 Total target_segments records: {len(segments)}")
        print("📊 Corrected target segments list:")
        for segment in segments:
            print(f"   {segment.id}: {segment.name} ({segment.code}) - {segment.age_range}")

        return len(segments)

async def main():
    """メイン処理"""
    print("=" * 80)
    print("🚀 Correcting target_segments to form specification compliance...")
    print("=" * 80)
    print("📋 Original issue: Mismatch between form choices, VR data, and DB")
    print("🎯 Form specification (correct):")
    for segment_data in CORRECT_TARGET_SEGMENTS_DATA:
        print(f"   - {segment_data['name']} ({segment_data['code']})")
    print("=" * 80)

    try:
        # 既存のターゲット層データクリア
        await clear_target_segments()

        # 正しいターゲット層データ投入
        seeded_count = await seed_correct_target_segments()

        # 投入結果検証
        total_count = await verify_seeding()

        print("\n" + "=" * 80)
        print("✅ Target_segments correction completed successfully!")
        print("=" * 80)
        print(f"📊 Summary:")
        print(f"   - Seeded: {seeded_count} records")
        print(f"   - Verified: {total_count} records")
        print(f"   - Status: ✅ Form specification compliant")
        print("=" * 80)
        print("🚨 Warning: VR/TPR data mapping may need adjustment")
        print("🔄 Next step: Re-import VR data with corrected target mapping")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during correction: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())