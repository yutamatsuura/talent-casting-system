"""Phase B詳細パフォーマンステスト"""
import asyncio
import time
from datetime import datetime
from app.db.ultra_optimized_queries import UltraOptimizedMatchingQueries

async def test_ultra_optimized_performance():
    """Phase B実装の各処理のパフォーマンスを詳細計測"""
    print("=" * 80)
    print("Phase B詳細パフォーマンステスト")
    print("=" * 80)
    print()

    # テストパラメータ
    industry = "化粧品・ヘアケア・オーラルケア"
    target_segment = "女性20-34歳"
    budget = "1,000万円〜3,000万円未満"

    print(f"テスト条件:")
    print(f"  - 業種: {industry}")
    print(f"  - ターゲット層: {target_segment}")
    print(f"  - 予算: {budget}")
    print()

    # 合計処理時間計測
    total_start = time.time()

    try:
        # Phase B実行
        phase_b_start = time.time()
        results = await UltraOptimizedMatchingQueries.execute_ultra_optimized_matching_flow(
            industry, target_segment, budget
        )
        phase_b_time = (time.time() - phase_b_start) * 1000

        print(f"✅ Phase B統合マッチング処理: {phase_b_time:.2f}ms")
        print(f"   - 結果数: {len(results)}名")
        print(f"   - 上位3名:")
        for i, talent in enumerate(results[:3]):
            print(f"     {i+1}位: {talent.get('name', 'N/A')} - スコア: {talent.get('matching_score', 0):.1f}")
        print()

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return

    # 合計時間
    total_time = (time.time() - total_start) * 1000
    print(f"📊 合計処理時間: {total_time:.2f}ms")
    print()

    # パフォーマンス評価
    if total_time < 3000:
        print("🎯 パフォーマンス: 目標達成 (<3秒) ✅")
    elif total_time < 5000:
        print("⚠️  パフォーマンス: 改善必要 (<5秒)")
    else:
        print("❌ パフォーマンス: 目標未達 (>5秒)")

    print()
    print("=" * 80)
    print("Phase B詳細パフォーマンステスト完了")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_ultra_optimized_performance())
