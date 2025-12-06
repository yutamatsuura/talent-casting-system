#!/usr/bin/env python3
"""データ件数差異の詳細調査"""

import asyncio
import sys
from pathlib import Path

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, text
from app.db.connection import init_db, get_session_maker

# グローバル変数でセッションメーカーを保持
AsyncSessionLocal = None

async def get_async_session():
    """非同期セッション取得"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

async def investigate_data_discrepancies():
    """データ件数差異の詳細調査"""
    print("=" * 80)
    print("🔍 DATA DISCREPANCY INVESTIGATION")
    print("=" * 80)
    print("📊 期待値と実際値の差異原因を調査")
    print("=" * 80)

    async with await get_async_session() as session:

        # 1. Talents詳細調査
        print("\n📋 TALENTS テーブル詳細調査")
        print("期待値: 約2,000件 → 実際: 4,810件")

        result = await session.execute(text("""
            SELECT category, COUNT(*) as count
            FROM talents
            GROUP BY category
            ORDER BY count DESC
        """))
        print("カテゴリ別件数:")
        for row in result:
            print(f"   • {row[0]}: {row[1]}件")

        # 2. Target Segments調査
        print("\n📋 TARGET_SEGMENTS 一覧")
        result = await session.execute(text("SELECT id, name, code FROM target_segments ORDER BY id"))
        segments = []
        for row in result:
            segments.append({"id": row[0], "name": row[1], "code": row[2]})
            print(f"   • ID{row[0]}: {row[1]} ({row[2]})")

        # 3. Talent Scores詳細調査
        print("\n📋 TALENT_SCORES テーブル詳細調査")
        print("期待値: 約16,000件 → 実際: 6,118件")

        result = await session.execute(text("""
            SELECT target_segment_id, COUNT(*) as count
            FROM talent_scores
            GROUP BY target_segment_id
            ORDER BY target_segment_id
        """))
        print("ターゲット層別件数:")
        scores_by_segment = {}
        for row in result:
            segment_id = row[0]
            count = row[1]
            scores_by_segment[segment_id] = count
            segment_name = next((s["name"] for s in segments if s["id"] == segment_id), f"ID{segment_id}")
            print(f"   • {segment_name}: {count}件")

        # 4. Talent Images詳細調査
        print("\n📋 TALENT_IMAGES テーブル詳細調査")
        print("期待値: 約16,000件 → 実際: 2,688件")

        result = await session.execute(text("""
            SELECT target_segment_id, COUNT(*) as count
            FROM talent_images
            GROUP BY target_segment_id
            ORDER BY target_segment_id
        """))
        print("ターゲット層別件数:")
        images_by_segment = {}
        for row in result:
            segment_id = row[0]
            count = row[1]
            images_by_segment[segment_id] = count
            segment_name = next((s["name"] for s in segments if s["id"] == segment_id), f"ID{segment_id}")
            print(f"   • {segment_name}: {count}件")

        # 5. 期待値計算
        print("\n📊 期待値計算・分析")
        talent_count = 4810
        segment_count = len(segments)
        image_items_count = 7

        print(f"タレント総数: {talent_count}件")
        print(f"ターゲット層数: {segment_count}件")
        print(f"イメージ項目数: {image_items_count}件")

        expected_talent_scores = talent_count * segment_count
        expected_talent_images = talent_count * segment_count * image_items_count

        print(f"\n期待値計算（理論値）:")
        print(f"   • talent_scores: {talent_count} × {segment_count} = {expected_talent_scores:,}件")
        print(f"   • talent_images: {talent_count} × {segment_count} × {image_items_count} = {expected_talent_images:,}件")

        actual_scores = sum(scores_by_segment.values())
        actual_images = sum(images_by_segment.values())

        print(f"\n実際値:")
        print(f"   • talent_scores: {actual_scores:,}件 ({actual_scores/expected_talent_scores*100:.1f}%)")
        print(f"   • talent_images: {actual_images:,}件 ({actual_images/expected_talent_images*100:.1f}%)")

        # 6. 余分テーブルの詳細調査
        print("\n📋 余分なテーブル詳細調査")

        print("\n🔍 INDUSTRY_IMAGES テーブル:")
        result = await session.execute(text("SELECT COUNT(*) FROM industry_images"))
        count = result.scalar()
        print(f"   件数: {count}件")

        result = await session.execute(text("""
            SELECT ii.industry_id, i.name as industry_name, ii.image_item_id, img.name as image_name
            FROM industry_images ii
            LEFT JOIN industries i ON ii.industry_id = i.id
            LEFT JOIN image_items img ON ii.image_item_id = img.id
            ORDER BY ii.industry_id
            LIMIT 10
        """))
        print("   サンプルデータ:")
        for row in result:
            print(f"     業種{row[0]} ({row[1]}) → イメージ{row[2]} ({row[3]})")

        print("\n🔍 PURPOSE_OBJECTIVES テーブル:")
        result = await session.execute(text("SELECT COUNT(*) FROM purpose_objectives"))
        count = result.scalar()
        print(f"   件数: {count}件")

        result = await session.execute(text("SELECT id, name FROM purpose_objectives ORDER BY display_order"))
        print("   データ内容:")
        for row in result:
            print(f"     {row[0]}: {row[1]}")

        # 7. 問題判定とレコメンデーション
        print("\n" + "=" * 80)
        print("📊 問題判定とレコメンデーション")
        print("=" * 80)

        problems = []
        recommendations = []

        # Talents件数問題
        if talent_count > 2400:  # 2000の20%マージン
            problems.append("📈 talentsテーブルの件数が期待値より多い")
            recommendations.append("🔧 talentsテーブルのフィルタリング基準確認")

        # Scores不足問題
        score_coverage = actual_scores / expected_talent_scores * 100
        if score_coverage < 80:
            problems.append("📉 talent_scoresデータが大幅に不足")
            recommendations.append("🔧 TPR/VRスコアデータの追加インポート")

        # Images不足問題
        image_coverage = actual_images / expected_talent_images * 100
        if image_coverage < 80:
            problems.append("📉 talent_imagesデータが大幅に不足")
            recommendations.append("🔧 VRイメージスコアデータの追加インポート")

        # 余分テーブル問題
        problems.append("📊 期待構成に含まれない余分テーブルが存在")
        recommendations.append("🧹 industry_images, purpose_objectivesテーブルの要否確認")

        print("🚨 発見された問題:")
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. {problem}")

        print("\n💡 推奨対応:")
        for i, recommendation in enumerate(recommendations, 1):
            print(f"   {i}. {recommendation}")

        print("\n🎯 結論:")
        if len(problems) > 2:
            print("   ❌ データベース構成に複数の問題があります")
            print("   🔧 構造的な見直しが必要です")
        else:
            print("   ⚠️ 部分的な修正で対応可能です")

        print("=" * 80)

        return {
            "talent_count": talent_count,
            "expected_scores": expected_talent_scores,
            "actual_scores": actual_scores,
            "expected_images": expected_talent_images,
            "actual_images": actual_images,
            "problems": problems,
            "recommendations": recommendations
        }

async def main():
    """メイン処理"""
    try:
        result = await investigate_data_discrepancies()
        return result
    except Exception as e:
        print(f"\n❌ 調査中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)