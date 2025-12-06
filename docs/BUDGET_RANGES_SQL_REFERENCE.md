# budget_rangesテーブル SQL リファレンス

**作成日**: 2025-12-03

---

## テーブル定義確認

### 完全な CREATE TABLE文

```sql
CREATE TABLE budget_ranges (
  id integer DEFAULT nextval('budget_ranges_id_seq'::regclass) PRIMARY KEY,
  name character varying,
  min_amount numeric,
  max_amount numeric,
  display_order integer
);
```

---

## データ確認クエリ集

### 1. 全データ取得（表示順序順）

```sql
SELECT * FROM budget_ranges ORDER BY display_order;
```

**結果**:
```
 id │            name             │ min_amount │ max_amount │ display_order
────┼─────────────────────────────┼────────────┼────────────┼───────────────
  1 │ 1,000万円未満                 │          0 │        999 │             1
  2 │ 1,000万円～3,000万円未満       │      1,000 │      2,999 │             2
  3 │ 3,000万円～1億円未満           │      3,000 │      9,999 │             3
  4 │ 1億円以上                     │     10,000 │            │             4
```

### 2. 特定の予算区分を検索

```sql
-- CLAUDE.mdのテスト対象
SELECT * FROM budget_ranges WHERE name = '1,000万円～3,000万円未満';
```

### 3. 金額範囲での検索

```sql
-- 例: 5,000万円以下の予算区分を取得
SELECT * FROM budget_ranges 
WHERE max_amount IS NULL OR max_amount >= 50000000
ORDER BY display_order;
```

### 4. レコード数確認

```sql
SELECT COUNT(*) as budget_range_count FROM budget_ranges;
```

---

## talentsテーブルとの関連確認

### 5. 各予算区分に該当するタレント数（STEP 0フィルタリング）

```sql
-- レコード#2 (1,000万円～3,000万円未満)
SELECT COUNT(*) FROM talents 
WHERE money_max_one_year <= 29999999;

-- 全予算区分の集計
SELECT 
  br.id,
  br.name,
  br.max_amount,
  COUNT(t.id) as talent_count
FROM budget_ranges br
LEFT JOIN talents t ON (
  br.max_amount IS NULL OR t.money_max_one_year <= br.max_amount
) AND (
  br.min_amount IS NULL OR t.money_max_one_year >= br.min_amount
)
GROUP BY br.id, br.name, br.max_amount
ORDER BY br.display_order;
```

### 6. talentsテーブルの money_max_one_year 統計

```sql
SELECT 
  COUNT(*) as total_talents,
  COUNT(CASE WHEN money_max_one_year > 0 THEN 1 END) as non_zero_count,
  COUNT(CASE WHEN money_max_one_year IS NULL THEN 1 END) as null_count,
  MIN(money_max_one_year) as min_amount,
  MAX(money_max_one_year) as max_amount
FROM talents;
```

---

## データ修正用クエリ

### 7. budget_ranges の全レコード削除（修正前）

```sql
DELETE FROM budget_ranges;
```

### 8. budget_ranges の再投入（正しい金額）

```sql
-- 各レコードを個別に INSERT
INSERT INTO budget_ranges (name, min_amount, max_amount, display_order)
VALUES ('1,000万円未満', 0, 9999999, 1);

INSERT INTO budget_ranges (name, min_amount, max_amount, display_order)
VALUES ('1,000万円～3,000万円未満', 10000000, 29999999, 2);

INSERT INTO budget_ranges (name, min_amount, max_amount, display_order)
VALUES ('3,000万円～1億円未満', 30000000, 99999999, 3);

INSERT INTO budget_ranges (name, min_amount, max_amount, display_order)
VALUES ('1億円以上', 100000000, NULL, 4);
```

### 9. talentsテーブルの money_max_one_year を設定（テストデータ）

```sql
-- テスト用: すべてのタレントに 15,000,000 を設定
UPDATE talents SET money_max_one_year = 15000000 
WHERE money_max_one_year IS NULL;

-- または、条件付きで設定
UPDATE talents SET money_max_one_year = 
  CASE 
    WHEN category = 'singer' THEN 20000000
    WHEN category = 'actor' THEN 15000000
    ELSE 10000000
  END
WHERE money_max_one_year IS NULL;
```

---

## インデックス追加

### 10. display_order インデックス

```sql
CREATE INDEX idx_budget_ranges_display_order 
ON budget_ranges(display_order);
```

### 11. 金額範囲インデックス

```sql
CREATE INDEX idx_budget_ranges_min_max 
ON budget_ranges(min_amount, max_amount);
```

---

## 制約追加

### 12. CHECK制約（金額の妥当性）

```sql
ALTER TABLE budget_ranges 
ADD CONSTRAINT check_amounts 
CHECK (min_amount <= max_amount OR max_amount IS NULL);
```

### 13. UNIQUE制約（名称の一意性）

```sql
ALTER TABLE budget_ranges 
ADD CONSTRAINT unique_budget_name 
UNIQUE(name);
```

---

## スキーマ確認クエリ

### 14. テーブルのカラム情報

```sql
SELECT 
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_name = 'budget_ranges'
ORDER BY ordinal_position;
```

### 15. インデックス一覧

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'budget_ranges';
```

### 16. 制約一覧

```sql
SELECT 
  constraint_name,
  constraint_type,
  column_name
FROM information_schema.constraint_column_usage ccu
JOIN information_schema.table_constraints tc USING (table_name, constraint_name)
WHERE table_name = 'budget_ranges';
```

---

## トラブルシューティング クエリ

### 17. 金額が小さすぎることの確認

```sql
-- レコード#2の金額を確認
SELECT 
  name,
  min_amount,
  max_amount,
  (max_amount::decimal / 10000) as expected_max_amount,
  (max_amount::decimal / 29999999) * 100 as ratio_percent
FROM budget_ranges
WHERE name = '1,000万円～3,000万円未満';
```

### 18. talentsテーブルがフィルタリングされない原因確認

```sql
-- STEP 0フィルタリングの現状
SELECT 
  COUNT(*) as total_talents,
  COUNT(CASE WHEN money_max_one_year IS NULL THEN 1 END) as null_count,
  COUNT(CASE WHEN money_max_one_year > 0 THEN 1 END) as positive_count
FROM talents;

-- もし positive_count > 0 であれば、フィルタリング可能
-- 現在: positive_count = 0（全NULL）
```

### 19. 修正後の検証クエリ

```sql
-- 修正前後の比較
SELECT 
  'before' as status,
  (SELECT COUNT(*) FROM talents WHERE money_max_one_year <= 29999999) as matching_count
UNION ALL
SELECT 
  'after',
  (SELECT COUNT(*) FROM talents WHERE money_max_one_year <= 29999999)
;
```

---

## パフォーマンス確認

### 20. クエリプランの確認

```sql
EXPLAIN ANALYZE
SELECT * FROM budget_ranges 
WHERE display_order = 2;

-- インデックスがあれば "Index Scan" が表示される
```

### 21. テーブルサイズ確認

```sql
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size
FROM pg_tables
WHERE tablename = 'budget_ranges';
```

---

## 運用用クエリ

### 22. 定期メンテナンス（VACUUM）

```sql
VACUUM ANALYZE budget_ranges;
```

### 23. 統計情報更新

```sql
ANALYZE budget_ranges;
```

### 24. テーブル構造確認（総合）

```sql
\d budget_ranges  -- psqlコマンド
-- または
DESC budget_ranges;  -- MySQL互換形式
```

---

## 実装チェック用クエリ

### 25. APIで返すべき形式（JSON）

```sql
SELECT json_agg(row_to_json(br.*) ORDER BY br.display_order) as data
FROM budget_ranges br;
```

**結果形式**:
```json
[
  {"id": 1, "name": "1,000万円未満", "min_amount": "0", "max_amount": "999", "display_order": 1},
  {"id": 2, "name": "1,000万円～3,000万円未満", "min_amount": "1000", "max_amount": "2999", "display_order": 2},
  ...
]
```

---

## 推奨実行順序（修正時）

```bash
# 1. 現状確認
psql -d neondb -c "SELECT * FROM budget_ranges ORDER BY display_order;"

# 2. talentsテーブル確認
psql -d neondb -c "SELECT COUNT(*) FROM talents WHERE money_max_one_year > 0;"

# 3. 既存データ削除
psql -d neondb -c "DELETE FROM budget_ranges;"

# 4. スクリプト実行
python3 insert_budget_ranges.py

# 5. 修正確認
psql -d neondb -c "SELECT * FROM budget_ranges ORDER BY display_order;"

# 6. マッチング確認
psql -d neondb -c "SELECT COUNT(*) FROM talents WHERE money_max_one_year <= 29999999;"
```

---

**注**: このリファレンスは 2025-12-03 時点の状態に基づいています。
