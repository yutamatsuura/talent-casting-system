# マッチングロジック修正完了サマリー

## 修正日時: 2025-12-03 19:48

## 修正完了事項

### ✅ 1. STEP 2: イメージスコア集約の正規化対応

**修正前（非正規化想定）**:
```sql
SELECT
    ti.account_id,
    ti.target_segment_id,
    PERCENT_RANK() OVER (
        PARTITION BY ti.target_segment_id, image_id
        ORDER BY
            CASE image_id
                WHEN 1 THEN ti.image_funny
                WHEN 2 THEN ti.image_clean
                -- ...7つのカラム
            END DESC
    ) AS percentile_rank
FROM talent_images ti
CROSS JOIN unnest($4::int[]) AS image_id
```

**修正後（正規化対応）**:
```sql
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

**メリット**:
- データベースの実際の構造（正規化）に完全一致
- 不要な`CROSS JOIN`を削除し、パフォーマンス向上
- `image_item_id`と`score`の2カラムで柔軟に管理

---

### ✅ 2. STEP 2: 加減点テーブルの修正

**修正前（誤り）**:
```sql
CASE
    WHEN percentile_rank <= 0.15 THEN 12.0   -- 上位15%: +12点
    WHEN percentile_rank <= 0.30 THEN 6.0    -- 16~30%: +6点
    WHEN percentile_rank <= 0.50 THEN 0.0    -- 31~50%: 0点 ❌
    WHEN percentile_rank <= 0.70 THEN -6.0   -- 51~70%: -6点 ❌
    ELSE -12.0                               -- 71~100%: -12点 ❌
END
```

**修正後（正しい）**:
```sql
CASE
    WHEN percentile_rank <= 0.15 THEN 12.0   -- 上位15%: +12点
    WHEN percentile_rank <= 0.30 THEN 6.0    -- 16~30%: +6点
    WHEN percentile_rank <= 0.50 THEN 3.0    -- 31~50%: +3点 ✅
    WHEN percentile_rank <= 0.70 THEN -3.0   -- 51~70%: -3点 ✅
    WHEN percentile_rank <= 0.85 THEN -6.0   -- 71~85%: -6点 ✅
    ELSE -12.0                               -- 86~100%: -12点 ✅
END
```

**影響**:
- 中位帯（31~70%）のタレントの評価が正確になる
- 上位優遇・下位減点の傾斜が適切に調整される
- マッチングスコアの分布が仕様通りになる

---

### ✅ 3. image_itemsテーブルのカラム名修正

**修正前（誤り）**:
```python
image_rows = await conn.fetch("SELECT image_id FROM image_items ORDER BY image_id")
image_item_ids = [row["image_id"] for row in image_rows]
```

**修正後（正しい）**:
```python
image_rows = await conn.fetch("SELECT id FROM image_items ORDER BY id")
image_item_ids = [row["id"] for row in image_rows]
```

**データベース構造**:
```sql
CREATE TABLE image_items (
    id INTEGER PRIMARY KEY,      -- ✅ 実際のカラム名
    code VARCHAR(50),
    name VARCHAR(100)
);
```

---

## 動作確認ステータス

### ✅ 構文チェック
```bash
python3 -m py_compile backend/app/api/endpoints/matching.py
# 成功
```

### ⏳ 実行テスト（次のステップ）
1. データベース接続テスト
2. `/api/matching` エンドポイント動作確認
3. 実際のフォームデータでマッチング結果確認

---

## 修正ファイル一覧

### 変更あり
- `/backend/app/api/endpoints/matching.py` (11,370 bytes)

### 変更なし（既に正しい）
- `/backend/app/schemas/matching.py` - スキーマ定義は正しい
- `/backend/app/models/__init__.py` - モデル定義は正しい

---

## データベース構造との整合性

### 実際のテーブル構造
```sql
-- m_account (タレント基本情報)
account_id (PK)
name_full_for_matching
last_name_kana
act_genre
birthday

-- m_talent_act (タレント活動情報)
account_id (FK)
money_max_one_year

-- talent_scores (スコア情報)
account_id (FK)
target_segment_id (FK)
base_power_score

-- talent_images (イメージスコア、正規化)
account_id (FK)
target_segment_id (FK)
image_item_id (FK)
score

-- image_items (イメージ項目マスタ)
id (PK)
code
name
```

### SQLクエリとの対応
| SQL内のカラム参照 | 実際のテーブル.カラム | 状態 |
|---|---|---|
| `ma.account_id` | `m_account.account_id` | ✅ 一致 |
| `ma.name_full_for_matching` | `m_account.name_full_for_matching` | ✅ 一致 |
| `mta.money_max_one_year` | `m_talent_act.money_max_one_year` | ✅ 一致 |
| `ts.base_power_score` | `talent_scores.base_power_score` | ✅ 一致 |
| `ti.image_item_id` | `talent_images.image_item_id` | ✅ 一致 |
| `ti.score` | `talent_images.score` | ✅ 一致 |

---

## 技術的詳細

### PERCENT_RANK()の動作
```sql
PERCENT_RANK() OVER (
    PARTITION BY ti.target_segment_id, ti.image_item_id
    ORDER BY ti.score DESC
)
```

- **PARTITION BY**: `target_segment_id`と`image_item_id`の組み合わせごとに独立して計算
- **ORDER BY**: `score`の降順でランク付け
- **結果**: 0.0（最上位）～ 1.0（最下位）の値

### 加減点の分布
| パーセンタイル | 加減点 | 想定人数（全体1000人） |
|---|---|---|
| 0~15% | +12点 | 150人 |
| 16~30% | +6点 | 150人 |
| 31~50% | +3点 | 200人 |
| 51~70% | -3点 | 200人 |
| 71~85% | -6点 | 150人 |
| 86~100% | -12点 | 150人 |

---

## パフォーマンス影響

### 改善点
1. **不要なCROSS JOIN削除**: クエリプランがシンプルに
2. **WHERE句でのフィルタリング**: インデックス利用が最適化
3. **PARTITION BYの最適化**: グループ数が減少

### 期待パフォーマンス
- **目標**: <3秒
- **設計値**: 242ms（リアルタイム計算）
- **余裕度**: 12倍
- **修正後の影響**: ほぼ同等（むしろ改善の可能性）

---

## 次のステップ

### 1. データベース接続テスト
```bash
cd backend
python3 -c "from app.db.connection import get_asyncpg_connection; import asyncio; asyncio.run(get_asyncpg_connection())"
```

### 2. エンドポイント動作確認
```bash
cd backend
uvicorn app.main:app --reload --port 8432
```

### 3. 実際のマッチング実行
```bash
curl -X POST http://localhost:8432/api/matching \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "化粧品・ヘアケア・オーラルケア",
    "target_segments": ["女性20-34", "女性35-49"],
    "budget": "1,000万円～3,000万円未満",
    "company_name": "株式会社テストクライアント",
    "email": "test@talent-casting-dev.local"
  }'
```

---

## まとめ

実際のデータベース構造に完全に合わせた修正を完了しました。

### 修正の重要ポイント
1. ✅ 正規化データ構造（`image_item_id` + `score`）に完全対応
2. ✅ 加減点テーブルを仕様通りに修正（31~50%: +3点、51~70%: -3点）
3. ✅ カラム名を実際のDB構造に統一（`id`、`account_id`、`name_full_for_matching`）

### 次の作業
データベース接続テストとエンドポイント動作確認を実施してください。
