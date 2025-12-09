# パフォーマンステストツール集

タレントキャスティングシステムの効率的なチューニング作業をサポートするツールセットです。

## 🚀 クイックスタート（3分で開始）

### 1. 一発セットアップ
```bash
cd backend/
python setup_performance_testing.py
```

### 2. APIサーバー起動（別ターミナル）
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8432
```

### 3. クイックテスト実行
```bash
python quick_performance_check.py
```

## 🎯 ツール一覧

### 📊 クイックパフォーマンスチェック
**ファイル**: `quick_performance_check.py`
**用途**: 日常的な軽量テスト（3分で完了）

```bash
python quick_performance_check.py
```

**出力例**:
```
🏆 総合評価: ✅ Bグレード (良好)
⏱️ 平均レスポンス時間: 1.234秒
💡 推奨アクション: ✅ 良好なパフォーマンス - 軽微な最適化で更なる向上可能
```

### 🔬 詳細ベンチマークスイート
**ファイル**: `performance_test_suite.py`
**用途**: 包括的な性能分析（15分程度）

```bash
python performance_test_suite.py
```

**特徴**:
- 4つの異なる負荷パターンをテスト
- 統計的分析とトレンド検出
- 具体的なチューニング推奨事項
- JSON形式の詳細レポート出力

### 🖥️ リアルタイム監視ダッシュボード
**ファイル**: `monitoring_dashboard.py`
**用途**: 本番運用時の継続的監視

```bash
python monitoring_dashboard.py
```

**機能**:
- WebブラウザでGUI表示 (`http://localhost:8433`)
- CPU、メモリ、DB接続数のリアルタイム監視
- アラート機能と自動推奨事項
- 30分間のトレンド分析

## 📈 パフォーマンス目標値

| 環境 | 目標レスポンス時間 | 評価基準 |
|------|-------------------|----------|
| 開発環境 | 平均2秒以下 | Cグレード以上 |
| ステージング | 平均1.5秒以下 | Bグレード以上 |
| 本番環境 | 平均1秒以下 | Aグレード |

## 🎭 テストシナリオ

### 定義済みテストケース
1. **人気ケース**: 化粧品業界 × 女性20-34歳（高負荷）
2. **一般ケース**: 食品業界 × 女性35-49歳（中負荷）
3. **ニッチケース**: 金融業界 × 男性50-69歳（低負荷）
4. **複雑ケース**: 自動車業界 × 複数ターゲット（処理複雑）

## 💡 効率的な使用方法

### 日常的なワークフロー
```bash
# 1. 機能開発後の確認（毎回）
python quick_performance_check.py

# 2. 週次定期チェック（詳細分析）
python performance_test_suite.py

# 3. 本番デプロイ前（最終確認）
python performance_test_suite.py --iterations=10
```

### CI/CD統合例
```bash
# Git コミット前の自動チェック
git add .
python quick_performance_check.py && git commit -m "feature: パフォーマンステスト通過"
```

## 🔧 設定カスタマイズ

### テスト頻度調整
```python
# quick_performance_check.py 内
for i in range(3):  # ← 実行回数（軽量: 3回、詳細: 5回）
```

### APIエンドポイント変更
```python
# 各ツール共通
checker = QuickPerformanceCheck("http://your-api-server:8432")
```

### アラートしきい値調整
```python
# monitoring_dashboard.py 内
self.alert_thresholds = {
    "response_time": 3.0,  # レスポンス時間警告（秒）
    "cpu_usage": 80.0,     # CPU使用率警告（%）
    "memory_usage": 85.0,  # メモリ使用率警告（%）
    "active_connections": 20  # DB接続数警告
}
```

## 📊 結果の読み方

### グレード評価基準
- **Aグレード (🚀)**: 平均1秒以下、最大2秒以下 → 優秀
- **Bグレード (✅)**: 平均2秒以下、最大3秒以下 → 良好
- **Cグレード (⚠️)**: 平均3秒以下、最大5秒以下 → 普通
- **Dグレード (❌)**: 平均3秒超過または最大5秒超過 → 要改善

### 推奨アクション
- **🔧 緊急**: 5秒超過 → インデックス最適化必須
- **📈 改善推奨**: 3秒超過 → SQLクエリ最適化検討
- **⚡ 継続監視**: 2-3秒 → 定期的なパフォーマンス確認
- **🚀 現状維持**: 1秒以下 → 最適化済み

## 🛠️ トラブルシューティング

### よくある問題と解決策

**問題1**: `❌ APIサーバー接続失敗`
```bash
# 解決方法
uvicorn app.main:app --host 0.0.0.0 --port 8432
```

**問題2**: `ModuleNotFoundError: requests`
```bash
# 解決方法
pip install -r requirements-testing.txt
```

**問題3**: `Database connection error`
```bash
# 解決方法: 環境変数確認
echo $DATABASE_URL
# Neon PostgreSQL接続文字列が正しく設定されているか確認
```

**問題4**: パフォーマンスが突然悪化
```bash
# 診断手順
1. python quick_performance_check.py  # 現状確認
2. python monitoring_dashboard.py     # リアルタイム監視
3. データベース接続数・メモリ使用量をチェック
4. 過去のベンチマーク結果と比較
```

## 📚 詳細ドキュメント

完全な使用方法は以下を参照:
- `PERFORMANCE_TESTING_GUIDE.md` - 詳細使用ガイド
- `performance_test_config.ini` - 設定ファイル
- `performance_results/` - 過去の結果履歴

## 🎯 推奨運用パターン

### 開発チーム向け
```bash
# 毎日の開発後
python quick_performance_check.py

# 金曜日の週次チェック
python performance_test_suite.py

# デプロイ前の最終確認
./run_benchmark.sh
```

### 本番監視担当向け
```bash
# 常時監視（画面表示）
python monitoring_dashboard.py

# 定期レポート（週次・月次）
python performance_test_suite.py --iterations=10
```

効率的なチューニング作業を支援します！ 🚀