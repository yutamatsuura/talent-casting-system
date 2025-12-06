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

    # CLAUDE.mdに基づいた予算区分データ
    budget_data = [
        {"name": "100万円未満", "min_amount": 0, "max_amount": 999999, "display_order": 1},
        {"name": "100万円～500万円未満", "min_amount": 1000000, "max_amount": 4999999, "display_order": 2},
        {"name": "500万円～1,000万円未満", "min_amount": 5000000, "max_amount": 9999999, "display_order": 3},
        {"name": "1,000万円～3,000万円未満", "min_amount": 10000000, "max_amount": 29999999, "display_order": 4},  # CLAUDE.mdのテスト予算
        {"name": "3,000万円～5,000万円未満", "min_amount": 30000000, "max_amount": 49999999, "display_order": 5},
        {"name": "5,000万円～1億円未満", "min_amount": 50000000, "max_amount": 99999999, "display_order": 6},
        {"name": "1億円以上", "min_amount": 100000000, "max_amount": None, "display_order": 7},
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
                INSERT INTO budget_ranges (name, min_amount, max_amount, display_order)
                VALUES ($1, $2, $3, $4)
            """, budget["name"], budget["min_amount"], budget["max_amount"], budget["display_order"])

            print(f"  ✅ {budget['name']} (¥{budget['min_amount']:,} - {f'¥{budget['max_amount']:,}' if budget['max_amount'] else '上限なし'})")

        # 投入結果を確認
        final_count = await conn.fetchval("SELECT COUNT(*) FROM budget_ranges")
        print(f"\n📊 投入完了: {final_count}件")

        # テスト用予算区分の確認
        claude_budget = "1,000万円～3,000万円未満"
        found = await conn.fetchrow(
            "SELECT * FROM budget_ranges WHERE name = $1", claude_budget
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