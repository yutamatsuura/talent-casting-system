# 本番環境予算フィルタリングバグ 詳細分析レポート

## 概要

**問題:** 新垣結衣（money_max_one_year: 8,000万）が、ユーザー予算「1,000万～3,000万未満」のテストで上位30名に含まれてしまう重大バグ

**緊急度:** CRITICAL（本番環境で実際に顧客に不正な結果を返却中）

**修正ファイル:** 1ファイル

**修正行数:** 3行

---

## バグの特定

### バグ位置

**ファイル:** `/Users/lennon/projects/talent-casting-form/backend/app/api/endpoints/matching.py`

**関数:** `execute_matching_logic()`

**WHERE句:** 行 551-562

**3つのORパターン**

---

## 仕様との比較

### CLAUDE.md の仕様（正しい定義）

```yaml
STEP 0: 予算フィルタリング
  - テーブル: talents.money_max_one_year
  - 条件: <= ユーザー選択予算上限
```

つまり：**タレント予算上限 <= ユーザー予算上限** が正しい条件

### 現在の実装（バグ）

```sql
AND (
  -- パターン1: 両方設定済み（MIN有・MAX有）
  (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NOT NULL
   AND $1 >= mta.money_min_one_year)    ❌ BUG
  OR
  -- パターン2: MIN有・MAX無
  (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NULL
   AND $1 >= mta.money_min_one_year)    ❌ BUG
  OR
  -- パターン3: MIN無・MAX有
  (mta.money_min_one_year IS NULL AND mta.money_max_one_year IS NOT NULL
   AND $1 >= mta.money_max_one_year)    ❌ BUG（意味は同じが不可解）
)
```

---

## バグの詳細分析

### パラメータの意味

- `$1` = ユーザー選択予算の「上限」（例：「1,000万～3,000万未満」→ 3,000万）
- `mta.money_min_one_year` = タレント予算の「下限」
- `mta.money_max_one_year` = タレント予算の「上限」

### パターン1の問題

```
現在の条件: $1 >= mta.money_min_one_year
意味: ユーザー予算上限 >= タレント最小予算
例: 3,000万 >= 2,000万 → YES （通過）

しかし新垣結衣の上限は8,000万であり、
ユーザー予算3,000万では対応できない。

正しい判定:
8,000万 <= 3,000万? → NO → 除外（正しい）
```

### なぜこのバグが存在するのか

1. パラメータ名が曖昧だった（`$1`の意味が不明確）
2. タレント下限だけをチェックして上限チェックを忘れた
3. 正しい実装（ultra_optimized_queries.py）との実装の不統一

---

## 修正方案

### 修正対象の3行

**行554:** `$1 >= mta.money_min_one_year` → `mta.money_max_one_year <= $1`

**行558:** `$1 >= mta.money_min_one_year` → `mta.money_min_one_year <= $1`

**行562:** `$1 >= mta.money_max_one_year` → `mta.money_max_one_year <= $1`

### 修正後のコード

```sql
AND (
  -- パターン1: 両方設定済み → タレント最大予算 <= ユーザー予算上限で通過
  (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NOT NULL
   AND mta.money_max_one_year <= $1)
  OR
  -- パターン2: MIN有・MAX無 → タレント最小予算 <= ユーザー予算上限で通過
  (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NULL
   AND mta.money_min_one_year <= $1)
  OR
  -- パターン3: MIN無・MAX有 → タレント最大予算 <= ユーザー予算上限で通過
  (mta.money_min_one_year IS NULL AND mta.money_max_one_year IS NOT NULL
   AND mta.money_max_one_year <= $1)
)
```

---

## 修正後の検証

### テストケース1：新垣結衣（MAX: 8,000万）が除外される

```sql
SELECT ma.name_full_for_matching, mta.money_max_one_year
FROM m_account ma
LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
WHERE ma.name_full_for_matching = '新垣結衣'
  AND mta.money_max_one_year > 3000  -- ユーザー予算3,000万より高い
```

**期待結果:** 除外される

### テストケース2：予算の小さいタレント（MAX: 2,000万）が通過

```sql
SELECT ma.name_full_for_matching, mta.money_max_one_year
FROM m_account ma
LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
WHERE mta.money_max_one_year <= 3000  -- ユーザー予算3,000万以下
LIMIT 10
```

**期待結果:** すべて通過

---

## 対比：他のエンドポイント

### /ultra_optimized エンドポイント

**ファイル:** `/Users/lennon/projects/talent-casting-form/backend/app/db/ultra_optimized_queries.py`

**行46:** `OR ($1 = 'Infinity'::float8 OR mta.money_max_one_year <= $1)`

ここでは正しいロジック（`mta.money_max_one_year <= $1`）が使用されている。

**結論:** ultra_optimized_queriesは正しい実装。matching.pyだけが間違っている。

---

## 影響分析

### 修正後のマッチング結果

- 新垣結衣のような高い上限予算を持つタレントが、低予算ユーザーに推薦されなくなる
- より適切な予算レンジのタレントが推薦される
- 顧客満足度向上

### データベース

- 修正はロジック変更のみ
- データベースには変更がない
- 既存データの整合性に問題なし

---

## 実装チェックリスト

- [ ] 行554を修正: `$1 >= mta.money_min_one_year` → `mta.money_max_one_year <= $1`
- [ ] 行558を修正: `$1 >= mta.money_min_one_year` → `mta.money_min_one_year <= $1`
- [ ] 行562を修正: `$1 >= mta.money_max_one_year` → `mta.money_max_one_year <= $1`
- [ ] コメントを更新（「MAX <= ユーザー予算」に修正）
- [ ] ローカルでテスト実行
- [ ] 本番環境にデプロイ
- [ ] マッチング結果を検証（新垣結衣が3,000万予算で除外される）

---

## 修正の優先度

**緊急度:** CRITICAL

- 本番環境で実際に顧客に不正な結果を返却している
- 修正は簡単（3行のSQL条件変更）
- 影響が限定的（予算フィルタリング部分のみ）

**修正所要時間:** 5分以内
**テスト所要時間:** 15分程度
**デプロイ所要時間:** 10分以内

---

## 補記

このバグは、開発者が以下を誤認識した結果発生した可能性が高い：

1. `$1`がユーザー予算の「上限」ではなく「下限」だと思い込んだ
2. タレント下限だけをチェックして上限チェックを忘れた
3. 他のエンドポイント（ultra_optimized_queries.py）との実装の不統一に気づかなかった

