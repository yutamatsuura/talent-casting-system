"""統合テストスクリプト - 全スライス実データ検証
作成日: 2025-11-28
目的: 実装された全スライスを実際のDBデータで統合テスト

テスト対象:
1. スライス1: GET /api/health - ヘルスチェックAPI
2. スライス2: GET /api/industries, GET /api/target-segments - マスターデータAPI
3. スライス3: POST /api/matching - 5段階マッチングエンジン

要件:
- 実データベースでテスト（モック禁止）
- パフォーマンステスト（POST /api/matching < 3秒）
- 実データ4,819件での動作確認
- エラーケースも含む完全テスト
"""
import asyncio
import httpx
import time
from pathlib import Path
from typing import Dict, List, Any


# ===== 設定 =====
API_BASE_URL = "http://localhost:8432"
TIMEOUT = 30.0  # 30秒タイムアウト
PERFORMANCE_TARGET = 3.0  # マッチングAPIの目標レスポンス時間（秒）


# ===== テスト結果管理 =====
class TestResult:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors: List[Dict[str, Any]] = []

    def add_pass(self, test_name: str, duration: float = 0):
        self.total += 1
        self.passed += 1
        print(f"✅ PASS: {test_name} ({duration:.3f}s)")

    def add_fail(self, test_name: str, error: str, duration: float = 0):
        self.total += 1
        self.failed += 1
        self.errors.append({
            "test": test_name,
            "error": error,
            "duration": duration
        })
        print(f"❌ FAIL: {test_name} ({duration:.3f}s)")
        print(f"   Error: {error}")

    def print_summary(self):
        print("\n" + "="*80)
        print("📊 統合テスト実行結果")
        print("="*80)
        print(f"Total Tests: {self.total}")
        print(f"✅ Passed: {self.passed}/{self.total}")
        print(f"❌ Failed: {self.failed}/{self.total}")

        if self.failed > 0:
            print("\n🔍 失敗詳細:")
            for i, err in enumerate(self.errors, 1):
                print(f"\n{i}. {err['test']}")
                print(f"   Duration: {err['duration']:.3f}s")
                print(f"   Error: {err['error']}")

        print("\n" + "="*80)
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"成功率: {success_rate:.1f}%")
        print("="*80 + "\n")


# ===== ヘルパー関数 =====
async def measure_time(func):
    """関数実行時間を計測"""
    start = time.time()
    result = await func()
    duration = time.time() - start
    return result, duration


# ===== スライス1: ヘルスチェックAPI =====
async def test_slice_1_health_check(client: httpx.AsyncClient, result: TestResult):
    """スライス1: GET /api/health のテスト"""
    print("\n" + "="*80)
    print("📋 スライス1: ヘルスチェックAPI")
    print("="*80)

    # Test 1-1: 正常系 - ヘルスチェック
    try:
        response, duration = await measure_time(
            lambda: client.get(f"{API_BASE_URL}/api/health")
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy" and "database" in data:
                result.add_pass("1-1: ヘルスチェック正常系", duration)
            else:
                result.add_fail("1-1: ヘルスチェック正常系", f"不正なレスポンス: {data}", duration)
        else:
            result.add_fail("1-1: ヘルスチェック正常系", f"Status: {response.status_code}", duration)
    except Exception as e:
        result.add_fail("1-1: ヘルスチェック正常系", str(e))


# ===== スライス2: マスターデータAPI =====
async def test_slice_2_master_data(client: httpx.AsyncClient, result: TestResult):
    """スライス2: GET /api/industries, GET /api/target-segments のテスト"""
    print("\n" + "="*80)
    print("📋 スライス2: マスターデータAPI")
    print("="*80)

    # Test 2-1: GET /api/industries
    try:
        response, duration = await measure_time(
            lambda: client.get(f"{API_BASE_URL}/api/industries")
        )

        if response.status_code == 200:
            data = response.json()
            # 実際のレスポンス形式: {"total": n, "industries": [...]}
            if isinstance(data, dict) and "industries" in data and "total" in data:
                industries = data["industries"]
                if len(industries) > 0:
                    # 業種データの構造検証
                    first_item = industries[0]
                    required_fields = ["id", "name"]
                    if all(field in first_item for field in required_fields):
                        result.add_pass(f"2-1: GET /api/industries ({data['total']}件)", duration)
                    else:
                        result.add_fail("2-1: GET /api/industries", f"必須フィールド不足: {first_item}", duration)
                else:
                    result.add_fail("2-1: GET /api/industries", "空のデータ", duration)
            else:
                result.add_fail("2-1: GET /api/industries", f"不正な形式: {data}", duration)
        else:
            result.add_fail("2-1: GET /api/industries", f"Status: {response.status_code}", duration)
    except Exception as e:
        result.add_fail("2-1: GET /api/industries", str(e))

    # Test 2-2: GET /api/target-segments
    try:
        response, duration = await measure_time(
            lambda: client.get(f"{API_BASE_URL}/api/target-segments")
        )

        if response.status_code == 200:
            data = response.json()
            # 実際のレスポンス形式: {"total": n, "items": [...]}
            if isinstance(data, dict) and "items" in data and "total" in data:
                items = data["items"]
                if len(items) > 0:
                    # ターゲット層データの構造検証
                    first_item = items[0]
                    required_fields = ["id", "code", "name", "gender", "age_range"]
                    if all(field in first_item for field in required_fields):
                        result.add_pass(f"2-2: GET /api/target-segments ({data['total']}件)", duration)
                    else:
                        result.add_fail("2-2: GET /api/target-segments", f"必須フィールド不足: {first_item}", duration)
                else:
                    result.add_fail("2-2: GET /api/target-segments", "空のデータ", duration)
            else:
                result.add_fail("2-2: GET /api/target-segments", f"不正な形式: {data}", duration)
        else:
            result.add_fail("2-2: GET /api/target-segments", f"Status: {response.status_code}", duration)
    except Exception as e:
        result.add_fail("2-2: GET /api/target-segments", str(e))


# ===== スライス3: マッチングエンジン =====
async def test_slice_3_matching_engine(client: httpx.AsyncClient, result: TestResult):
    """スライス3: POST /api/matching のテスト"""
    print("\n" + "="*80)
    print("📋 スライス3: 5段階マッチングエンジン")
    print("="*80)

    # まずエンドポイントの存在確認
    try:
        test_response = await client.post(f"{API_BASE_URL}/api/matching", json={})
        if test_response.status_code == 404:
            print("⚠️  マッチングAPI未実装のため、スライス3のテストをスキップします")
            result.add_fail("3-1: POST /api/matching", "エンドポイント未実装 (404)")
            result.add_fail("3-2: マッチング結果上限検証", "エンドポイント未実装 (404)")
            result.add_fail("3-3: Top3スコア範囲検証", "エンドポイント未実装 (404)")
            return
    except Exception:
        pass

    # Test 3-1: 正常系 - 基本マッチング
    try:
        payload = {
            "industry_id": 1,  # 化粧品・ヘアケア・オーラルケア
            "target_segment_ids": [1, 2],  # 女性20-34, 女性35-49
            "budget_max": 30000000  # 3,000万円
        }

        response, duration = await measure_time(
            lambda: client.post(f"{API_BASE_URL}/api/matching", json=payload)
        )

        if response.status_code == 200:
            data = response.json()

            # レスポンス構造検証
            if isinstance(data, list) and len(data) > 0:
                first_talent = data[0]
                required_fields = [
                    "talent_id", "name", "category", "matching_score",
                    "base_power_score", "image_adjustment", "final_score",
                    "money_max_one_year"
                ]

                if all(field in first_talent for field in required_fields):
                    # パフォーマンステスト
                    if duration < PERFORMANCE_TARGET:
                        result.add_pass(f"3-1: POST /api/matching 正常系 ({len(data)}件)", duration)
                    else:
                        result.add_fail(
                            "3-1: POST /api/matching 正常系",
                            f"パフォーマンス基準未達成: {duration:.3f}s > {PERFORMANCE_TARGET}s",
                            duration
                        )
                else:
                    result.add_fail("3-1: POST /api/matching 正常系", f"必須フィールド不足: {first_talent}", duration)
            else:
                result.add_fail("3-1: POST /api/matching 正常系", f"空のデータまたは不正な形式: {data}", duration)
        else:
            result.add_fail("3-1: POST /api/matching 正常系", f"Status: {response.status_code}", duration)
    except Exception as e:
        result.add_fail("3-1: POST /api/matching 正常系", str(e))

    # Test 3-2: マッチング結果件数検証（最大30件）
    try:
        payload = {
            "industry_id": 1,
            "target_segment_ids": [1, 2],
            "budget_max": 100000000  # 1億円（より多くのタレントが対象）
        }

        response, duration = await measure_time(
            lambda: client.post(f"{API_BASE_URL}/api/matching", json=payload)
        )

        if response.status_code == 200:
            data = response.json()
            if len(data) <= 30:
                result.add_pass(f"3-2: マッチング結果上限検証 ({len(data)}件 <= 30件)", duration)
            else:
                result.add_fail("3-2: マッチング結果上限検証", f"上限超過: {len(data)}件 > 30件", duration)
        else:
            result.add_fail("3-2: マッチング結果上限検証", f"Status: {response.status_code}", duration)
    except Exception as e:
        result.add_fail("3-2: マッチング結果上限検証", str(e))

    # Test 3-3: スコア範囲検証（1-3位: 97-99.7点）
    try:
        payload = {
            "industry_id": 1,
            "target_segment_ids": [1],
            "budget_max": 50000000
        }

        response, duration = await measure_time(
            lambda: client.post(f"{API_BASE_URL}/api/matching", json=payload)
        )

        if response.status_code == 200:
            data = response.json()
            if len(data) >= 3:
                top3_scores = [t["matching_score"] for t in data[:3]]
                all_valid = all(97.0 <= score <= 99.7 for score in top3_scores)

                if all_valid:
                    result.add_pass(f"3-3: Top3スコア範囲検証 ({top3_scores})", duration)
                else:
                    result.add_fail("3-3: Top3スコア範囲検証", f"スコア範囲外: {top3_scores}", duration)
            else:
                result.add_fail("3-3: Top3スコア範囲検証", f"結果不足: {len(data)}件 < 3件", duration)
        else:
            result.add_fail("3-3: Top3スコア範囲検証", f"Status: {response.status_code}", duration)
    except Exception as e:
        result.add_fail("3-3: Top3スコア範囲検証", str(e))


# ===== エラーケーステスト =====
async def test_error_cases(client: httpx.AsyncClient, result: TestResult):
    """エラーケーステスト"""
    print("\n" + "="*80)
    print("📋 エラーケーステスト")
    print("="*80)

    # マッチングAPI存在確認
    try:
        test_response = await client.post(f"{API_BASE_URL}/api/matching", json={})
        if test_response.status_code == 404:
            print("⚠️  マッチングAPI未実装のため、エラーケーステストをスキップします")
            result.add_fail("E-1: 不正なindustry_id", "エンドポイント未実装 (404)")
            result.add_fail("E-2: 空のtarget_segment_ids", "エンドポイント未実装 (404)")
            result.add_fail("E-3: 負のbudget_max", "エンドポイント未実装 (404)")
            return
    except Exception:
        pass

    # Test E-1: 不正なindustry_id
    try:
        payload = {
            "industry_id": 99999,
            "target_segment_ids": [1],
            "budget_max": 10000000
        }

        response, duration = await measure_time(
            lambda: client.post(f"{API_BASE_URL}/api/matching", json=payload)
        )

        # 400または422エラーを期待
        if response.status_code in [400, 422]:
            result.add_pass(f"E-1: 不正なindustry_id (Status: {response.status_code})", duration)
        else:
            result.add_fail("E-1: 不正なindustry_id", f"予期しないStatus: {response.status_code}", duration)
    except Exception as e:
        result.add_fail("E-1: 不正なindustry_id", str(e))

    # Test E-2: 空のtarget_segment_ids
    try:
        payload = {
            "industry_id": 1,
            "target_segment_ids": [],
            "budget_max": 10000000
        }

        response, duration = await measure_time(
            lambda: client.post(f"{API_BASE_URL}/api/matching", json=payload)
        )

        if response.status_code in [400, 422]:
            result.add_pass(f"E-2: 空のtarget_segment_ids (Status: {response.status_code})", duration)
        else:
            result.add_fail("E-2: 空のtarget_segment_ids", f"予期しないStatus: {response.status_code}", duration)
    except Exception as e:
        result.add_fail("E-2: 空のtarget_segment_ids", str(e))

    # Test E-3: 負のbudget_max
    try:
        payload = {
            "industry_id": 1,
            "target_segment_ids": [1],
            "budget_max": -1000
        }

        response, duration = await measure_time(
            lambda: client.post(f"{API_BASE_URL}/api/matching", json=payload)
        )

        if response.status_code in [400, 422]:
            result.add_pass(f"E-3: 負のbudget_max (Status: {response.status_code})", duration)
        else:
            result.add_fail("E-3: 負のbudget_max", f"予期しないStatus: {response.status_code}", duration)
    except Exception as e:
        result.add_fail("E-3: 負のbudget_max", str(e))


# ===== メイン実行 =====
async def main():
    """統合テストメイン"""
    print("\n" + "="*80)
    print("🚀 統合テスト開始")
    print("="*80)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Timeout: {TIMEOUT}s")
    print(f"Performance Target: {PERFORMANCE_TARGET}s (POST /api/matching)")
    print("="*80)

    result = TestResult()

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # スライス1: ヘルスチェック
        await test_slice_1_health_check(client, result)

        # スライス2: マスターデータ
        await test_slice_2_master_data(client, result)

        # スライス3: マッチングエンジン
        await test_slice_3_matching_engine(client, result)

        # エラーケース
        await test_error_cases(client, result)

    # 結果サマリー表示
    result.print_summary()

    # 終了コード
    return 0 if result.failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
