# 最適化実装詳細仕様書
生成日: 2025-12-05
制約: **マッチングロジック完全保持**

## 🎯 Phase A: 即効性最適化（推奨実装）

### 1. クエリ統合による接続数削減

#### 現状問題
```python
# 現在：5段階で個別クエリ実行（5+回のDB接続）
step0_results = await execute_budget_filter(budget_max)
step1_results = await execute_base_power(target_segment_id)
step2_results = await execute_image_assessment(industry_id, target_segment_id)
step3_results = await execute_final_scoring(step1_results, step2_results)
step4_results = await execute_ranking(step3_results)
```

#### 最適化提案
```python
# 最適化：1つの統合クエリで全処理（1回のDB接続）
async def execute_unified_matching_query(
    budget_max: int,
    target_segment_id: int,
    industry_id: int
) -> List[TalentMatchResult]:

    unified_query = """
    WITH step0_budget_filter AS (
        -- STEP 0: 予算フィルタリング（ロジック完全保持）
        SELECT talent_id
        FROM talents
        WHERE money_max_one_year <= $1
    ),
    step1_base_power AS (
        -- STEP 1: 基礎パワー得点（ロジック完全保持）
        SELECT
            ts.talent_id,
            (ts.vr_popularity + ts.tpr_power_score) / 2.0 as base_power_score
        FROM talent_scores ts
        INNER JOIN step0_budget_filter bf ON ts.talent_id = bf.talent_id
        WHERE ts.target_segment_id = $2
    ),
    step2_image_assessment AS (
        -- STEP 2: 業界イメージ査定（ロジック完全保持）
        SELECT
            ti.talent_id,
            ti.image_score,
            PERCENT_RANK() OVER (ORDER BY ti.image_score DESC) as percentile_rank,
            CASE
                WHEN PERCENT_RANK() OVER (ORDER BY ti.image_score DESC) <= 0.15 THEN 12.0
                WHEN PERCENT_RANK() OVER (ORDER BY ti.image_score DESC) <= 0.30 THEN 6.0
                WHEN PERCENT_RANK() OVER (ORDER BY ti.image_score DESC) <= 0.50 THEN 3.0
                WHEN PERCENT_RANK() OVER (ORDER BY ti.image_score DESC) <= 0.70 THEN -3.0
                WHEN PERCENT_RANK() OVER (ORDER BY ti.image_score DESC) <= 0.85 THEN -6.0
                ELSE -12.0
            END as image_adjustment
        FROM talent_images ti
        WHERE ti.target_segment_id = $2
          AND ti.industry_id = $3
    ),
    step3_final_scoring AS (
        -- STEP 3: 基礎反映得点（ロジック完全保持）
        SELECT
            bp.talent_id,
            bp.base_power_score,
            ia.image_adjustment,
            bp.base_power_score + COALESCE(ia.image_adjustment, 0) as final_score
        FROM step1_base_power bp
        LEFT JOIN step2_image_assessment ia ON bp.talent_id = ia.talent_id
    )
    -- STEP 4: ランキング確定（ソート順完全保持）
    SELECT
        fs.talent_id,
        fs.base_power_score,
        fs.image_adjustment,
        fs.final_score,
        ma.name_full_for_matching,
        ma.image_url
    FROM step3_final_scoring fs
    INNER JOIN m_account ma ON fs.talent_id = ma.account_id
    ORDER BY fs.final_score DESC, fs.base_power_score DESC, fs.talent_id
    LIMIT 30
    """

    return await conn.fetch(unified_query, budget_max, target_segment_id, industry_id)
```

**期待効果**: 70%高速化（8.4秒 → 2.5秒）

### 2. プリペアドステートメント実装

#### 現状問題
```python
# 現在：動的SQL生成でコンパイルコスト発生
query = f"SELECT * FROM talents WHERE budget <= {budget_max}"
```

#### 最適化実装
```python
# app/db/prepared_statements.py
class PreparedQueries:
    def __init__(self):
        self.unified_matching_query = None

    async def prepare_statements(self, conn):
        """プリペアドステートメント事前準備"""
        self.unified_matching_query = await conn.prepare("""
            WITH step0_budget_filter AS (...)
            -- 上記統合クエリ
        """)

    async def execute_matching(self, budget_max, target_segment_id, industry_id):
        """事前コンパイル済みクエリ実行"""
        return await self.unified_matching_query.fetch(
            budget_max, target_segment_id, industry_id
        )

# app/main.py でアプリ起動時に準備
@app.on_event("startup")
async def prepare_database():
    global prepared_queries
    conn = await get_asyncpg_connection()
    prepared_queries = PreparedQueries()
    await prepared_queries.prepare_statements(conn)
    await conn.close()
```

**期待効果**: 15%高速化

### 3. 接続プール詳細チューニング

#### 現状設定問題
```env
# 現在：汎用的設定
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=10
```

#### 最適化設定
```env
# 最適化：マッチングAPI特化設定
DB_POOL_SIZE=12               # 同時マッチング処理数に最適化
DB_MAX_OVERFLOW=18            # 過剰接続防止
DB_POOL_TIMEOUT=3             # 高速レスポンス優先
DB_POOL_RECYCLE=600           # 10分サイクル（短縮）
DB_POOL_PRE_PING=true         # 接続事前検証
DB_ENGINE_ECHO=false          # SQLログ無効化（本番）
```

#### FastAPI接続最適化
```python
# app/db/connection.py
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=12,
    max_overflow=18,
    pool_timeout=3,
    pool_recycle=600,
    pool_pre_ping=True,
    echo=False,  # 本番はFalse
    future=True
)
```

**期待効果**: 10%高速化

## 🔧 Phase B: 持続的最適化

### 4. 複合インデックス作成

#### 実装SQL
```sql
-- インデックス作成スクリプト
-- performance_indices_phase_b.sql

-- STEP0用：予算フィルタ最適化
CREATE INDEX CONCURRENTLY idx_talents_budget_optimization
ON talents(money_max_one_year, talent_id)
WHERE money_max_one_year IS NOT NULL;

-- STEP1用：基礎パワー計算最適化
CREATE INDEX CONCURRENTLY idx_talent_scores_base_power
ON talent_scores(target_segment_id, talent_id, vr_popularity, tpr_power_score)
WHERE vr_popularity IS NOT NULL AND tpr_power_score IS NOT NULL;

-- STEP2用：業界イメージ最適化
CREATE INDEX CONCURRENTLY idx_talent_images_industry_assessment
ON talent_images(industry_id, target_segment_id, image_score DESC, talent_id);

-- 最終ソート用：ランキング最適化
CREATE INDEX CONCURRENTLY idx_final_ranking_optimization
ON talent_scores(target_segment_id, talent_id)
INCLUDE (vr_popularity, tpr_power_score);

-- 名前検索用：結果表示最適化
CREATE INDEX CONCURRENTLY idx_m_account_display
ON m_account(account_id)
INCLUDE (name_full_for_matching, image_url);
```

#### 実行スクリプト
```python
# execute_phase_b_indices.py
async def create_phase_b_indices():
    """Phase B インデックス作成実行"""
    conn = await get_asyncpg_connection()

    indices = [
        "CREATE INDEX CONCURRENTLY idx_talents_budget_optimization...",
        "CREATE INDEX CONCURRENTLY idx_talent_scores_base_power...",
        # ... 他のインデックス
    ]

    for idx_sql in indices:
        print(f"作成中: {idx_sql.split()[4]}")  # インデックス名表示
        await conn.execute(idx_sql)
        print("✅ 完了")

    await conn.close()
    print("🎉 Phase B インデックス作成完了")
```

**期待効果**: 25%高速化

### 5. パーシャルインデックス活用

```sql
-- 条件付きインデックスで効率化
CREATE INDEX CONCURRENTLY idx_high_budget_talents
ON talents(talent_id, money_max_one_year)
WHERE money_max_one_year >= 50000000;  -- 5000万円以上

CREATE INDEX CONCURRENTLY idx_valid_scores_only
ON talent_scores(target_segment_id, talent_id, vr_popularity, tpr_power_score)
WHERE vr_popularity > 0 AND tpr_power_score > 0;

CREATE INDEX CONCURRENTLY idx_image_scores_positive
ON talent_images(industry_id, target_segment_id, image_score DESC)
WHERE image_score > 0;
```

**期待効果**: 15%高速化

## 🧪 Phase C: 将来対応最適化

### 6. マスタデータキャッシュ

```python
# app/cache/master_data.py
from functools import lru_cache
import asyncio
from datetime import datetime, timedelta

class MasterDataCache:
    def __init__(self):
        self._industries_cache = None
        self._target_segments_cache = None
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=30)

    async def get_industries(self):
        """業種マスタキャッシュ取得"""
        if self._is_cache_expired():
            await self._refresh_cache()
        return self._industries_cache

    async def get_target_segments(self):
        """ターゲット層マスタキャッシュ取得"""
        if self._is_cache_expired():
            await self._refresh_cache()
        return self._target_segments_cache

    def _is_cache_expired(self) -> bool:
        if self._cache_timestamp is None:
            return True
        return datetime.now() - self._cache_timestamp > self._cache_duration

    async def _refresh_cache(self):
        """キャッシュ更新（マッチング結果は対象外）"""
        conn = await get_asyncpg_connection()

        # 並行取得
        industries, segments = await asyncio.gather(
            conn.fetch("SELECT * FROM industries ORDER BY industry_id"),
            conn.fetch("SELECT * FROM target_segments ORDER BY segment_id")
        )

        self._industries_cache = industries
        self._target_segments_cache = segments
        self._cache_timestamp = datetime.now()

        await conn.close()

# グローバルキャッシュインスタンス
master_cache = MasterDataCache()
```

**期待効果**: 5%高速化

### 7. 並行処理最適化

```python
# app/api/endpoints/matching_optimized.py
async def optimized_matching_endpoint(request: MatchingRequest):
    """最適化済みマッチングエンドポイント"""

    # 並行実行可能な前処理
    validation_task = asyncio.create_task(validate_request(request))
    master_data_task = asyncio.create_task(master_cache.get_industries())

    # 前処理完了待ち
    await validation_task
    industries = await master_data_task

    # メイン処理：統合クエリ実行
    start_time = time.time()
    matching_results = await prepared_queries.execute_matching(
        request.budget_max,
        request.target_segment_id,
        request.industry_id
    )

    # STEP 5: マッチングスコア振り分け（並行実行）
    scored_results = await asyncio.gather(*[
        assign_matching_score(result, index)
        for index, result in enumerate(matching_results)
    ])

    processing_time = time.time() - start_time

    return {
        "results": scored_results,
        "processing_time": processing_time,
        "total_count": len(scored_results)
    }
```

**期待効果**: 8%高速化

## 📊 実装優先度と推奨順序

### 即効実装（Phase A）- 4時間
```bash
# 1時間目：クエリ統合実装
# 2時間目：プリペアドステートメント実装
# 3時間目：接続プール最適化
# 4時間目：動作検証・パフォーマンステスト
```

### 持続最適化（Phase B）- 2時間
```bash
# 1時間目：複合インデックス作成
# 2時間目：パーシャルインデックス作成・検証
```

### 将来対応（Phase C）- 2時間
```bash
# 1時間目：マスタデータキャッシュ実装
# 2時間目：並行処理最適化・最終検証
```

## ⚠️ 実装時注意事項

### 絶対遵守事項
1. **マッチングロジック保持**: STEP 0-5の計算式を1文字たりとも変更しない
2. **結果整合性**: 最適化前後で同一入力に対して同一結果を保証
3. **ソート順保持**: `ORDER BY final_score DESC, base_power_score DESC, talent_id`
4. **PERCENT_RANK()維持**: 業界イメージ査定の統計計算手法を保持

### 実装前検証
```python
# 実装前の結果保存
before_results = await original_matching(test_cases)

# 最適化実装後の検証
after_results = await optimized_matching(test_cases)

# 完全一致確認
assert before_results == after_results, "結果不一致！実装中止！"
```

### ロールバック準備
```bash
# 実装前バックアップ
cp -r /talent-casting-form/backend /talent-casting-form/backend-backup-optimization

# 問題発生時の復旧
rm -rf /talent-casting-form/backend
mv /talent-casting-form/backend-backup-optimization /talent-casting-form/backend
```

この詳細仕様書に従って実装することで、マッチングロジックを完全に保持しながら大幅な性能向上を実現できます。