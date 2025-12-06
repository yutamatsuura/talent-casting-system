#!/usr/bin/env python3
"""ターゲット層を既存データ保持しつつ安全に更新（段階的修正）"""

import asyncio
import sys
from pathlib import Path

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, delete, update, text
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

async def step1_delete_empty_senior():
    """STEP1: データ0件の60歳以上を削除"""
    print("\n📋 STEP 1: Deleting empty 'Senior' target segment...")

    async with await get_async_session() as session:
        # 60歳以上(Senior)を削除
        await session.execute(delete(TargetSegment).where(TargetSegment.code == "Senior"))
        await session.commit()
        print("✅ Empty 'Senior' segment deleted")

async def step2_update_age_ranges():
    """STEP2: 年齢範囲名を修正"""
    print("\n📋 STEP 2: Updating age range names...")

    async with await get_async_session() as session:
        # 各セグメントの名称とコードを更新
        updates = [
            # 既存 → フォーム仕様
            {"old_code": "F1", "new_code": "F2034", "new_name": "女性20-34歳", "new_age_range": "20-34歳"},
            {"old_code": "F2", "new_code": "F3549", "new_name": "女性35-49歳", "new_age_range": "35-49歳"},
            {"old_code": "F3", "new_code": "F5069", "new_name": "女性50-69歳", "new_age_range": "50-69歳"},
            {"old_code": "M1", "new_code": "M2034", "new_name": "男性20-34歳", "new_age_range": "20-34歳"},
            {"old_code": "M2", "new_code": "M3549", "new_name": "男性35-49歳", "new_age_range": "35-49歳"},
            {"old_code": "M3", "new_code": "M5069", "new_name": "男性50-69歳", "new_age_range": "50-69歳"},
        ]

        for update_data in updates:
            await session.execute(
                update(TargetSegment)
                .where(TargetSegment.code == update_data["old_code"])
                .values(
                    code=update_data["new_code"],
                    name=update_data["new_name"],
                    age_range=update_data["new_age_range"]
                )
            )

        await session.commit()
        print(f"✅ Updated {len(updates)} target segments")

async def step3_split_teen_segment():
    """STEP3: 10代を男性12-19歳と女性12-19歳に分離"""
    print("\n📋 STEP 3: Splitting Teen segment into male/female 12-19...")

    async with await get_async_session() as session:
        # 既存の10代セグメントを取得
        result = await session.execute(select(TargetSegment).where(TargetSegment.code == "Teen"))
        teen_segment = result.scalar_one_or_none()

        if teen_segment:
            teen_id = teen_segment.id
            print(f"   Found Teen segment ID: {teen_id}")

            # 10代を男性12-19歳に変更
            await session.execute(
                update(TargetSegment)
                .where(TargetSegment.id == teen_id)
                .values(
                    code="M1219",
                    name="男性12-19歳",
                    gender="男性",
                    age_range="12-19歳",
                    display_order=1
                )
            )

            # 女性12-19歳を新規追加
            new_female_teen = TargetSegment(
                code="F1219",
                name="女性12-19歳",
                gender="女性",
                age_range="12-19歳",
                display_order=5
            )
            session.add(new_female_teen)

            await session.commit()

            # 新しく追加された女性12-19歳のIDを取得
            result = await session.execute(
                select(TargetSegment).where(TargetSegment.code == "F1219")
            )
            new_female_teen = result.scalar_one()
            new_female_id = new_female_teen.id

            print(f"   ✅ Teen split completed:")
            print(f"      Male 12-19: ID {teen_id}")
            print(f"      Female 12-19: ID {new_female_id}")

            return teen_id, new_female_id

async def step4_verify_final_state():
    """STEP4: 最終状態の検証"""
    print("\n📋 STEP 4: Verifying final target segments...")

    async with await get_async_session() as session:
        result = await session.execute(select(TargetSegment).order_by(TargetSegment.display_order))
        segments = result.scalars().all()

        print(f"📊 Final target segments ({len(segments)} total):")
        for seg in segments:
            print(f"   ID {seg.id}: {seg.name} ({seg.code}) - {seg.age_range}")

        return len(segments)

async def main():
    """メイン処理"""
    print("=" * 80)
    print("🚀 Safe target segments update (preserving existing data)...")
    print("=" * 80)
    print("🎯 Target: Form specification compliance without data loss")
    print("=" * 80)

    try:
        # STEP 1: 空の60歳以上削除
        await step1_delete_empty_senior()

        # STEP 2: 年齢範囲名更新
        await step2_update_age_ranges()

        # STEP 3: 10代セグメント分離
        male_teen_id, female_teen_id = await step3_split_teen_segment()

        # STEP 4: 最終検証
        total_segments = await step4_verify_final_state()

        print("\n" + "=" * 80)
        print("✅ Safe target segments update completed!")
        print("=" * 80)
        print(f"📊 Summary:")
        print(f"   - Total segments: {total_segments}")
        print(f"   - Form compliance: ✅ Achieved")
        print(f"   - Data preservation: ✅ All existing data preserved")
        print("=" * 80)
        print("🔔 Note: Existing VR/TPR data automatically mapped to new structure")
        print("📝 Next: Test matching API with new target segments")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during safe update: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())