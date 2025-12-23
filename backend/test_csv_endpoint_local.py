#!/usr/bin/env python3
"""
CSV診断エンドポイントのローカルテスト
エラーの原因を確認
"""
import asyncio
import asyncpg
import os
import json
import traceback
from dotenv import load_dotenv

load_dotenv()

async def test_csv_endpoint_local():
    """CSV診断エンドポイントのエラーをローカルで再現"""
    try:
        # データベースに接続
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            db_url = "postgresql://neondb_owner:npg_5X1MlRZzVheF@ep-sparkling-smoke-a183z7h8-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

        conn = await asyncpg.connect(db_url)

        submission_id = 330

        # フォーム送信データを取得
        submission_query = """
            SELECT id, industry, target_segment, usage_purpose, budget_range
            FROM form_submissions
            WHERE id = $1
        """

        result = await conn.fetch(submission_query, submission_id)

        if not result:
            print(f"❌ 送信ID {submission_id} が見つかりません")
            await conn.close()
            return

        submission = result[0]
        print(f"✅ 送信データ取得:")
        print(f"   ID: {submission['id']}")
        print(f"   業種: {submission['industry']}")
        print(f"   ターゲット: {submission['target_segment']}")
        print(f"   目的: {submission['usage_purpose']}")
        print(f"   予算: {submission['budget_range']}")

        # enhanced_matching_debugと同じロジックを実行
        from app.services.enhanced_matching_debug import EnhancedMatchingDebug

        debug_matcher = EnhancedMatchingDebug()

        print(f"\n🔍 enhanced_matching_debug実行中...")
        detailed_results = await debug_matcher.generate_complete_talent_analysis(
            industry=submission['industry'],
            target_segments=[submission['target_segment']],
            purpose=submission['usage_purpose'],
            budget=submission['budget_range']
        )

        print(f"✅ 分析完了: {len(detailed_results)}件のタレントデータ")

        if detailed_results:
            # 最初の3件の結果を表示
            print(f"\n📈 サンプル結果 (最初の3件):")
            for i, result in enumerate(detailed_results[:3], 1):
                print(f"{i}. {result.get('タレント名', 'N/A')} - VR: {result.get('VR人気度', 0)}, TPR: {result.get('TPRスコア', 0)}")

            # CSV用のデータ構造を作成
            csv_export_data = []
            for talent in detailed_results:
                row = [
                    talent.get('タレント名', ''),
                    talent.get('VR人気度', 0),
                    talent.get('TPRスコア', 0),
                    talent.get('従来スコア', 0),  # (VR人気度 + TPRスコア) / 2
                    talent.get('おもしろさ', 0),
                    talent.get('清潔感', 0),
                    talent.get('個性的な', 0),
                    talent.get('信頼できる', 0),
                    talent.get('かわいい', 0),
                    talent.get('カッコいい', 0),
                    talent.get('大人の魅力', 0),
                    talent.get('従来順位', 0),
                    talent.get('業種別イメージ', ''),
                    talent.get('最終スコア', 0),
                    talent.get('最終順位', 0),
                    talent.get('ジャンル', '')
                ]
                csv_export_data.append(row)

            print(f"\n📊 CSV用データ準備完了: {len(csv_export_data)}行")
            print(f"   最初の行: {csv_export_data[0] if csv_export_data else 'データなし'}")

            # APIレスポンス形式でデータを返す
            response_data = {
                "message": "CSV診断結果の取得が成功しました",
                "submission_id": submission_id,
                "csv_export_data": csv_export_data,
                "total_talents": len(csv_export_data),
                "analysis_details": {
                    "industry": submission['industry'],
                    "target_segment": submission['target_segment'],
                    "purpose": submission['usage_purpose'],
                    "budget": submission['budget_range']
                }
            }

            print(f"\n✅ APIレスポンス準備完了")
            print(f"   メッセージ: {response_data['message']}")
            print(f"   タレント数: {response_data['total_talents']}")

        else:
            print("❌ 分析結果が空です")

        await conn.close()

    except Exception as e:
        print(f"❌ エラー: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_csv_endpoint_local())