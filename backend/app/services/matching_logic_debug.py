"""
マッチングロジック詳細版 - デバッグ・テスト用
既存のマッチングロジックを再利用し、詳細な計算過程を記録してGoogle Sheetsエクスポートに使用
"""
from typing import Dict, List, Any, Tuple
from app.api.endpoints.matching import execute_matching_logic, check_currently_in_cm, get_recommended_talents_batch
import datetime


class MatchingLogicDebug:
    def __init__(self):
        self.debug_info = []

    async def execute_matching_with_debug(
        self,
        industry: str,
        target_segments: List[str],
        purpose: str,
        budget: str
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        既存のマッチングロジックを実行し、詳細なデバッグ情報を収集

        Returns:
            Tuple[最終結果, デバッグ情報]
        """
        self.debug_info = []

        # 入力条件の記録
        input_conditions = {
            "industry": industry,
            "target_segments": target_segments,
            "purpose": purpose,
            "budget": budget,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result_url": f"診断結果URL（後で設定）"
        }

        # 既存のマッチングロジックを実行
        # target_segments が List[str] なので、最初の要素を使用（仕様上単一選択）
        target_segment = target_segments[0] if target_segments else "女性20-34歳"

        # 既存のマッチングロジック実行（修正版）
        # 注意：この部分は実際のマッチングロジックと統合する必要がある
        try:
            from app.api.endpoints.matching import post_matching_optimized
            from app.schemas.matching import MatchingFormData
            from app.db.connection import get_db_session

            # マッチングフォームデータを作成
            form_data = MatchingFormData(
                industry=industry,
                target_segments=target_segments,
                purpose=purpose,
                budget=budget,
                company_name="テスト用",
                contact_email="test@example.com"
            )

            # データベース接続を取得（仮の実装）
            async for db_session in get_db_session():
                # 基本的なマッチング結果を取得
                talent_results = await execute_matching_logic(
                    industry=industry,
                    target_segment=target_segments[0],
                    budget=budget,
                    db=db_session
                )
                break

        except Exception as e:
            print(f"マッチングロジック実行エラー: {e}")
            talent_results = []

        # 詳細データ構造を生成（16列対応）
        detailed_results = await self._generate_detailed_talent_data(
            talent_results, industry, target_segments[0]
        )

        # 結果をマージして最終データに変換
        final_results = []
        for i, talent in enumerate(talent_results):
            account_id = talent["account_id"]
            final_talent = {
                "ranking": i + 1,
                "account_id": account_id,
                "name": talent["name"],
                "category": talent.get("category", ""),
                "matching_score": float(talent["matching_score"]),
                "base_power_score": talent.get("base_power_score", 0.0),
                "image_adjustment": talent.get("image_adjustment", 0.0),
                "is_recommended": account_id in recommended_talent_ids,
                "is_currently_in_cm": cm_status_map.get(account_id, False),
                "人気度": talent.get("vr_popularity", 0),
                "知名度": talent.get("tpr_power_score", 0),
                "従来スコア": talent.get("base_power_score", 0.0),
                "おもしろい": talent.get("omoshiroi", 0),
                "清潔感がある": talent.get("seiketsukan", 0),
                "個性的な": talent.get("koseiteki", 0),
                "信頼できる": talent.get("shinrai", 0),
                "かわいい": talent.get("kawaii", 0),
                "カッコいい": talent.get("kakkoii", 0),
                "大人の魅力": talent.get("otona", 0),
                "従来順位": talent.get("original_ranking", i + 1),
                "業種別イメージスコア": talent.get("image_adjustment", 0.0),
                "最終スコア": float(talent["matching_score"]),
                "最終順位": i + 1
            }
            final_results.append(final_talent)

        # デバッグ情報を構築
        step_calculations = [
            {
                "step": "Step 0: 予算フィルタリング",
                "description": f"予算範囲「{budget}」でタレントを絞り込み",
                "talent_count": len(talent_results),
                "details": f"対象タレント数: {len(talent_results)}件"
            },
            {
                "step": "Step 1: 基礎パワー得点計算",
                "description": f"ターゲット層「{target_segment}」の人気度・パワースコアを算出",
                "talent_count": len(talent_results),
                "details": "VRデータ（人気度）とTPRデータ（パワースコア）の平均値を計算"
            },
            {
                "step": "Step 2: 業種イメージ査定",
                "description": f"業種「{industry}」のイメージ適合度を評価",
                "talent_count": len(talent_results),
                "details": "業種別イメージデータを基に加減点を算出"
            },
            {
                "step": "Step 3: 基礎反映得点",
                "description": "Step1とStep2の結果を合算",
                "talent_count": len(talent_results),
                "details": "基礎パワー得点 + 業種イメージ加減点"
            },
            {
                "step": "Step 4: ランキング確定",
                "description": "基礎反映得点でソート・上位30名を選定",
                "talent_count": min(30, len(talent_results)),
                "details": "基礎反映得点 DESC, base_power_score DESC, talent_id でソート"
            },
            {
                "step": "Step 5: マッチングスコア振り分け",
                "description": "ランキング位置に応じてマッチングスコア（86-99.7点）を振り分け",
                "talent_count": len(final_results),
                "details": "1-3位: 97.0-99.7点, 4-10位: 93.0-96.9点, 11-20位: 89.0-92.9点, 21-30位: 86.0-88.9点"
            }
        ]

        debug_data = {
            "input_conditions": input_conditions,
            "step_calculations": step_calculations,
            "final_results": final_results,
            "summary": {
                "total_talents": len(final_results),
                "recommended_count": len(recommended_talent_ids),
                "cm_competing_count": sum(1 for status in cm_status_map.values() if status),
                "average_score": sum(r["matching_score"] for r in final_results) / len(final_results) if final_results else 0
            }
        }

        return final_results, debug_data