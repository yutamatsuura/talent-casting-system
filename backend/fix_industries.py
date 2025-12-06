#!/usr/bin/env python3
"""
業種マスタ修正スクリプト
要件仕様書の正確な20カテゴリに修正
"""

import asyncio
import asyncpg
import os
import sys

# データベース接続URL
DATABASE_URL = "postgresql://neondb_owner:npg_9fvZtIKj3gHe@ep-wild-art-a1dq56d3-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

async def fix_industries():
    """業種マスタの修正（要件仕様書準拠の20カテゴリ）"""
    print("🚀 業種マスタ修正開始...")

    try:
        # データベース接続
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ データベース接続成功")

        # 現在のデータを確認
        current_data = await conn.fetch('''
            SELECT id, name, display_order FROM industries ORDER BY display_order
        ''')

        print(f"\n📋 現在の業種データ（{len(current_data)}件）:")
        print("-" * 80)
        for row in current_data:
            print(f"{row['display_order']}. {row['name']} (ID: {row['id']})")

        # 全データクリア
        await conn.execute('DELETE FROM industries')
        print("\n✅ 既存データクリア完了")

        # 要件仕様書準拠の正確な20カテゴリ
        required_industries = [
            ('食品', 1),
            ('菓子・氷菓', 2),
            ('アルコール飲料', 3),
            ('清涼飲料', 4),
            ('乳製品・乳飲料', 5),
            ('化粧品・ヘアケア・オーラルケア', 6),
            ('薬事・健康食品', 7),
            ('ファッション・アパレル・アクセサリー', 8),
            ('自動車・バイク', 9),
            ('金融・保険・証券・投資', 10),
            ('IT・通信・ソフトウェア', 11),
            ('不動産・住宅・建築', 12),
            ('小売・EC・通販', 13),
            ('ゲーム・エンターテイメント', 14),
            ('スポーツ・フィットネス', 15),
            ('旅行・ホテル・レジャー', 16),
            ('教育・学習・資格', 17),
            ('医療・ヘルスケア', 18),
            ('BtoB・法人向けサービス', 19),
            ('その他・官公庁・団体', 20)
        ]

        # データ挿入
        for name, order in required_industries:
            await conn.execute('''
                INSERT INTO industries (name, display_order)
                VALUES ($1, $2)
            ''', name, order)

        print(f"✅ {len(required_industries)}件の正しいデータ挿入完了")

        # 検証
        result = await conn.fetch('''
            SELECT id, name, display_order FROM industries ORDER BY display_order
        ''')

        print("\n📋 修正後の業種マスタデータ一覧:")
        print("-" * 80)
        for row in result:
            print(f"{row['display_order']}. {row['name']} (ID: {row['id']})")

        print(f"\n✅ 業種マスタ修正完了（合計: {len(result)}件）")

        if len(result) == 20:
            print("✅ 業種数が要件の20カテゴリと一致しました")
        else:
            print(f"❌ 業種数が要件と不一致です（期待値: 20、実際: {len(result)}）")

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
    asyncio.run(fix_industries())