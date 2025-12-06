#!/usr/bin/env python3
"""
基本マスターデータシーディング（予算・ターゲット層のみ）
"""
import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.connection import init_db, get_session_maker
from app.models import Base, TargetSegment, BudgetRange


async def seed_basic_master_data():
    """基本マスターデータ（予算・ターゲット層）をシーディング"""

    # データベース接続（既存の方法を使用）
    await init_db()
    AsyncSessionLocal = get_session_maker()

    async with AsyncSessionLocal() as session:
        try:
            print("🚀 基本マスターデータシーディング開始...")

            # 既存データクリア（ターゲット層・予算のみ）
            await session.execute(text("DELETE FROM target_segments"))
            await session.execute(text("DELETE FROM budget_ranges"))

            # ターゲット層データ
            target_segments = [
                TargetSegment(id=1, code="M1", name="男性12-19歳", gender="男性", age_range="12-19", display_order=1),
                TargetSegment(id=2, code="F1", name="女性12-19歳", gender="女性", age_range="12-19", display_order=2),
                TargetSegment(id=3, code="M2", name="男性20-34歳", gender="男性", age_range="20-34", display_order=3),
                TargetSegment(id=4, code="F2", name="女性20-34歳", gender="女性", age_range="20-34", display_order=4),
                TargetSegment(id=5, code="M3", name="男性35-49歳", gender="男性", age_range="35-49", display_order=5),
                TargetSegment(id=6, code="F3", name="女性35-49歳", gender="女性", age_range="35-49", display_order=6),
                TargetSegment(id=7, code="M4", name="男性50-69歳", gender="男性", age_range="50-69", display_order=7),
                TargetSegment(id=8, code="F4", name="女性50-69歳", gender="女性", age_range="50-69", display_order=8),
            ]
            session.add_all(target_segments)
            await session.flush()
            print(f"✅ Target segments: {len(target_segments)} 件")

            # 予算データ
            budget_ranges = [
                BudgetRange(id=1, name="1,000万円未満", min_amount=0, max_amount=10000000, display_order=1),
                BudgetRange(id=2, name="1,000万円～3,000万円未満", min_amount=10000000, max_amount=30000000, display_order=2),
                BudgetRange(id=3, name="3,000万円～1億円未満", min_amount=30000000, max_amount=100000000, display_order=3),
                BudgetRange(id=4, name="1億円以上", min_amount=100000000, max_amount=None, display_order=4),
            ]
            session.add_all(budget_ranges)
            await session.flush()
            print(f"✅ Budget ranges: {len(budget_ranges)} 件")

            # コミット
            await session.commit()
            print("🎯 基本マスターデータシーディング完了")

        except Exception as e:
            await session.rollback()
            print(f"❌ エラー: {str(e)}")
            raise
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(seed_basic_master_data())