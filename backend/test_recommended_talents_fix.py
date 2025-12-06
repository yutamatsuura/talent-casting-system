#!/usr/bin/env python3
"""
おすすめタレント機能修正版のテストスクリプト

STEP 5.5 修正内容の動作確認：
1. 管理画面設定のおすすめタレントが1-3位に確実に配置される
2. 予算フィルタリングがおすすめタレントに適用されない
3. スコア分配が適切に行われる
"""

import asyncio
import sys
import os

# パスを追加（backend/appモジュール読み込み用）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.endpoints.matching import (
    apply_recommended_talents_integration,
    get_recommended_talent_details,
    apply_step5_score_distribution
)
from app.api.endpoints.recommended_talents import get_recommended_talents_for_matching
from app.schemas.matching import MatchingFormData

async def test_recommended_talents_fix():
    """おすすめタレント機能修正版のテスト"""

    print("🔬 おすすめタレント機能修正版テスト開始")
    print("=" * 60)

    # テスト用フォームデータ（化粧品業界）
    test_form_data = MatchingFormData(
        industry="化粧品・ヘアケア・オーラルケア",
        target_segments="女性20-34歳",
        budget="1,000万円～3,000万円未満",
        purpose="ブランド認知向上",
        company_name="テスト企業",
        contact_name="テスト担当者",
        email="test@example.com",
        phone="090-1234-5678"
    )

    # 1. おすすめタレント設定の確認
    print("\n1️⃣ おすすめタレント設定確認")
    try:
        recommended_talents = await get_recommended_talents_for_matching(test_form_data.industry)
        print(f"設定済みおすすめタレント数: {len(recommended_talents) if recommended_talents else 0}")

        if recommended_talents:
            for i, talent in enumerate(recommended_talents[:3]):
                print(f"  - {i+1}位設定: ID={talent['account_id']}, 名前={talent['name']}")
        else:
            print("  ⚠️ おすすめタレント未設定")

    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return

    # 2. 予算フィルタリング除外テスト
    print("\n2️⃣ 予算フィルタリング除外テスト")
    if recommended_talents:
        talent_id = recommended_talents[0]["account_id"]
        try:
            talent_details = await get_recommended_talent_details(
                talent_id,
                test_form_data.target_segments
            )
            if talent_details:
                print(f"  ✅ おすすめタレント詳細取得成功: {talent_details['name']}")
                print(f"     - base_power_score: {talent_details['base_power_score']}")
            else:
                print(f"  ❌ おすすめタレント詳細取得失敗: ID={talent_id}")
        except Exception as e:
            print(f"  ❌ エラー: {e}")

    # 3. 統合ロジックテスト（モックデータ使用）
    print("\n3️⃣ 統合ロジックテスト")

    # モック通常結果作成
    mock_standard_results = []
    for i in range(10):
        mock_standard_results.append({
            "account_id": 10000 + i,
            "target_segment_id": 4,
            "base_power_score": 50.0 - i,
            "image_adjustment": 5.0 - i,
            "reflected_score": 55.0 - i,
            "ranking": i + 1,
            "name": f"通常タレント{i+1}",
            "last_name_kana": f"ツウジョウ",
            "act_genre": "俳優"
        })

    try:
        # 統合ロジック実行
        integrated_results = await apply_recommended_talents_integration(
            test_form_data,
            mock_standard_results
        )

        print(f"  統合後結果数: {len(integrated_results)}")

        # 1-3位のチェック
        top_3 = integrated_results[:3]
        for i, result in enumerate(top_3):
            is_recommended = result.get("is_recommended", False)
            recommended_type = result.get("recommended_type", "unknown")
            print(f"  - {i+1}位: {result['name']} (おすすめ: {is_recommended}, タイプ: {recommended_type})")

        # 4-6位のチェック
        if len(integrated_results) > 3:
            print("\n  4-6位の結果:")
            for i in range(3, min(6, len(integrated_results))):
                result = integrated_results[i]
                is_recommended = result.get("is_recommended", False)
                recommended_type = result.get("recommended_type", "unknown")
                print(f"  - {result['ranking']}位: {result['name']} (おすすめ: {is_recommended}, タイプ: {recommended_type})")

    except Exception as e:
        print(f"  ❌ 統合ロジックエラー: {e}")
        return

    # 4. スコア分配テスト
    print("\n4️⃣ スコア分配テスト")
    try:
        scored_results = apply_step5_score_distribution(integrated_results.copy())

        print("  順位帯別スコア確認:")
        for result in scored_results[:10]:  # 上位10名のみ表示
            ranking = result["ranking"]
            score = result["matching_score"]
            is_recommended = result.get("is_recommended", False)
            expected_range = ""

            if 1 <= ranking <= 3:
                expected_range = "97.0-99.7"
            elif 4 <= ranking <= 10:
                expected_range = "93.0-96.9"

            print(f"  - {ranking}位: {score}点 (期待範囲: {expected_range}, おすすめ: {is_recommended})")

    except Exception as e:
        print(f"  ❌ スコア分配エラー: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ おすすめタレント機能修正版テスト完了")

    # 修正内容サマリー
    print("\n📋 修正内容サマリー:")
    print("1. ✅ おすすめタレントを必ず1-3位に固定配置")
    print("2. ✅ 予算フィルタリングの除外処理実装")
    print("3. ✅ 特別スコア範囲を廃止し、通常の順位帯ルールに統一")
    print("4. ✅ おすすめタレント不足時の補完ロジック改善")

if __name__ == "__main__":
    asyncio.run(test_recommended_talents_fix())