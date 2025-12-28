#!/usr/bin/env python3
"""予算区分マスタデータの作成・投入"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv('/Users/lennon/projects/talent-casting-form/.env.local')

async def insert_budget_ranges():
    """予算区分マスタデータを投入"""
    database_url = os.getenv('DATABASE_URL')

    # 新しい予算区分データ（フロントエンドと完全一致）
    budget_data = [
        {"range_name": "500万円以下", "min_amount": 0, "max_amount": 5000000},
        {"range_name": "500万円〜1,000万円", "min_amount": 5000001, "max_amount": 10000000},
        {"range_name": "1,000万円〜3,000万円", "min_amount": 10000001, "max_amount": 30000000},
        {"range_name": "3,000万円〜5,000万円", "min_amount": 30000001, "max_amount": 50000000},
        {"range_name": "5,000万円〜1億円", "min_amount": 50000001, "max_amount": 100000000},
        {"range_name": "1億円以上", "min_amount": 100000001, "max_amount": None},
    ]

    print(f"🔗 データベース接続中...")

    try:
        conn = await asyncpg.connect(database_url)
        print("✅ データベース接続成功")

        # 既存データの確認
        existing_count = await conn.fetchval("SELECT COUNT(*) FROM budget_ranges")
        print(f"📊 現在の予算区分件数: {existing_count}件")

        if existing_count > 0:
            print("⚠️  既存データがあります。削除してから投入しますか？")

            # 既存データを削除
            await conn.execute("DELETE FROM budget_ranges")
            print("🗑️  既存データを削除しました")

        # 新しいデータを投入
        print("\n📥 予算区分データを投入中...")

        for budget in budget_data:
            await conn.execute("""
                INSERT INTO budget_ranges (range_name, min_amount, max_amount)
                VALUES ($1, $2, $3)
            """, budget["range_name"], budget["min_amount"], budget["max_amount"])

            print(f"  ✅ {budget['range_name']} (¥{budget['min_amount']:,} - {f'¥{budget['max_amount']:,}' if budget['max_amount'] else '上限なし'})")

        # 投入結果を確認
        final_count = await conn.fetchval("SELECT COUNT(*) FROM budget_ranges")
        print(f"\n📊 投入完了: {final_count}件")

        # テスト用予算区分の確認
        claude_budget = "1,000万円〜3,000万円"
        found = await conn.fetchrow(
            "SELECT * FROM budget_ranges WHERE range_name = $1", claude_budget
        )

        if found:
            print(f"✅ CLAUDE.md記載の予算区分 '{claude_budget}' が正常に投入されました")
            print(f"   金額範囲: ¥{int(found['min_amount']):,} - ¥{int(found['max_amount']):,}")
        else:
            print(f"❌ 予算区分 '{claude_budget}' の投入に失敗しました")

        await conn.close()
        print("\n✅ 予算区分マスタデータの投入が完了しました")

    except Exception as e:
        print(f"❌ エラー発生: {str(e)}")

if __name__ == "__main__":
    asyncio.run(insert_budget_ranges())