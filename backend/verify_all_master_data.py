#!/usr/bin/env python3
"""
全マスタデータ検証スクリプト
要件仕様書との完全一致を確認
"""

import asyncio
import asyncpg
import os
import sys

# データベース接続URL
DATABASE_URL = "postgresql://neondb_owner:npg_9fvZtIKj3gHe@ep-wild-art-a1dq56d3-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# 要件で定義された正しいマスタデータ
REQUIRED_INDUSTRIES = [
    "食品", "菓子・氷菓", "アルコール飲料", "清涼飲料", "乳製品・乳飲料",
    "化粧品・ヘアケア・オーラルケア", "薬事・健康食品", "ファッション・アパレル・アクセサリー",
    "自動車・バイク", "金融・保険・証券・投資", "IT・通信・ソフトウェア", "不動産・住宅・建築",
    "小売・EC・通販", "ゲーム・エンターテイメント", "スポーツ・フィットネス", "旅行・ホテル・レジャー",
    "教育・学習・資格", "医療・ヘルスケア", "BtoB・法人向けサービス", "その他・官公庁・団体"
]

REQUIRED_TARGET_SEGMENTS = [
    ("F1", "女性20-34", "女性", "20-34歳"),
    ("F2", "女性35-49", "女性", "35-49歳"),
    ("F3", "女性50歳以上", "女性", "50歳以上"),
    ("M1", "男性20-34", "男性", "20-34歳"),
    ("M2", "男性35-49", "男性", "35-49歳"),
    ("M3", "男性50歳以上", "男性", "50歳以上"),
    ("Teen", "10代（高校生中心）", "全体", "13-19歳"),
    ("Senior", "60歳以上", "全体", "60歳以上")
]

REQUIRED_PURPOSE_OBJECTIVES = [
    "ブランドイメージの向上",
    "商品・サービス認知度向上",
    "購買促進・売上拡大",
    "新商品・サービスの告知",
    "企業信頼度・安心感の向上",
    "ターゲット層の拡大",
    "競合他社との差別化"
]

REQUIRED_BUDGET_RANGES = [
    ("300万円未満", 0, 2999999),
    ("300万円～1,000万円未満", 3000000, 9999999),
    ("1,000万円～3,000万円未満", 10000000, 29999999),
    ("3,000万円以上", 30000000, 999999999)
]

async def verify_all_master_data():
    """全マスタデータの検証"""
    print("🔍 全マスタデータ検証開始...")
    print("=" * 80)

    all_passed = True

    try:
        # データベース接続
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ データベース接続成功\n")

        # 1. 業種マスタ検証
        print("1️⃣ 業種マスタ（industries）検証")
        print("-" * 40)

        industries = await conn.fetch('''
            SELECT name FROM industries ORDER BY display_order
        ''')

        industry_names = [row['name'] for row in industries]

        print(f"期待値: {len(REQUIRED_INDUSTRIES)}件")
        print(f"実際値: {len(industry_names)}件")

        if industry_names == REQUIRED_INDUSTRIES:
            print("✅ 業種マスタ: 完全一致")
        else:
            print("❌ 業種マスタ: 不一致")
            print("不足:", set(REQUIRED_INDUSTRIES) - set(industry_names))
            print("余分:", set(industry_names) - set(REQUIRED_INDUSTRIES))
            all_passed = False

        # 2. ターゲット層マスタ検証
        print("\n2️⃣ ターゲット層マスタ（target_segments）検証")
        print("-" * 40)

        segments = await conn.fetch('''
            SELECT code, name, gender, age_range FROM target_segments ORDER BY display_order
        ''')

        segment_tuples = [(row['code'], row['name'], row['gender'], row['age_range']) for row in segments]

        print(f"期待値: {len(REQUIRED_TARGET_SEGMENTS)}件")
        print(f"実際値: {len(segment_tuples)}件")

        if segment_tuples == REQUIRED_TARGET_SEGMENTS:
            print("✅ ターゲット層マスタ: 完全一致")
        else:
            print("❌ ターゲット層マスタ: 不一致")
            print("期待:", REQUIRED_TARGET_SEGMENTS)
            print("実際:", segment_tuples)
            all_passed = False

        # 3. 起用目的マスタ検証
        print("\n3️⃣ 起用目的マスタ（purpose_objectives）検証")
        print("-" * 40)

        purposes = await conn.fetch('''
            SELECT name FROM purpose_objectives ORDER BY display_order
        ''')

        purpose_names = [row['name'] for row in purposes]

        print(f"期待値: {len(REQUIRED_PURPOSE_OBJECTIVES)}件")
        print(f"実際値: {len(purpose_names)}件")

        if purpose_names == REQUIRED_PURPOSE_OBJECTIVES:
            print("✅ 起用目的マスタ: 完全一致")
        else:
            print("❌ 起用目的マスタ: 不一致")
            print("不足:", set(REQUIRED_PURPOSE_OBJECTIVES) - set(purpose_names))
            print("余分:", set(purpose_names) - set(REQUIRED_PURPOSE_OBJECTIVES))
            all_passed = False

        # 4. 予算区分マスタ検証
        print("\n4️⃣ 予算区分マスタ（budget_ranges）検証")
        print("-" * 40)

        budgets = await conn.fetch('''
            SELECT name, min_amount, max_amount FROM budget_ranges ORDER BY display_order
        ''')

        budget_tuples = [(row['name'], row['min_amount'], row['max_amount']) for row in budgets]

        print(f"期待値: {len(REQUIRED_BUDGET_RANGES)}件")
        print(f"実際値: {len(budget_tuples)}件")

        if budget_tuples == REQUIRED_BUDGET_RANGES:
            print("✅ 予算区分マスタ: 完全一致")
        else:
            print("❌ 予算区分マスタ: 不一致")
            print("期待:", REQUIRED_BUDGET_RANGES)
            print("実際:", budget_tuples)
            all_passed = False

        # 詳細データ表示
        print(f"\n📋 詳細データ一覧")
        print("=" * 80)

        # 各マスタの詳細表示
        for title, query, items in [
            ("業種マスタ", "SELECT id, name, display_order FROM industries ORDER BY display_order", None),
            ("ターゲット層マスタ", "SELECT id, code, name, gender, age_range, display_order FROM target_segments ORDER BY display_order", None),
            ("起用目的マスタ", "SELECT id, name, display_order FROM purpose_objectives ORDER BY display_order", None),
            ("予算区分マスタ", "SELECT id, name, min_amount, max_amount, display_order FROM budget_ranges ORDER BY display_order", None),
        ]:
            print(f"\n{title}:")
            print("-" * 40)

            data = await conn.fetch(query)
            for row in data:
                if "budget_ranges" in query:
                    print(f"  {row['display_order']}. {row['name']} (ID: {row['id']}) - {row['min_amount']:,}円～{row['max_amount']:,}円")
                elif "target_segments" in query:
                    print(f"  {row['display_order']}. {row['code']}: {row['name']} ({row['gender']}, {row['age_range']}) (ID: {row['id']})")
                else:
                    print(f"  {row['display_order']}. {row['name']} (ID: {row['id']})")

        # 最終結果
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ 全マスタデータ検証: 成功")
            print("✅ 全てのマスタデータが要件仕様書と完全一致しています")
        else:
            print("❌ 全マスタデータ検証: 失敗")
            print("❌ 一部のマスタデータに不整合があります")

        return all_passed

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        try:
            await conn.close()
            print("\n✅ データベース接続終了")
        except:
            pass

if __name__ == "__main__":
    result = asyncio.run(verify_all_master_data())
    sys.exit(0 if result else 1)