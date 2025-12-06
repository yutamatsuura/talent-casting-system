# バックエンド マッチングロジック修正レポート

## 修正日: 2025-12-03

## 概要
実際のデータベース構造に合わせて、5段階マッチングロジックのSQLクエリを修正しました。

## 修正内容

### 1. STEP 2: イメージスコア集約の修正

#### 問題点
- **期待値**: `talent_images.image_funny`, `image_clean`など7つのカラム（非正規化）
- **実際**: `talent_images.image_item_id`と`score`（正規化）

#### 修正内容
```sql
-- 修正前（非正規化想定）
SELECT
    ti.account_id,
    ti.target_segment_id,
    PERCENT_RANK() OVER (
        PARTITION BY ti.target_segment_id, image_id
        ORDER BY
            CASE image_id
                WHEN 1 THEN ti.image_funny
                WHEN 2 THEN ti.image_clean
                -- ...
            END DESC
    ) AS percentile_rank,
    image_id
FROM talent_images ti
CROSS JOIN unnest($4::int[]) AS image_id
WHERE ti.target_segment_id = ANY($3::int[])

-- 修正後（正規化対応）
SELECT
    ti.account_id,
    ti.target_segment_id,
    PERCENT_RANK() OVER (
        PARTITION BY ti.target_segment_id, ti.image_item_id
        ORDER BY ti.score DESC
    ) AS percentile_rank
FROM talent_images ti
WHERE ti.target_segment_id = ANY($3::int[])
    AND ti.image_item_id = ANY($4::int[])
```

### 2. STEP 2: 加減点テーブルの修正

#### 問題点
```
誤り:
- 31~50%帯: 0.0点
- 51~70%帯: -6.0点
- 71~100%帯: -12.0点
```

#### 修正内容
```sql
-- 正しい加減点テーブル
CASE
    WHEN percentile_rank <= 0.15 THEN 12.0   -- 上位15%: +12点
    WHEN percentile_rank <= 0.30 THEN 6.0    -- 16~30%: +6点
    WHEN percentile_rank <= 0.50 THEN 3.0    -- 31~50%: +3点 (修正)
    WHEN percentile_rank <= 0.70 THEN -3.0   -- 51~70%: -3点 (修正)
    WHEN percentile_rank <= 0.85 THEN -6.0   -- 71~85%: -6点 (修正)
    ELSE -12.0                               -- 86~100%: -12点
END
```

### 3. image_itemsテーブルのカラム名修正

#### 問題点
- **期待値**: `image_items.image_id`
- **実際**: `image_items.id`

#### 修正内容
```python
# 修正前
image_rows = await conn.fetch("SELECT image_id FROM image_items ORDER BY image_id")
image_item_ids = [row["image_id"] for row in image_rows]

# 修正後
image_rows = await conn.fetch("SELECT id FROM image_items ORDER BY id")
image_item_ids = [row["id"] for row in image_rows]
```

## 影響範囲

### 修正ファイル
- `/backend/app/api/endpoints/matching.py`

### 変更なしファイル
- `/backend/app/schemas/matching.py` - スキーマ定義は既に正しい
- `/backend/app/models/__init__.py` - モデル定義は既に正しい

## 確認事項

### データベース構造（実際）
```sql
-- m_account テーブル
account_id (PK)
name_full_for_matching
last_name_kana
act_genre
birthday

-- m_talent_act テーブル
account_id (FK)
money_max_one_year

-- talent_scores テーブル
account_id (FK)
target_segment_id (FK)
base_power_score

-- talent_images テーブル（正規化）
account_id (FK)
target_segment_id (FK)
image_item_id (FK)
score

-- image_items テーブル
id (PK)
code
name
```

## 動作確認

### 構文チェック
```bash
cd /Users/lennon/projects/talent-casting-form/backend
python3 -m py_compile app/api/endpoints/matching.py
# ✓ 成功
```

### 次のステップ
1. データベース接続テスト
2. `/api/matching` エンドポイント動作確認
3. 実際のフォームデータでマッチング結果確認

## 技術的な詳細

### 正規化データ対応の利点
1. **柔軟性**: イメージ項目の追加・削除が容易
2. **保守性**: カラム数が固定されないため、スキーマ変更が不要
3. **クエリ効率**: 必要なイメージ項目のみを絞り込める

### PERCENT_RANK()の動作
- 各`target_segment_id`と`image_item_id`の組み合わせごとにパーセンタイルを計算
- `score`の降順で順位付け
- 上位ほど低い値（0に近い）、下位ほど高い値（1に近い）

## 注意事項

### データベース側の変更なし
- 全ての修正はコード側で対応
- データベーススキーマの変更は一切不要

### パフォーマンス影響
- 正規化データの`JOIN`により、若干のパフォーマンス低下の可能性
- ただし、適切なインデックス（`idx_talent_images_lookup`）により最適化済み
- 目標レスポンス時間（<3秒）は維持される見込み

## まとめ

実際のデータベース構造に完全に合わせた修正を完了しました。正規化されたデータ構造に対応し、加減点テーブルも正しい値に修正しました。これにより、5段階マッチングロジックが正常に動作する準備が整いました。

次は、実際のデータベースに接続してエンドポイントの動作確認を行います。
