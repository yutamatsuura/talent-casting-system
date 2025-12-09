"""Phase B移行後の動作確認テスト"""
import asyncio
import os
import sys
from datetime import datetime

# プロジェクトのルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 環境変数読み込み
from dotenv import load_dotenv
load_dotenv()

async def test_matching_api():
    """標準エンドポイントのPhase B移行動作確認"""
    import httpx

    API_BASE = os.getenv("API_BASE_URL", "http://localhost:8432")

    print("=" * 80)
    print("Phase B移行後の動作確認テスト")
    print("=" * 80)
    print()

    # テストデータ
    test_form_data = {
        "industry": "化粧品・ヘアケア・オーラルケア",
        "target_segments": "女性20-34歳",
        "purpose": "新商品のプロモーション",
        "budget": "1,000万円〜3,000万円未満",
        "company_name": "株式会社テストクライアント",
        "contact_name": "山田太郎",
        "email": "test@example.com",
        "phone": "03-1234-5678",
        "genre_preference": "interest",
        "preferred_genres": ["女優", "モデル"],
        "session_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"[1] APIベースURL: {API_BASE}")
        print(f"[2] テスト条件:")
        print(f"    - 業種: {test_form_data['industry']}")
        print(f"    - ターゲット層: {test_form_data['target_segments']}")
        print(f"    - 予算: {test_form_data['budget']}")
        print()

        # ヘルスチェック
        print("[3] ヘルスチェック...")
        try:
            health_response = await client.get(f"{API_BASE}/api/health")
            if health_response.status_code == 200:
                print("    ✅ API稼働中")
            else:
                print(f"    ❌ APIエラー (status: {health_response.status_code})")
                return
        except Exception as e:
            print(f"    ❌ API接続エラー: {e}")
            return

        print()

        # Phase B移行後の標準エンドポイントテスト
        print("[4] Phase B移行後の標準エンドポイント `/api/matching` テスト...")
        try:
            start_time = datetime.now()
            matching_response = await client.post(
                f"{API_BASE}/api/matching",
                json=test_form_data
            )
            end_time = datetime.now()

            elapsed_time = (end_time - start_time).total_seconds() * 1000

            if matching_response.status_code == 200:
                data = matching_response.json()
                print(f"    ✅ マッチング成功")
                print(f"    📊 処理時間: {data.get('processing_time_ms', 0):.2f}ms (計測: {elapsed_time:.2f}ms)")
                print(f"    📋 結果数: {data.get('total_results', 0)}名")
                print(f"    🆔 セッションID: {data.get('session_id', 'N/A')}")

                # パフォーマンス判定
                processing_time = data.get('processing_time_ms', 0)
                if processing_time < 3000:
                    print(f"    🎯 パフォーマンス: 目標達成 (<3秒) ✅")
                elif processing_time < 5000:
                    print(f"    ⚠️  パフォーマンス: 改善必要 (<5秒)")
                else:
                    print(f"    ❌ パフォーマンス: 目標未達 (>5秒)")

                print()
                print("    上位3名:")
                for i, talent in enumerate(data.get('results', [])[:3]):
                    print(f"      {i+1}位: {talent['name']} ({talent['category']}) - "
                          f"スコア: {talent['matching_score']:.1f} "
                          f"{'[おすすめ]' if talent.get('is_recommended') else ''}"
                          f"{'[CM出演中]' if talent.get('is_currently_in_cm') else ''}")

                print()
                print("=" * 80)
                print("✅ Phase B移行成功: すべてのテストがパスしました")
                print("=" * 80)

            else:
                print(f"    ❌ マッチングエラー (status: {matching_response.status_code})")
                print(f"    エラー詳細: {matching_response.text}")

        except Exception as e:
            print(f"    ❌ マッチングエラー: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_matching_api())
