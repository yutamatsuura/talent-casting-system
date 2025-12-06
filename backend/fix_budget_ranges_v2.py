#!/usr/bin/env python3
"""
予算区分マスタ修正スクリプト v2
7カテゴリ → 4カテゴリに修正（要件仕様書準拠）
Noneハンドリング対応
"""

import asyncio
import asyncpg
import os
import sys

# データベース接続URL
DATABASE_URL = "postgresql://neondb_owner:npg_9fvZtIKj3gHe@ep-wild-art-a1dq56d3-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

async def fix_budget_ranges():
    """予算区分マスタの修正（4カテゴリに統一）"""
    print("🚀 予算区分マスタ修正開始...")

    try:
        # データベース接続
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ データベース接続成功")

        # 現在のデータを確認
        current_data = await conn.fetch('''
            SELECT id, name, min_amount, max_amount, display_order
            FROM budget_ranges
            ORDER BY display_order
        ''')

        print(f"\n📋 現在の予算区分データ（{len(current_data)}件）:")
        print("-" * 80)
        for row in current_data:
            min_val = row['min_amount'] if row['min_amount'] is not None else 0
            max_val = row['max_amount'] if row['max_amount'] is not None else "無制限"

            if max_val == "無制限":
                print(f"{row['display_order']}. {row['name']} ({min_val:,}円 ～ {max_val})")
            else:
                print(f"{row['display_order']}. {row['name']} ({min_val:,}円 ～ {max_val:,}円)")

        # 全データクリア
        await conn.execute('DELETE FROM budget_ranges')
        print("\n✅ 既存データクリア完了")

        # 4つの正しい予算区分（要件仕様書準拠）
        correct_budget_ranges = [
            ('300万円未満', 0, 2999999, 1),
            ('300万円～1,000万円未満', 3000000, 9999999, 2),
            ('1,000万円～3,000万円未満', 10000000, 29999999, 3),
            ('3,000万円以上', 30000000, 999999999, 4)
        ]

        # データ挿入
        for name, min_amount, max_amount, order in correct_budget_ranges:
            await conn.execute('''
                INSERT INTO budget_ranges (name, min_amount, max_amount, display_order)
                VALUES ($1, $2, $3, $4)
            ''', name, min_amount, max_amount, order)

        print(f"✅ {len(correct_budget_ranges)}件の正しいデータ挿入完了")

        # 検証
        result = await conn.fetch('''
            SELECT id, name, min_amount, max_amount, display_order
            FROM budget_ranges
            ORDER BY display_order
        ''')

        print("\n📋 修正後の予算区分マスタデータ一覧:")
        print("-" * 80)
        for row in result:
            min_str = f"{row['min_amount']:,}円"

            if row['max_amount'] >= 999999999:
                max_str = "以上"
            else:
                max_str = f"{row['max_amount']:,}円"

            print(f"{row['display_order']}. {row['name']} (ID: {row['id']}) - {min_str} ～ {max_str}")

        print(f"\n✅ 予算区分マスタ修正完了（合計: {len(result)}件）")

        if len(result) == 4:
            print("✅ 予算区分数が要件の4カテゴリと一致しました")
        else:
            print(f"❌ 予算区分数が要件と不一致です（期待値: 4、実際: {len(result)}）")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        try:
            await conn.close()
            print("✅ データベース接続終了")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(fix_budget_ranges())