#!/usr/bin/env python3
"""データベースとマスタデータの整合性確認"""

import asyncio
import sys
from pathlib import Path

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, text
from app.db.connection import init_db, get_session_maker
from app.models import Industry, TargetSegment, ImageItem, BudgetRange, IndustryImage

# グローバル変数でセッションメーカーを保持
AsyncSessionLocal = None

async def get_async_session():
    """非同期セッション取得"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

async def verify_industries():
    """業種マスタの整合性確認"""
    print("\n🏭 === INDUSTRIES VERIFICATION ===")

    async with await get_async_session() as session:
        result = await session.execute(select(Industry).order_by(Industry.id))
        industries = result.scalars().all()

        print(f"📊 総件数: {len(industries)}件")
        print("✅ 正しい20業種であることを確認:")

        expected_names = [
            "食品", "菓子・氷菓", "乳製品", "清涼飲料水", "アルコール飲料",
            "フードサービス", "医薬品・医療・健康食品", "化粧品・ヘアケア・オーラルケア",
            "トイレタリー", "自動車関連", "家電", "通信・IT",
            "ゲーム・エンターテイメント・アプリ", "流通・通販", "ファッション",
            "貴金属", "金融・不動産", "エネルギー・輸送・交通",
            "教育・出版・公共団体", "観光"
        ]

        all_correct = True
        for i, industry in enumerate(industries):
            if i < len(expected_names) and industry.name == expected_names[i]:
                print(f"   ✅ {industry.id}: {industry.name}")
            else:
                print(f"   ❌ {industry.id}: {industry.name} (期待値: {expected_names[i] if i < len(expected_names) else 'N/A'})")
                all_correct = False

        return len(industries) == 20 and all_correct

async def verify_target_segments():
    """ターゲット層マスタの整合性確認"""
    print("\n🎯 === TARGET_SEGMENTS VERIFICATION ===")

    async with await get_async_session() as session:
        result = await session.execute(select(TargetSegment).order_by(TargetSegment.display_order))
        segments = result.scalars().all()

        print(f"📊 総件数: {len(segments)}件")
        print("✅ 正しい8セグメント（フォーム仕様準拠）であることを確認:")

        expected_codes = ["M1219", "M2034", "M3549", "M5069", "F1219", "F2034", "F3549", "F5069"]

        all_correct = True
        segment_codes = [seg.code for seg in segments]

        for code in expected_codes:
            if code in segment_codes:
                segment = next(seg for seg in segments if seg.code == code)
                print(f"   ✅ {segment.id}: {segment.name} ({segment.code})")
            else:
                print(f"   ❌ Missing: {code}")
                all_correct = False

        return len(segments) == 8 and all_correct

async def verify_image_items():
    """イメージ項目マスタの整合性確認"""
    print("\n🖼️  === IMAGE_ITEMS VERIFICATION ===")

    async with await get_async_session() as session:
        result = await session.execute(select(ImageItem).order_by(ImageItem.display_order))
        items = result.scalars().all()

        print(f"📊 総件数: {len(items)}件")
        print("✅ 正しい7イメージ項目であることを確認:")

        expected_names = ["おもしろい", "清潔感がある", "個性的", "信頼できる", "可愛い", "カッコいい", "大人っぽい"]

        all_correct = True
        for i, item in enumerate(items):
            if i < len(expected_names) and item.name in expected_names:
                print(f"   ✅ {item.id}: {item.name} ({item.code})")
            else:
                print(f"   ❌ {item.id}: {item.name} (予期しない項目)")
                all_correct = False

        return len(items) == 7 and all_correct

async def verify_budget_ranges():
    """予算区分マスタの整合性確認"""
    print("\n💰 === BUDGET_RANGES VERIFICATION ===")

    async with await get_async_session() as session:
        result = await session.execute(select(BudgetRange).order_by(BudgetRange.display_order))
        ranges = result.scalars().all()

        print(f"📊 総件数: {len(ranges)}件")
        print("✅ 正しい4予算区分であることを確認:")

        expected_ranges = [
            ("1,000万円未満", 0, 9999999),
            ("1,000万円～3,000万円未満", 10000000, 29999999),
            ("3,000万円～1億円未満", 30000000, 99999999),
            ("1億円以上", 100000000, 999999999)
        ]

        all_correct = True
        for i, budget_range in enumerate(ranges):
            if i < len(expected_ranges):
                name, min_amt, max_amt = expected_ranges[i]
                if (budget_range.name == name and
                    int(budget_range.min_amount) == min_amt and
                    int(budget_range.max_amount) == max_amt):
                    print(f"   ✅ {budget_range.id}: {budget_range.name}")
                    print(f"        {budget_range.min_amount:,}円 ～ {budget_range.max_amount:,}円")
                else:
                    print(f"   ❌ {budget_range.id}: {budget_range.name} (値が不正)")
                    all_correct = False
            else:
                print(f"   ❌ 予期しない予算区分: {budget_range.name}")
                all_correct = False

        return len(ranges) == 4 and all_correct

async def verify_industry_images():
    """業種-イメージマッピングの整合性確認"""
    print("\n🔗 === INDUSTRY_IMAGES MAPPING VERIFICATION ===")

    async with await get_async_session() as session:
        result = await session.execute(select(IndustryImage))
        mappings = result.scalars().all()

        print(f"📊 総マッピング件数: {len(mappings)}件")
        print("✅ 1業種1イメージの正式マッピングであることを確認:")

        # 業種別マッピング数確認
        industry_counts = {}
        for mapping in mappings:
            industry_id = mapping.industry_id
            industry_counts[industry_id] = industry_counts.get(industry_id, 0) + 1

        all_correct = True
        for industry_id in range(1, 21):  # 1-20業種
            count = industry_counts.get(industry_id, 0)
            if count == 1:
                print(f"   ✅ 業種{industry_id}: 1イメージ項目")
            else:
                print(f"   ❌ 業種{industry_id}: {count}イメージ項目 (期待値: 1)")
                all_correct = False

        return len(mappings) == 20 and all_correct

async def main():
    """メイン処理"""
    print("=" * 80)
    print("🔍 DATABASE INTEGRITY VERIFICATION")
    print("=" * 80)
    print("🎯 目的: マスタデータとデータベースの整合性確認")
    print("=" * 80)

    try:
        # 各テーブルの整合性確認
        industries_ok = await verify_industries()
        segments_ok = await verify_target_segments()
        images_ok = await verify_image_items()
        budget_ok = await verify_budget_ranges()
        mappings_ok = await verify_industry_images()

        print("\n" + "=" * 80)
        print("📊 整合性確認結果サマリー")
        print("=" * 80)

        results = {
            "業種マスタ (industries)": industries_ok,
            "ターゲット層 (target_segments)": segments_ok,
            "イメージ項目 (image_items)": images_ok,
            "予算区分 (budget_ranges)": budget_ok,
            "業種イメージマッピング (industry_images)": mappings_ok
        }

        all_ok = True
        for table_name, is_ok in results.items():
            status = "✅ 整合性OK" if is_ok else "❌ 整合性NG"
            print(f"{status} {table_name}")
            if not is_ok:
                all_ok = False

        print("\n" + "=" * 80)
        if all_ok:
            print("🎉 データベース整合性確認完了: すべて正常")
            print("📊 マスタデータとデータベースは完全に同期済み")
            print("✅ 追加のデータベース修正は不要です")
        else:
            print("🚨 データベース整合性に問題があります")
            print("🔧 該当テーブルの修正が必要です")
        print("=" * 80)

        return all_ok

    except Exception as e:
        print(f"\n❌ 整合性確認中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)