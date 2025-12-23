#!/usr/bin/env python3
"""
execute_matching_logic結果を16列CSV形式に変換する関数
"""
import asyncio
from typing import List, Dict, Any
from app.db.connection import get_asyncpg_connection, release_asyncpg_connection

async def convert_matching_results_to_csv_format(
    matching_results: List[Dict],
    industry: str,
    target_segment: str
) -> List[Dict[str, Any]]:
    """
    execute_matching_logic + apply_recommended_talents_integrationの結果を
    16列CSV形式に変換
    """
    if not matching_results:
        return []

    # account_idリストを取得
    account_ids = [result['account_id'] for result in matching_results]

    conn = await get_asyncpg_connection()
    try:
        # 追加データ一括取得（Enhanced_matching_debugと同様）
        additional_query = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching as full_name,
            ma.act_genre,
            ts.vr_popularity,
            ts.tpr_power_score,
            ti.image_funny,
            ti.image_clean,
            ti.image_unique,
            ti.image_trustworthy,
            ti.image_cute,
            ti.image_cool,
            ti.image_mature
        FROM m_account ma
        LEFT JOIN talent_scores ts ON ma.account_id = ts.account_id
        LEFT JOIN talent_images ti ON ma.account_id = ti.account_id
        WHERE ma.account_id = ANY($1)
        AND ts.target_segment_id = (
            SELECT target_segment_id FROM target_segments
            WHERE segment_name = $2 LIMIT 1
        )
        """
        additional_rows = await conn.fetch(additional_query, account_ids, target_segment)

        # account_id -> 追加データのマッピング作成
        additional_data = {}
        for row in additional_rows:
            additional_data[row['account_id']] = dict(row)

    finally:
        await release_asyncpg_connection(conn)

    # 16列形式に変換
    detailed_results = []
    for talent in matching_results:
        account_id = talent['account_id']
        additional = additional_data.get(account_id, {})

        # None値を安全に処理するヘルパー関数
        def safe_float(value, default=0):
            if value is None:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        detailed_talent = {
            "タレント名": talent.get('name', additional.get('full_name', f"タレント{talent.get('ranking', 0)}")),
            "カテゴリー": additional.get('act_genre', 'タレント'),
            "VR人気度": round(safe_float(additional.get('vr_popularity')), 1),
            "TPRスコア": round(safe_float(additional.get('tpr_power_score')), 1),
            "従来スコア": round(safe_float(talent.get('base_power_score')), 1),
            "おもしろさ": round(safe_float(additional.get('image_funny')), 1),
            "清潔感": round(safe_float(additional.get('image_clean')), 1),
            "個性的な": round(safe_float(additional.get('image_unique')), 1),
            "信頼できる": round(safe_float(additional.get('image_trustworthy')), 1),
            "かわいい": round(safe_float(additional.get('image_cute')), 1),
            "カッコいい": round(safe_float(additional.get('image_cool')), 1),
            "大人の魅力": round(safe_float(additional.get('image_mature')), 1),
            "従来順位": 0,  # 後で計算
            "業種別イメージ": round(safe_float(talent.get('image_adjustment')), 1),
            "最終スコア": round(safe_float(talent.get('reflected_score')), 3),
            "最終順位": talent.get('ranking', 0)
        }
        detailed_results.append(detailed_talent)

    # 従来順位を基礎パワー得点順で計算
    detailed_results_sorted_by_base = sorted(detailed_results,
                                           key=lambda x: x['従来スコア'],
                                           reverse=True)

    for i, talent in enumerate(detailed_results_sorted_by_base):
        talent['従来順位'] = i + 1

    # 最終順位順でソート（元の順序に戻す）
    detailed_results.sort(key=lambda x: x['最終順位'])

    return detailed_results

if __name__ == "__main__":
    # テスト用
    async def test():
        # テストデータ
        test_results = [
            {
                'account_id': 123,
                'name': 'テストタレント',
                'base_power_score': 85.5,
                'image_adjustment': 5,
                'reflected_score': 90.5,
                'ranking': 1
            }
        ]

        converted = await convert_matching_results_to_csv_format(
            test_results, "ファッション", "女性20-34歳"
        )
        print("変換結果:", converted)

    asyncio.run(test())