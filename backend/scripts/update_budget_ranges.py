#!/usr/bin/env python3
"""
安全に予算区分のみを更新するスクリプト
DELETE操作は行わず、UPDATEのみでCASCADE削除を避ける
"""
import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.connection import init_db, get_session_maker


async def update_budget_ranges_only():
    """予算区分のみを安全に更新（CASCADE削除回避）"""

    # データベース接続
    await init_db()
    AsyncSessionLocal = get_session_maker()

    async with AsyncSessionLocal() as session:
        try:
            print("🚀 予算区分の安全更新開始...")

            # 既存の予算区分を個別にUPDATE（DELETE使用回避）
            await session.execute(text(
                "UPDATE budget_ranges SET name = '3,000万円～1億円未満', max_amount = 100000000 WHERE id = 3"
            ))
            await session.execute(text(
                "UPDATE budget_ranges SET name = '1億円以上', min_amount = 100000000 WHERE id = 4"
            ))

            await session.commit()
            print("✅ 予算区分更新完了:")
            print("  - ID 3: 3,000万円～1億円未満 (30,000,000 - 100,000,000)")
            print("  - ID 4: 1億円以上 (100,000,000 - NULL)")

        except Exception as e:
            await session.rollback()
            print(f"❌ エラー: {str(e)}")
            raise
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(update_budget_ranges_only())