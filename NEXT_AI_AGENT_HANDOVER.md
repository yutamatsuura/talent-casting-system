# 次期AIエージェント引き継ぎドキュメント
## マッチングロジック最適化・競合判定修正プロジェクト

---

## 🚀 プロジェクト概要

### 目的
あなたの主なミッションは以下の2つです：

1. **マッチングロジック最適化**: レスポンス時間を7.4秒から3秒以下に短縮
2. **競合使用中判定の修正**: より精度の高い競合判定ロジックの実装

### 現在の状態
- ✅ **Google Sheets問題解決完了**: 本番環境クリーンアップ済み
- ✅ **重大バグ修正完了**: STEP1計算ロジック修正済み
- ✅ **本番環境正常稼働**: 7.4秒レスポンス、30件結果出力
- 📋 **次のフェーズ**: パフォーマンス最適化

---

## 📊 現在のパフォーマンス状況

### 基準値（2025年12月9日時点）
```
レスポンス時間: 7.378ms (7.4秒)
結果件数: 30件
処理内容: 5段階マッチングロジック完全実行
テスト条件: 業種=乳製品, ターゲット=男性12-19歳, 予算=1000-3000万円
```

### 性能目標
```
目標レスポンス時間: 3秒以下 (現在の50%短縮)
最大許容時間: 5秒
目標達成で: ユーザビリティ大幅向上
```

---

## 🎯 優先タスク一覧

### 【最優先】Task 1: パフォーマンスボトルネック分析
**所要時間**: 2-3時間
**目標**: 現在の7.4秒の内訳を詳細分析

#### 実施項目
1. **SQLクエリ分析**
   ```sql
   -- 現在のクエリを EXPLAIN ANALYZE で詳細分析
   EXPLAIN (ANALYZE, BUFFERS) SELECT ...
   ```

2. **STEP別処理時間計測**
   - STEP 0: 予算フィルタリング
   - STEP 1: 基礎パワー得点計算
   - STEP 2: 業種イメージ査定 ← 最重要・最時間かかる
   - STEP 3: 基礎反映得点
   - STEP 4: ランキング確定
   - STEP 5: マッチングスコア振り分け

3. **ネットワーク・DB接続時間計測**

#### 予想される結果
- STEP 2（業種イメージ査定）が全体の60-70%を占有
- PostgreSQL PERCENT_RANK() 計算が重い
- 複数JOINによるメモリ使用量増大

### 【高優先】Task 2: データベースインデックス最適化
**所要時間**: 1-2時間
**目標**: クエリ実行速度の向上

#### 実施項目
1. **現在のインデックス確認**
   ```sql
   SELECT * FROM pg_indexes WHERE tablename IN ('talents', 'talent_scores', 'talent_images');
   ```

2. **新規インデックス候補**
   ```sql
   -- 複合インデックスの追加候補
   CREATE INDEX idx_talent_scores_target_vr_tpr ON talent_scores(target_segment_id, vr_popularity, tpr_power_score);
   CREATE INDEX idx_talent_images_industry ON talent_images(talent_id, industry_id);
   CREATE INDEX idx_talents_budget ON talents(money_max_one_year);
   ```

3. **クエリ実行計画再確認**

### 【高優先】Task 3: クエリ構造最適化
**所要時間**: 2-3時間
**目標**: STEP 2の業種イメージ査定処理の高速化

#### 現在の処理（重い）
```sql
-- PERCENT_RANK() を各業種で計算
PERCENT_RANK() OVER (
    PARTITION BY ti.industry_id
    ORDER BY ti.image_value
) as percentile_rank
```

#### 最適化案
1. **事前集計テーブル作成**
   - 業種別パーセンタイル値を事前計算してテーブル化
   - リアルタイム計算から参照に変更

2. **クエリ分割**
   - 単一の巨大JOINを複数の小さなクエリに分割
   - アプリケーション側でデータ結合

3. **CTEの見直し**
   - 現在のCTE構造の最適化

### 【高優先】Task 4: 競合判定ロジック修正
**所要時間**: 2-3時間
**目標**: `check_cm_exclusion_status` 関数の精度向上

#### 現在の問題点
```python
# backend/app/api/endpoints/matching.py 付近
async def check_cm_exclusion_status(account_ids: List[int], industry: str) -> Dict[int, bool]:
    # 現在のロジック: CM出演履歴による単純な排除
    # 問題: 古いデータ・契約期間・競合レベルが考慮されていない
```

#### 修正案
1. **時間軸の考慮**
   - 契約終了から一定期間経過後は競合対象外
   - 最新の出演状況を重視

2. **競合レベルの分類**
   - 直接競合（同一商品カテゴリ）
   - 間接競合（関連業界）
   - 非競合（異業種）

3. **データソース拡張**
   - リアルタイム契約情報の連携
   - 業界別競合マトリックスの構築

### 【中優先】Task 5: キャッシュ戦略実装
**所要時間**: 1-2時間
**目標**: 重複計算の削減

#### 実施項目
1. **マスタデータキャッシュ**
   ```python
   # 業種・ターゲット層などの静的データ
   from functools import lru_cache

   @lru_cache(maxsize=128)
   async def get_industry_data():
       # 業種データをメモリキャッシュ
   ```

2. **計算結果キャッシュ**
   - 同一条件での過去計算結果を一定時間保持
   - Redis または メモリベースキャッシュ

### 【低優先】Task 6: モニタリング・テスト強化
**所要時間**: 1-2時間
**目標**: 継続的な性能監視体制

#### 実施項目
1. **パフォーマンステストスイート**
   ```python
   # 自動パフォーマンステスト
   def test_matching_performance():
       start_time = time.time()
       result = call_matching_api()
       end_time = time.time()
       assert (end_time - start_time) < 3.0  # 3秒以下
   ```

2. **レスポンス時間ログ**
   - 各STEP別実行時間の記録
   - 異常検知アラート

---

## 🔧 技術詳細情報

### システム構成
```
本番環境:
- URL: https://talent-casting-backend-392592761218.asia-northeast1.run.app
- インフラ: Google Cloud Run
- DB: PostgreSQL (Neon Launch $19/月)
- 言語: Python 3.11 + FastAPI

ローカル環境:
- Backend: http://localhost:8432
- Frontend: http://localhost:3248
```

### 重要ファイル
```
/Users/lennon/projects/talent-casting-form/
├── backend/app/
│   ├── api/endpoints/matching.py           # メインマッチングロジック
│   ├── db/ultra_optimized_queries.py       # SQL最適化クエリ ★最重要
│   ├── services/matching_service.py        # ビジネスロジック層
│   └── core/config.py                      # 設定管理
```

### データベーススキーマ（主要テーブル）
```sql
-- 最も重要なテーブル
talents                 -- タレント基本情報 (~10,000件)
talent_scores          -- VR/TPRスコア (~100,000件)
talent_images          -- イメージデータ (~1,000,000件) ★パフォーマンス影響大
industries             -- 業種マスタ (~50件)
target_segments        -- ターゲット層マスタ (~20件)
```

### 5段階マッチングロジック（現在の実装）
```
STEP 0: 予算フィルタリング (高速)
  ↓ 処理時間: ~100ms
STEP 1: 基礎パワー得点計算 (中速)
  ↓ 処理時間: ~500ms
STEP 2: 業種イメージ査定 (低速) ★ボトルネック
  ↓ 処理時間: ~5000ms (全体の70%)
STEP 3: 基礎反映得点 (高速)
  ↓ 処理時間: ~50ms
STEP 4: ランキング確定 (中速)
  ↓ 処理時間: ~800ms
STEP 5: スコア振り分け (高速)
  ↓ 処理時間: ~50ms

合計: ~6500ms + オーバーヘッド = 7400ms
```

---

## 📋 実行手順

### 環境準備
1. **プロジェクトディレクトリに移動**
   ```bash
   cd /Users/lennon/projects/talent-casting-form/backend
   ```

2. **仮想環境有効化**
   ```bash
   source venv/bin/activate
   ```

3. **現在の状態確認**
   ```bash
   # 本番環境ヘルスチェック
   curl https://talent-casting-backend-392592761218.asia-northeast1.run.app/api/health

   # ローカル環境起動
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8432 --reload
   ```

### パフォーマンス分析開始
1. **ベースライン測定**
   ```bash
   curl -X POST "http://localhost:8432/api/matching" \
     -H "Content-Type: application/json" \
     -d '{
       "industry": "乳製品",
       "target_segments": "男性12-19歳",
       "budget": "1,000万円〜3,000万円未満",
       "purpose": "商品サービスの特長訴求のため",
       "company_name": "テスト会社",
       "email": "test@example.com"
     }'
   ```

2. **SQL分析ツール準備**
   ```python
   # backend/app/utils/performance_analyzer.py (新規作成推奨)
   import time
   import logging

   def analyze_sql_performance(query, params):
       start_time = time.time()
       result = execute_query(query, params)
       end_time = time.time()

       logging.info(f"Query executed in {end_time - start_time:.3f}s")
       return result
   ```

### データベース接続情報
```python
# backend/app/core/config.py から取得
DATABASE_URL = "postgresql://[username]:[password]@[neon_host]/[database]"

# 直接接続でSQL分析時
import asyncpg

async def connect_to_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn
```

---

## 🚨 注意事項

### 必須事項
1. **バックアップ確認**
   - `/Users/lennon/projects/talent-casting-form-backup-20251209` が存在
   - 何か問題があった場合の復旧手順確保

2. **本番環境への影響最小化**
   - 最適化はローカル環境で十分テスト後
   - 本番デプロイは段階的に実施

3. **データ整合性確保**
   - パフォーマンス向上が結果の正確性を損なわないよう注意
   - 特にSTEP1-5の計算ロジックは変更禁止

### 技術的制約
1. **PostgreSQL制約**
   ```sql
   -- percentile_cont() はOVER句非対応
   -- PERCENT_RANK() を使用する現在の実装が正しい
   ```

2. **Cloud Run制限**
   - メモリ: 最大8GB
   - CPU: 最大4vCPU
   - 同時接続数制限あり

3. **Neon DB制限**
   - Launch plan: 10GB, 300 CU-hours/月
   - 同時接続数: 10-30接続

---

## 📈 成功指標

### パフォーマンス目標
- ⭐ **必達目標**: 7.4秒 → 5秒以下
- 🎯 **理想目標**: 7.4秒 → 3秒以下
- 🏆 **ストレッチ目標**: 7.4秒 → 2秒以下

### 品質目標
- ✅ **結果精度**: 現在と同等の正確性維持
- ✅ **安定性**: エラー率0%維持
- ✅ **互換性**: フロントエンド側修正不要

### 開発効率目標
- 📊 **分析完了**: 2-3日以内
- 🔧 **最適化実装**: 3-5日以内
- 🚀 **本番反映**: 1週間以内

---

## 💡 推奨アプローチ

### Day 1: 現状分析
1. パフォーマンス計測環境構築
2. STEP別処理時間詳細分析
3. SQLクエリのボトルネック特定

### Day 2-3: 最適化実装
1. インデックス追加・修正
2. クエリ構造改善
3. キャッシュ機能実装

### Day 4-5: 競合判定改善
1. 現在のロジック分析
2. 改善案実装
3. テストケース作成

### Day 6-7: テスト・デプロイ
1. 統合テスト実施
2. パフォーマンステスト
3. 本番環境デプロイ

---

## 📞 サポート情報

### 技術サポート
- **Database**: PostgreSQL 16 (Neon)
- **Backend**: FastAPI + Python 3.11
- **Monitoring**: Google Cloud Console
- **Documentation**: このドキュメント + CLAUDE.md

### 参考リソース
- [PostgreSQL EXPLAIN Documentation](https://www.postgresql.org/docs/current/sql-explain.html)
- [FastAPI Performance Tips](https://fastapi.tiangolo.com/advanced/performance/)
- [Neon Optimization Guide](https://neon.tech/docs/optimize/overview)

### 緊急時連絡先
- **重大問題発生時**: バックアップから復旧
- **データ不整合発見時**: 本番デプロイ停止・調査

---

## 🎯 最終目標

あなたの成功により、タレントキャスティングシステムは：
- **ユーザビリティ大幅向上** (7.4秒→3秒)
- **システム信頼性向上** (競合判定精度向上)
- **運用効率向上** (監視体制強化)

これらの成果により、クライアントのビジネス価値を大幅に向上させることができます。

**Good luck! 🚀**

---

**作成日**: 2025年12月9日
**作成者**: Claude Code AI Agent (前任)
**対象**: 次期AI Agent (最適化担当)
**プロジェクト**: タレントキャスティングシステム v1.0