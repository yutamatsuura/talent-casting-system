#!/usr/bin/env python3
"""
パフォーマンステスト環境セットアップスクリプト
効率的なチューニング作業のためのツール群を自動設定
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """テスト用依存関係のインストール"""
    print("📦 パフォーマンステスト用パッケージをインストール中...")

    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "-r", "requirements-testing.txt"
        ], check=True)
        print("✅ 依存関係インストール完了")
    except subprocess.CalledProcessError as e:
        print(f"❌ インストール失敗: {e}")
        return False
    return True

def create_test_config():
    """テスト設定ファイル作成"""
    config_content = """
# パフォーマンステスト設定
[test_settings]
api_base_url = http://localhost:8432
iterations = 5
timeout_seconds = 30
concurrent_users = 1

[monitoring]
dashboard_port = 8433
metrics_interval = 10
alert_thresholds_cpu = 80.0
alert_thresholds_memory = 85.0
alert_thresholds_connections = 20

[database]
connection_pool_size = 10
max_connections = 30
connection_timeout = 30

[output]
results_directory = ./performance_results
keep_history_count = 50
auto_cleanup = true
"""

    config_path = Path("performance_test_config.ini")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

    print(f"✅ テスト設定ファイル作成: {config_path}")
    return True

def create_results_directory():
    """結果保存ディレクトリ作成"""
    results_dir = Path("./performance_results")
    results_dir.mkdir(exist_ok=True)
    print(f"✅ 結果ディレクトリ作成: {results_dir}")

    # サブディレクトリ作成
    subdirs = ["benchmarks", "monitoring", "reports"]
    for subdir in subdirs:
        (results_dir / subdir).mkdir(exist_ok=True)

    return True

def create_run_scripts():
    """実行スクリプト作成"""

    # ベンチマーク実行スクリプト
    benchmark_script = """#!/bin/bash
echo "🚀 パフォーマンスベンチマーク開始"
echo "対象API: http://localhost:8432"
echo "==========================================="

# APIサーバーが起動しているかチェック
if ! curl -s http://localhost:8432/api/health > /dev/null; then
    echo "❌ APIサーバーが起動していません"
    echo "先にbackendサーバーを起動してください: uvicorn app.main:app --host 0.0.0.0 --port 8432"
    exit 1
fi

echo "✅ APIサーバー確認完了"

# ベンチマーク実行
python performance_test_suite.py

echo "📊 ベンチマーク完了 - performance_results/benchmarks/ を確認してください"
"""

    with open("run_benchmark.sh", "w") as f:
        f.write(benchmark_script)

    os.chmod("run_benchmark.sh", 0o755)

    # 監視ダッシュボード実行スクリプト
    monitoring_script = """#!/bin/bash
echo "🖥️ パフォーマンス監視ダッシュボード開始"
echo "ダッシュボードURL: http://localhost:8433"
echo "==========================================="

python monitoring_dashboard.py
"""

    with open("run_monitoring.sh", "w") as f:
        f.write(monitoring_script)

    os.chmod("run_monitoring.sh", 0o755)

    print("✅ 実行スクリプト作成完了:")
    print("   - run_benchmark.sh (ベンチマーク実行)")
    print("   - run_monitoring.sh (リアルタイム監視)")

    return True

def create_usage_guide():
    """使用方法ガイド作成"""
    guide_content = """# パフォーマンステストツール使用ガイド

## 🎯 概要
このツールセットは、タレントキャスティングシステムの効率的なチューニング作業をサポートします。

## 🚀 クイックスタート

### 1. 環境セットアップ
```bash
# セットアップスクリプト実行（初回のみ）
python setup_performance_testing.py

# 依存関係インストール確認
pip install -r requirements-testing.txt
```

### 2. APIサーバー起動
```bash
# バックエンドサーバーを先に起動
cd backend/
uvicorn app.main:app --host 0.0.0.0 --port 8432
```

### 3. ベンチマーク実行
```bash
# 自動ベンチマーク実行
./run_benchmark.sh

# または手動実行
python performance_test_suite.py
```

### 4. リアルタイム監視
```bash
# 監視ダッシュボード起動
./run_monitoring.sh

# ブラウザで http://localhost:8433 にアクセス
```

## 📊 出力結果の見方

### ベンチマーク結果
- `performance_results/benchmarks/` に保存
- JSON形式で詳細な統計情報
- レスポンス時間、CPU使用率、結果一貫性など

### 重要な指標
1. **平均レスポンス時間**: 3秒以下が目標
2. **95%ile レスポンス時間**: 5秒以下が目標
3. **結果一貫性スコア**: 80%以上が理想
4. **CPU使用率変化**: +20%以下が適切

### チューニング推奨事項
ツールが自動生成する推奨事項：
- ⚠️ 5秒超過 → インデックス最適化検討
- 📈 3秒超過 → クエリ最適化検討
- 🔄 一貫性低下 → マッチングロジック確認
- 📊 実行時間ばらつき → 負荷分散検討

## 🛠️ カスタマイズ

### テスト設定変更
`performance_test_config.ini` を編集：
```ini
[test_settings]
iterations = 3          # 実行回数（少なめで高速テスト）
concurrent_users = 5    # 同時ユーザー数（負荷テスト）
timeout_seconds = 15    # タイムアウト設定
```

### 監視しきい値調整
```ini
[monitoring]
alert_thresholds_cpu = 70.0        # CPU警告しきい値
alert_thresholds_memory = 80.0     # メモリ警告しきい値
alert_thresholds_connections = 15  # DB接続数警告
```

## 🎭 テストケース

### 定義済みシナリオ
1. **高負荷**: 化粧品業界 × 女性20-34歳（人気の組み合わせ）
2. **中負荷**: 食品業界 × 女性35-49歳（一般的な組み合わせ）
3. **低負荷**: 金融業界 × 男性50-69歳（ニッチな組み合わせ）
4. **複雑**: 自動車業界 × 複数ターゲット（複雑な処理）

### カスタムテスト追加
`performance_test_suite.py` の `_define_test_cases()` を編集

## 📈 継続的改善

### 定期実行（推奨）
```bash
# 週次ベンチマーク（crontab例）
0 2 * * 1 cd /path/to/backend && ./run_benchmark.sh

# デプロイ前チェック
git add . && ./run_benchmark.sh && git commit -m "performance check passed"
```

### パフォーマンス履歴管理
- 結果ファイルは自動タイムスタンプ付き
- 最新50件を自動保持（設定変更可能）
- 長期トレンド分析用にGit管理推奨

## 🔧 トラブルシューティング

### よくある問題
1. **"APIサーバーが起動していません"**
   - `uvicorn app.main:app --port 8432` でバックエンド起動

2. **"依存関係エラー"**
   - `pip install -r requirements-testing.txt` 再実行

3. **"DB接続エラー"**
   - DATABASE_URL環境変数確認
   - PostgreSQL(Neon)接続状況確認

4. **"メモリ不足警告"**
   - テスト実行頻度を下げる
   - iterationsを3回程度に減らす

### ログ確認
- 詳細ログ: `performance_results/logs/`
- エラー詳細: コンソール出力確認

## 💡 効率的な使い方

### 日常的なチューニング
1. 機能追加後: 軽量ベンチマーク（iterations=3）
2. 週次定期: フル ベンチマーク（iterations=5）
3. 本番前: 負荷テスト（concurrent_users=10）

### パフォーマンス目標
- **開発環境**: 平均2秒以下
- **ステージング**: 平均1.5秒以下
- **本番環境**: 平均1秒以下

効率的なチューニング作業をサポートします！
"""

    with open("PERFORMANCE_TESTING_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide_content)

    print("✅ 使用ガイド作成: PERFORMANCE_TESTING_GUIDE.md")
    return True

def main():
    """メインセットアップ処理"""
    print("🎯 タレントキャスティングシステム パフォーマンステスト環境セットアップ")
    print("=" * 70)

    steps = [
        ("依存関係インストール", install_requirements),
        ("テスト設定ファイル作成", create_test_config),
        ("結果保存ディレクトリ作成", create_results_directory),
        ("実行スクリプト作成", create_run_scripts),
        ("使用ガイド作成", create_usage_guide)
    ]

    for step_name, step_func in steps:
        print(f"\n📝 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} 失敗")
            return False

    print("\n" + "=" * 70)
    print("🎉 パフォーマンステスト環境セットアップ完了！")
    print("\n📚 次のステップ:")
    print("1. APIサーバー起動: uvicorn app.main:app --host 0.0.0.0 --port 8432")
    print("2. ベンチマーク実行: ./run_benchmark.sh")
    print("3. 監視ダッシュボード: ./run_monitoring.sh")
    print("\n📖 詳細な使用方法: PERFORMANCE_TESTING_GUIDE.md を参照")

    return True

if __name__ == "__main__":
    main()