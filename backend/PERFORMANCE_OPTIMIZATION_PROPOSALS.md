# マッチングAPIパフォーマンス最適化提案書
生成日: 2025-12-05
制約: **マッチングロジック絶対不変**

## 現状分析
- **現在の処理時間**: 8.4〜8.6秒
- **主要ボトルネック**: データベース接続とクエリ処理
- **接続数**: リクエスト毎に4+N回の個別接続
- **目標**: 3秒以下（設計値242msの余裕度12倍）

## 📋 最適化提案（優先度順）

### 🟢 【高優先度】データベース最適化（即効性あり）

#### 1. クエリ統合による接続数削減
**現在**: 5段階で個別クエリ実行
**提案**: 全クエリを1つのJOIN文に統合

**効果見込み**: 50-70%高速化
**実装難易度**: 低
**リスク**: なし（結果は完全同一）

```sql
-- 統合クエリ例（マッチングロジックは完全保持）
WITH step0_budget_filter AS (
  SELECT talent_id FROM talents WHERE money_max_one_year <= ?
),
step1_base_power AS (
  SELECT ts.talent_id,
         (ts.vr_popularity + ts.tpr_power_score) / 2.0 as base_power_score
  FROM talent_scores ts
  INNER JOIN step0_budget_filter bf ON ts.talent_id = bf.talent_id
  WHERE ts.target_segment_id = ?
),
step2_image_assessment AS (
  SELECT ti.talent_id,
         PERCENT_RANK() OVER (ORDER BY ti.image_score DESC) as percentile_rank,
         CASE
           WHEN PERCENT_RANK() OVER (ORDER BY ti.image_score DESC) <= 0.15 THEN 12.0
           WHEN PERCENT_RANK() OVER (ORDER BY ti.image_score DESC) <= 0.30 THEN 6.0
           -- 既存ロジックと完全同一
         END as image_adjustment
  FROM talent_images ti
  WHERE ti.target_segment_id = ? AND ti.industry_id = ?
)
SELECT * FROM step1_base_power
JOIN step2_image_assessment USING (talent_id)
ORDER BY (base_power_score + image_adjustment) DESC, base_power_score DESC, talent_id
LIMIT 30
```

#### 2. プリペアドステートメント活用
**現在**: 動的SQL生成
**提案**: 事前コンパイル済みクエリ使用

**効果見込み**: 10-20%高速化
**実装**: SQLAlchemy text()でプレースホルダー使用

#### 3. 接続プール詳細チューニング
**現在設定**:
```env
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=10
```

**最適化提案**:
```env
DB_POOL_SIZE=15         # 同時接続最適化
DB_MAX_OVERFLOW=25      # 過剰接続防止
DB_POOL_TIMEOUT=5       # 高速タイムアウト
DB_POOL_RECYCLE=900     # 15分サイクル
DB_POOL_PRE_PING=true   # 接続検証
```

### 🟡 【中優先度】インデックス追加最適化

#### 4. 複合インデックス作成
**既存**: 基本インデックスのみ
**提案**: クエリパターン特化型複合インデックス

```sql
-- STEP0用予算フィルタ最適化
CREATE INDEX idx_talents_budget_target ON talents(money_max_one_year, target_segment_id);

-- STEP2用業界別イメージ最適化
CREATE INDEX idx_talent_images_industry_segment ON talent_images(industry_id, target_segment_id, image_score DESC);

-- 最終ソート最適化
CREATE INDEX idx_final_ranking ON talent_scores(target_segment_id, base_power_score DESC, talent_id);
```

**効果見込み**: 20-30%高速化

#### 5. パーシャルインデックス活用
**提案**: 条件付きインデックスで容量削減

```sql
-- 有効なスコアのみインデックス
CREATE INDEX idx_valid_scores ON talent_scores(target_segment_id, base_power_score DESC)
WHERE base_power_score IS NOT NULL AND base_power_score > 0;

-- 予算範囲内タレント専用
CREATE INDEX idx_affordable_talents ON talents(talent_id, target_segment_id)
WHERE money_max_one_year <= 100000000; -- 1億円以下
```

### 🟠 【低優先度】アプリケーション層最適化

#### 6. 非同期処理最適化
**現在**: 逐次処理
**提案**: 並行処理可能部分の分離

```python
# マスタデータ事前取得（並行実行）
async def preload_master_data():
    return await asyncio.gather(
        get_industries(),
        get_target_segments(),
        get_image_items()
    )
```

#### 7. 結果キャッシュ（部分的）
**対象**: マスタデータのみ
**制約**: マッチング結果は毎回リアルタイム計算維持

```python
# マスタデータ30分キャッシュ
@cache(expire=1800)  # 30分
async def get_cached_industries():
    return await get_industries()
```

### 🔵 【検討事項】インフラ層最適化

#### 8. データベース設定調整
**Neon PostgreSQL最適化設定**:
```sql
-- 検索性能向上
SET work_mem = '256MB';
SET random_page_cost = 1.1;  # SSD最適化
SET effective_cache_size = '1GB';

-- 接続最適化
SET max_connections = 50;
SET shared_buffers = '256MB';
```

#### 9. ネットワーク最適化
- **データベース地域**: ap-southeast-1 (シンガポール)
- **API地域**: Google Cloud Run 最適配置
- **レイテンシ測定**: 定期的な接続速度監視

## 📊 実装優先順位と効果予測

| 項目 | 優先度 | 実装時間 | 効果予測 | リスク |
|------|-------|---------|---------|-------|
| クエリ統合 | 🟢 最高 | 2-3時間 | 50-70% | なし |
| プリペアド文 | 🟢 高 | 1時間 | 10-20% | なし |
| 接続プール調整 | 🟢 高 | 30分 | 5-15% | なし |
| 複合インデックス | 🟡 中 | 1時間 | 20-30% | 低 |
| 並行処理 | 🟠 低 | 2時間 | 5-10% | 中 |
| キャッシュ | 🟠 低 | 1時間 | 3-8% | 中 |

## 🎯 推奨実装プラン

### Phase A: 即効性最適化（想定効果: 70-80%高速化）
1. **クエリ統合** → 単一JOIN文での全処理
2. **プリペアドステートメント** → SQLコンパイル高速化
3. **接続プール調整** → 設定パラメータ最適化

**実装時間**: 3-4時間
**期待結果**: 8.4秒 → 1.7-2.5秒

### Phase B: 持続的最適化（想定効果: 追加20-30%）
4. **複合インデックス追加** → クエリ特化型インデックス
5. **パーシャルインデックス** → 条件付き高速検索

**実装時間**: 1-2時間
**期待結果**: 1.7-2.5秒 → 1.2-2.0秒

### Phase C: 将来対応（想定効果: 追加5-15%）
6. **マスタデータキャッシュ** → 静的データ高速化
7. **並行処理** → 非依存処理の並列実行

## ⚠️ 重要制約事項

### 絶対不変事項
1. **マッチングロジック**: STEP 0-5の計算式一切変更なし
2. **スコアリング**: PERCENT_RANK()による業界イメージ査定維持
3. **ランキング**: 最終ソート順序完全保持
4. **結果整合性**: 既存結果との100%一致保証

### 変更許可範囲
1. **データ取得方法**: JOINによる統合化
2. **接続方式**: プール最適化、プリペアド文使用
3. **インデックス**: 検索高速化のための追加
4. **キャッシュ**: マスタデータのみ（結果は毎回計算）

## 📈 測定・検証方法

### パフォーマンステスト
```python
# 測定スクリプト例
async def benchmark_matching():
    test_cases = [
        {"industry": "化粧品", "target": "女性20-34", "budget": 50000000},
        {"industry": "医薬品", "target": "男性20-34", "budget": 100000000}
    ]

    for case in test_cases:
        start_time = time.time()
        result = await matching_api(case)
        duration = time.time() - start_time
        print(f"ケース: {case}, 処理時間: {duration:.2f}秒")
```

### 結果整合性検証
```python
# 最適化前後の結果比較
async def verify_consistency():
    old_result = await original_matching(test_data)
    new_result = await optimized_matching(test_data)

    assert old_result == new_result, "結果不一致検出"
    print("✅ 結果整合性確認完了")
```

この提案書に基づき、Phase Aから順次実装することで、マッチングロジックを一切変更することなく大幅な性能向上が期待できます。