# budget_rangesマスタテーブル 詳細分析レポート

**作成日時**: 2025-12-03  
**対象**: PostgreSQL (Neon) - talent-casting-form データベース  
**分析者**: Claude Code AI Assistant

---

## 目次

1. [テーブル構造](#テーブル構造)
2. [データ内容](#データ内容)
3. [ワーカー説明資料との照合](#ワーカー説明資料との照合)
4. [talentsテーブルとの関連](#talentsテーブルとの関連)
5. [フロントエンド連携](#フロントエンド連携)
6. [トラブルシューティング](#トラブルシューティング)
7. [修正が必要な箇所](#修正が必要な箇所)

---

## テーブル構造

### 1-1. CREATE TABLE文（完全形）

```sql
CREATE TABLE budget_ranges (
  id integer DEFAULT nextval('budget_ranges_id_seq'::regclass) PRIMARY KEY,
  name character varying,
  min_amount numeric,
  max_amount numeric,
  display_order integer
);
```

### 1-2. カラム詳細

| # | カラム名 | データ型 | NULL許可 | 説明 |
|---|---------|--------|--------|------|
| 1 | **id** | integer | NO | 自動採番（PRIMARY KEY） |
| 2 | **name** | character varying | YES | 予算区分の日本語名称 |
| 3 | **min_amount** | numeric | YES | 最小金額（日本円） |
| 4 | **max_amount** | numeric | YES | 最大金額（日本円、NULLで上限なし） |
| 5 | **display_order** | integer | YES | UI表示順序 |

### 1-3. インデックス

```sql
CREATE UNIQUE INDEX budget_ranges_pkey ON public.budget_ranges USING btree (id)
```

**現状**: PRIMARY KEY のみ。display_order でのインデックスは未設定。

### 1-4. 制約

- **PRIMARY KEY**: id カラム
- **UNIQUE**: id（PRIMARY KEY により自動）
- **FOREIGN KEY**: なし

---

## データ内容

### 2-1. 全レコード（4件）

| ID | 名称 | min_amount | max_amount | display_order |
|---|------|-----------|-----------|---------------|
| 1 | 1,000万円未満 | 0 | 999 | 1 |
| 2 | 1,000万円～3,000万円未満 | 1,000 | 2,999 | 2 |
| 3 | 3,000万円～1億円未満 | 3,000 | 9,999 | 3 |
| 4 | 1億円以上 | 10,000 | NULL | 4 |

### 2-2. データの詳細説明

#### レコード #1: 1,000万円未満
- **ID**: 1
- **名称**: 1,000万円未満
- **最小額**: ¥0
- **最大額**: ¥999
- **表示順序**: 1（最初に表示）

#### レコード #2: 1,000万円～3,000万円未満（CLAUDE.mdテスト予算）
- **ID**: 2
- **名称**: 1,000万円～3,000万円未満
- **最小額**: ¥1,000
- **最大額**: ¥2,999
- **表示順序**: 2（2番目に表示）
- **重要**: CLAUDE.md の `test_budget: 1,000万円～3,000万円未満` に対応

#### レコード #3: 3,000万円～1億円未満
- **ID**: 3
- **名称**: 3,000万円～1億円未満
- **最小額**: ¥3,000
- **最大額**: ¥9,999
- **表示順序**: 3（3番目に表示）

#### レコード #4: 1億円以上
- **ID**: 4
- **名称**: 1億円以上
- **最小額**: ¥10,000
- **最大額**: NULL（上限なし）
- **表示順序**: 4（最後に表示）

---

## ワーカー説明資料との照合

### 3-1. CLAUDE.md記載の予算区分

```yaml
# CLAUDE.md テスト認証情報より
test_budget: 1,000万円～3,000万円未満
```

### 3-2. 要件定義書（ワーカー説明資料）に記載された4つの予算区分

| # | 名称 | 期待される金額範囲 | 備考 |
|---|------|-----------------|------|
| 1 | 1,000万円未満 | ¥0 ～ ¥9,999,999 | 日本円単位 |
| 2 | 1,000万円～3,000万円未満 | ¥10,000,000 ～ ¥29,999,999 | **テスト対象** |
| 3 | 3,000万円～1億円未満 | ¥30,000,000 ～ ¥99,999,999 | 日本円単位 |
| 4 | 1億円以上 | ¥100,000,000 ～ 上限なし | 日本円単位 |

### 3-3. 照合結果

✅ **名称は完全一致**

```
✅ 1,000万円未満                    ← 存在確認OK
✅ 1,000万円～3,000万円未満          ← 存在確認OK（CLAUDE.mdテスト対象）
✅ 3,000万円～1億円未満              ← 存在確認OK
✅ 1億円以上                        ← 存在確認OK
```

### 3-4. 重大な問題: 金額の単位の不一致

| 項目 | 現在の値 | 期待される値 | 状態 |
|------|---------|-----------|------|
| min_amount (レコード#2) | 1,000 | 10,000,000 | ❌ 不一致 |
| max_amount (レコード#2) | 2,999 | 29,999,999 | ❌ 不一致 |

**原因推定**: 金額の単位が「万円」ではなく「千円」または「百円」で入力されている可能性

**影響範囲**:
- STEP 0フィルタリングで talentsテーブルのmoney_max_one_year と比較不可
- 全タレントがフィルタリング対象から除外される（0人になる）
- マッチング結果が返されない

---

## talentsテーブルとの関連

### 4-1. talentsテーブルのスキーマ（抜粋）

```sql
CREATE TABLE talents (
  id integer PRIMARY KEY,
  account_id integer,
  name character varying,
  kana character varying,
  gender character varying,
  birth_year integer,
  category character varying,
  money_max_one_year numeric,  ← STEP 0で使用
  created_at timestamp without time zone,
  updated_at timestamp without time zone
);
```

### 4-2. money_max_one_year の統計情報

| 項目 | 値 |
|------|-----|
| 総タレント数 | 4,819 |
| money_max_one_year > 0 の件数 | **0人** ❌ |
| money_max_one_year IS NULL | **4,819人** ❌ |
| 最小値 | (なし) |
| 最大値 | (なし) |

**重大問題**: talentsテーブルの全4,819人のmoney_max_one_yearが**NULL設定**

### 4-3. 各予算区分に該当するタレント数（STEP 0フィルタリング結果）

```
- 1,000万円未満                 0人  ❌
- 1,000万円～3,000万円未満       0人  ❌
- 3,000万円～1億円未満           0人  ❌
- 1億円以上                     0人  ❌
───────────────────────────────────
合計                           0人  ❌
```

**原因**: talentsテーブルの money_max_one_year が全てNULL → 全てのフィルタリング条件から除外

### 4-4. STEP 0フィルタリングの実装例

```sql
-- ユーザーが「1,000万円～3,000万円未満」（ID=2）を選択した場合
-- 期待される金額: max_amount = 29,999,999

SELECT talents.* FROM talents
WHERE money_max_one_year <= 29999999
  AND money_max_one_year IS NOT NULL
LIMIT 30;

-- 現在の問題: money_max_one_year = NULL のため、0件になる
```

---

## フロントエンド連携

### 5-1. 現状: APIエンドポイント未実装

```python
# backend/app/main.py の現在の登録ルーター
app.include_router(health.router, prefix="/api", tags=["Health Check"])
app.include_router(target_segments.router, prefix="/api", tags=["Master Data"])
app.include_router(industries.router, prefix="/api", tags=["Master Data"])
app.include_router(matching.router, prefix="/api", tags=["Matching Engine"])

# ❌ budget_ranges エンドポイントがない！
```

### 5-2. 必要なエンドポイント

```
GET /api/budget-ranges
  説明: 全予算区分を取得
  レスポンス: JSON形式の予算区分リスト
```

### 5-3. 期待されるAPIレスポンス

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "1,000万円未満",
      "min_amount": 0,
      "max_amount": 999,
      "display_order": 1
    },
    {
      "id": 2,
      "name": "1,000万円～3,000万円未満",
      "min_amount": 1000,
      "max_amount": 2999,
      "display_order": 2
    },
    {
      "id": 3,
      "name": "3,000万円～1億円未満",
      "min_amount": 3000,
      "max_amount": 9999,
      "display_order": 3
    },
    {
      "id": 4,
      "name": "1億円以上",
      "min_amount": 10000,
      "max_amount": null,
      "display_order": 4
    }
  ]
}
```

### 5-4. フロントエンド診断フロー

```
┌─────────────────────────────────────────────┐
│ 1. 初期化                                   │
│ GET /api/budget-ranges                      │
│ → 予算区分リストを取得して選択肢に表示      │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 2. ユーザー入力                             │
│ 例: ID=2 (1,000万円～3,000万円未満) を選択  │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 3. マッチング計算開始                       │
│ STEP 0: WHERE money_max_one_year <= 29999999│
│ (max_amount の値を使用)                     │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 4. 5段階マッチングロジック実行              │
│ STEP 1 ～ STEP 5                            │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 5. 結果表示                                 │
│ マッチングスコア付きタレントリスト          │
└─────────────────────────────────────────────┘
```

---

## トラブルシューティング

### 6-1. よくある問題と原因

#### 問題1: talentsテーブルで「各予算区分に該当するタレント数」がすべて0人

**症状**:
```
- 1,000万円未満                 0人
- 1,000万円～3,000万円未満       0人
- 3,000万円～1億円未満           0人
- 1億円以上                     0人
```

**原因**: talentsテーブルの money_max_one_year が全てNULL

**対処法**:
1. VRデータ/TPRデータのインポート状況を確認
2. `UPDATE talents SET money_max_one_year = ... WHERE ...` で値を設定
3. データインポートスクリプトを再実行

#### 問題2: 金額の単位が合致しない

**症状**:
```
現在の値:  min_amount=1000, max_amount=2999
期待値:   min_amount=10000000, max_amount=29999999
差分:     1/10000倍の値
```

**原因**: insert_budget_ranges.py で設定された値が正しくない

**対処法**:
1. insert_budget_ranges.py の budget_data を修正
2. DELETE FROM budget_ranges; で既存データを削除
3. insert_budget_ranges.py を再実行

#### 問題3: 予算区分がフロント画面で表示されない

**症状**: 選択肢メニューに予算区分がない

**原因**: 
- APIエンドポイント `/api/budget-ranges` が未実装
- フロントエンドが呼び出せない

**対処法**:
1. FastAPI に budget_ranges.py エンドポイントを実装
2. app/main.py に include_router を追加
3. フロントエンドから GET /api/budget-ranges を呼び出し

#### 問題4: マッチング結果が返されない（0件）

**症状**: 
```
POST /api/matching の後、data が empty array
```

**原因**: 
- STEP 0フィルタリングで全タレントが除外
- talentsの money_max_one_year が未設定
- budget_ranges の金額が小さすぎる

**対処法**:
1. talentsテーブルのデータを確認
2. budget_ranges の金額を確認
3. SELECT COUNT(*) FROM talents WHERE money_max_one_year ... で件数確認

---

## 修正が必要な箇所

### 7-1. 最優先度: 実装必須

#### 【優先度1】talentsテーブルのmoney_max_one_yearの設定

**現状**: 全件NULL（4,819人）

**必要な対応**:
```sql
-- VRデータ/TPRデータから適切な金額を取得して設定
UPDATE talents SET money_max_one_year = ... WHERE ...;
```

**確認方法**:
```sql
SELECT COUNT(*) FROM talents WHERE money_max_one_year > 0;
-- 期待値: 4,819件（または一部）
```

#### 【優先度2】budget_rangesの金額修正

**現状**: 値が小さすぎる（1,000 vs 10,000,000）

**修正内容**:
```python
# insert_budget_ranges.py の budget_data を修正
budget_data = [
    {"name": "1,000万円未満", "min_amount": 0, "max_amount": 9999999, "display_order": 1},
    {"name": "1,000万円～3,000万円未満", "min_amount": 10000000, "max_amount": 29999999, "display_order": 2},
    {"name": "3,000万円～1億円未満", "min_amount": 30000000, "max_amount": 99999999, "display_order": 3},
    {"name": "1億円以上", "min_amount": 100000000, "max_amount": None, "display_order": 4},
]
```

**実行手順**:
```bash
# 1. 既存データを削除
mysql> DELETE FROM budget_ranges;

# 2. スクリプトを実行
python3 insert_budget_ranges.py

# 3. 確認
SELECT * FROM budget_ranges ORDER BY display_order;
```

#### 【優先度3】FastAPI エンドポイント実装

**ファイル**: backend/app/api/endpoints/budget_ranges.py（新規作成）

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connection import get_db_session
from app.schemas.budget_ranges import BudgetRangeResponse

router = APIRouter()

@router.get("/budget-ranges", response_model=list[BudgetRangeResponse])
async def get_budget_ranges(session: AsyncSession = Depends(get_db_session)):
    """全予算区分を取得"""
    # SELECT * FROM budget_ranges ORDER BY display_order
    ...
```

**app/main.py に追加**:
```python
from app.api.endpoints import budget_ranges
app.include_router(budget_ranges.router, prefix="/api", tags=["Master Data"])
```

### 7-2. 次優先度: パフォーマンス改善

#### インデックス追加

```sql
-- display_order でのクエリ高速化
CREATE INDEX idx_budget_ranges_display_order ON budget_ranges(display_order);

-- 将来の検索用
CREATE INDEX idx_budget_ranges_min_max ON budget_ranges(min_amount, max_amount);
```

#### 制約追加

```sql
-- 金額の妥当性をDB側で担保
ALTER TABLE budget_ranges 
ADD CONSTRAINT check_amounts CHECK (min_amount <= max_amount OR max_amount IS NULL);

-- 名称の一意性
ALTER TABLE budget_ranges 
ADD CONSTRAINT unique_budget_name UNIQUE(name);
```

---

## 実装チェックリスト

- [ ] 【最優先】talentsテーブルの money_max_one_year にデータを入力
  - [ ] VRデータの確認
  - [ ] TPRデータの確認
  - [ ] UPDATE実行
  - [ ] SELECT COUNT(*) で検証

- [ ] 【最優先】budget_rangesの金額を修正
  - [ ] insert_budget_ranges.py の値を修正
  - [ ] DELETE FROM budget_ranges;
  - [ ] python3 insert_budget_ranges.py 実行
  - [ ] SELECT * FROM budget_ranges; で確認

- [ ] 【必須】FastAPI エンドポイント実装
  - [ ] backend/app/api/endpoints/budget_ranges.py 作成
  - [ ] GET /api/budget-ranges 実装
  - [ ] app/main.py に登録
  - [ ] 動作確認（curl等）

- [ ] 【推奨】フロントエンド対応
  - [ ] GET /api/budget-ranges 呼び出し追加
  - [ ] 選択肢メニューに予算区分を表示
  - [ ] ユーザー選択値をマッチングAPIに送信

- [ ] 【推奨】インデックス追加
  - [ ] display_order インデックス
  - [ ] min_amount, max_amount 複合インデックス

- [ ] 【推奨】制約追加
  - [ ] CHECK 制約（min_amount <= max_amount）
  - [ ] UNIQUE 制約（name）

---

## 参考資料

### CLAUDE.md 関連記述

```yaml
# 5段階マッチングロジック仕様 - STEP 0
STEP 0: 予算フィルタリング
  - テーブル: talents.money_max_one_year
  - 条件: <= ユーザー選択予算上限

# テスト認証情報
test_budget: 1,000万円～3,000万円未満
```

### APIエンドポイント命名規則

```yaml
命名規則:
  - RESTful形式を厳守
  - 複数形を使用 (/talents, /industries, /budget-ranges)
  - ケバブケース使用

主要エンドポイント:
  - GET /api/budget-ranges (新規実装が必要)
  - GET /api/industries (既実装)
  - GET /api/target-segments (既実装)
```

---

## まとめ

### 現状

| 項目 | 状態 | 備考 |
|------|------|------|
| テーブル構造 | ✅ OK | CREATE TABLE文はCLAUDE.md準拠 |
| テーブルデータ | ⚠️ 部分的 | 名称はOK、金額に問題 |
| 名称の正確性 | ✅ OK | ワーカー説明資料と完全一致 |
| 金額の正確性 | ❌ NG | 1/10000倍の値になっている |
| talentsとの連携 | ❌ NG | money_max_one_year全件NULL |
| APIエンドポイント | ❌ NG | 未実装 |
| フロントエンド対応 | ❌ NG | 未実装 |

### 重大な問題

1. **talentsテーブルのmoney_max_one_year全件NULL** → STEP 0フィルタリング不可
2. **budget_rangesの金額が小さすぎる** → 金額単位の不一致
3. **APIエンドポイント未実装** → フロント画面で選択肢が表示されない

### 次のステップ

1. talentsテーブルに正確な money_max_one_year を入力
2. budget_rangesの金額を修正（insert_budget_ranges.py を再実行）
3. FastAPI に budget_ranges エンドポイント実装
4. フロントエンド診断フローで利用可能に

---

**分析完了**: 2025-12-03  
**推奨対応開始時期**: 即時（STEP 0フィルタリング必須機能）
