"""
本番環境マッチングロジック直接呼び出し（独自ロジック一切なし）
"""
from typing import Dict, List, Any
import datetime
from app.db.ultra_optimized_queries import UltraOptimizedMatchingQueries
from app.db.connection import get_asyncpg_connection

class EnhancedMatchingDebug:
    def __init__(self):
        self.debug_info = []

    async def generate_complete_talent_analysis(
        self,
        industry: str,
        target_segments: List[str],
        purpose: str,
        budget: str
    ) -> List[Dict[str, Any]]:
        """
        本番環境と完全に同じマッチングロジックを使用してタレント分析データを生成
        VR/TPR個別データとイメージスコアを追加取得
        """

        # 入力条件の記録
        input_conditions = {
            "industry": industry,
            "target_segments": target_segments,
            "purpose": purpose,
            "budget": budget,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analysis_type": "本番環境同等16列データ"
        }

        target_segment = target_segments[0] if target_segments else "女性20-34歳"

        try:
            # 本番環境のマッチングロジックを直接呼び出し
            talent_data = await UltraOptimizedMatchingQueries.execute_ultra_optimized_matching_flow(
                industry,
                target_segment,
                budget
            )

            # account_idリストを取得
            account_ids = [talent['account_id'] for talent in talent_data]

            # VR/TPRデータとイメージスコアを追加取得
            additional_data = await self._get_additional_talent_data(account_ids, target_segment)

            # 本番環境の結果を16列形式に変換（追加データと統合）
            detailed_results = []
            for talent in talent_data:
                account_id = talent['account_id']
                additional = additional_data.get(account_id, {})

                detailed_talent = {
                    "タレント名": talent.get('name', f"タレント{talent.get('ranking', 0)}"),
                    "カテゴリー": additional.get('act_genre', 'タレント'),
                    "VR人気度": round(float(additional.get('vr_popularity', 0)), 1),
                    "TPRスコア": round(float(additional.get('tpr_power_score', 0)), 1),
                    "従来スコア": round(float(talent.get('base_power_score', 0)), 1),
                    "おもしろさ": round(float(additional.get('image_funny', 0)), 1),
                    "清潔感": round(float(additional.get('image_clean', 0)), 1),
                    "個性的な": round(float(additional.get('image_unique', 0)), 1),
                    "信頼できる": round(float(additional.get('image_trustworthy', 0)), 1),
                    "かわいい": round(float(additional.get('image_cute', 0)), 1),
                    "カッコいい": round(float(additional.get('image_cool', 0)), 1),
                    "大人の魅力": round(float(additional.get('image_mature', 0)), 1),
                    "従来順位": 0,  # 後で計算
                    "業種別イメージ": round(float(talent.get('image_adjustment', 0)), 1),
                    "最終スコア": round(float(talent.get('matching_score', 0)), 3),
                    "最終順位": talent.get('ranking', 0)
                }
                detailed_results.append(detailed_talent)

            # 従来順位を基礎パワー得点順で計算
            detailed_results = self._calculate_conventional_ranking(detailed_results)

            return detailed_results

        except Exception as e:
            print(f"本番環境マッチング実行エラー: {e}")
            import traceback
            traceback.print_exc()
            # エラー時は空のリストを返す
            return []

    async def _get_additional_talent_data(self, account_ids: List[int], target_segment: str) -> Dict[int, Dict[str, Any]]:
        """
        VR/TPR個別データとイメージスコアを取得
        """
        if not account_ids:
            return {}

        conn = await get_asyncpg_connection()
        try:
            # ターゲットセグメントIDを取得
            segment_query = "SELECT target_segment_id FROM target_segments WHERE segment_name = $1"
            segment_result = await conn.fetchrow(segment_query, target_segment)
            if not segment_result:
                return {}

            target_segment_id = segment_result['target_segment_id']

            # VR/TPRデータとイメージスコアを一括取得
            query = """
            SELECT
                ma.account_id,
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
                AND ts.target_segment_id = $1
            LEFT JOIN talent_images ti ON ma.account_id = ti.account_id
                AND ti.target_segment_id = $1
            WHERE ma.account_id = ANY($2)
            """

            results = await conn.fetch(query, target_segment_id, account_ids)

            # 結果を辞書形式で返す
            data_dict = {}
            for row in results:
                data_dict[row['account_id']] = dict(row)

            return data_dict

        finally:
            await conn.close()

    def _calculate_conventional_ranking(self, detailed_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        従来順位を基礎パワー得点（従来スコア）順で正しく計算
        """
        # 従来スコア順でソート（降順）
        sorted_by_conventional = sorted(detailed_results, key=lambda x: x["従来スコア"], reverse=True)

        # 従来順位を割り当て
        for i, talent in enumerate(sorted_by_conventional):
            talent["従来順位"] = i + 1

        return detailed_results

