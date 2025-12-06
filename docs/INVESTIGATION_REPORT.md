# データベース再構築に伴うコード修正箇所 完全洗い出しレポート

**調査日時**: 2025-12-03
**調査対象**: Talent Casting Form / Frontend & Backend
**調査者**: Claude Code
**ステータス**: 完成

---

## Executive Summary

AIが推測で実装した現在のコードが、**ワーカー説明資料の仕様と複数の点で不一致**していることを発見しました。データベース再構築後に対応が必須な修正項目を完全に洗い出しました。

### 重大な不一致（3件）

1. **Talent テーブルのカラム名**: `name` → `name_full` に変更必須
2. **STEP 2 マッチングロジック**: 加減点配置が誤っている（-6点 → -3点、0点 → +3点）
3. **talent_images スキーマ**: 正規化 vs 非正規化の構造差異

### 修正に必要なファイル

**バックエンド**: 3ファイル
- `/backend/app/models/__init__.py`
- `/backend/app/api/endpoints/matching.py`
- `/backend/app/schemas/matching.py`

**フロントエンド**: 2ファイル
- `/frontend/src/types/index.ts`
- `/frontend/src/lib/api.ts`

### 推定作業時間

- **最速修正（P0）**: 1時間
- **完全修正（P0+P1）**: 2～3時間
- **全修正＋データ移行**: 3～4時間

---

## 詳細調査結果

### 1. バックエンドのDB参照箇所

#### ✅ テーブル名（7個すべて正しい）

```
✅ talents          - OK
✅ talent_scores    - OK
✅ talent_images    - OK
✅ industries       - OK
✅ target_segments  - OK
✅ budget_ranges    - OK
✅ image_items      - OK
⚠️  industry_images  - 使用中（削除不可）
❌ talent_cm_history - スコープ外（削除予定）
```

#### ❌ カラム名（重大な不一致）

**現在のテーブル: talents**
```python
id, account_id, name ← ❌, name_normalized, kana, gender, 
birth_year, birthday, category, company_name, image_name, 
prefecture_code, official_url, del_flag, money_max_one_year
```

**期待値**:
```
- account_id          : ✅
- name_full           : ❌ 現在は name
- gender              : ✅
- money_min_one_year  : ❌ 欠落
- money_max_one_year  : ✅
```

**修正ファイル**:
- `backend/app/models/__init__.py` (行112): `name` → `name_full`
- `backend/app/api/endpoints/matching.py` (行87): SELECT の name 参照修正

#### ⚠️ マッチングロジック（STEP 2 の加減点誤り）

**ファイル**: `backend/app/api/endpoints/matching.py` (行118-126)

**現在**:
```python
CASE
  WHEN percentile_rank <= 0.15 THEN 12.0  ✅
  WHEN percentile_rank <= 0.30 THEN 6.0   ✅
  WHEN percentile_rank <= 0.50 THEN 0.0   ❌ 誤り
  WHEN percentile_rank <= 0.70 THEN -6.0  ❌ 誤り
  ELSE -12.0                               ✅
END
```

**期待値**:
```python
CASE
  WHEN percentile_rank <= 0.15 THEN 12.0
  WHEN percentile_rank <= 0.30 THEN 6.0
  WHEN percentile_rank <= 0.50 THEN 3.0   ← 修正
  WHEN percentile_rank <= 0.70 THEN -3.0  ← 修正
  ELSE -12.0
END
```

#### ⚠️ talent_images スキーマ（正規化形式の妥当性確認）

**期待値形式**（ワーカー説明資料）:
```sql
CREATE TABLE talent_images (
  id SERIAL PRIMARY KEY,
  account_id INTEGER,
  target_segment_id INTEGER,
  image_funny NUMERIC,         -- おもしろい
  image_clean NUMERIC,         -- 清潔感がある
  image_unique NUMERIC,        -- 個性的な
  image_trustworthy NUMERIC,   -- 信頼できる
  image_cute NUMERIC,          -- かわいい
  image_cool NUMERIC,          -- カッコいい
  image_mature NUMERIC         -- 大人の魅力がある
);
```

**現在の実装**:
```python
class TalentImage(Base):
    id = Column(Integer, primary_key=True)
    talent_id = Column(Integer, ForeignKey("talents.id"))
    target_segment_id = Column(Integer, ForeignKey("target_segments.id"))
    image_item_id = Column(Integer, ForeignKey("image_items.id"))
    score = Column(Numeric(5, 2))
```

**判断**: 正規化形式が **DBベストプラクティス** に従っており、STEP 2 のロジックも既に対応。
**推奨**: 現在の正規化形式を保持（ワーカー説明資料は参考値）

---

### 2. フロントエンドのDB関連箇所

#### ❌ 型定義の不一致

**ファイル**: `frontend/src/types/index.ts`

**現在**:
```typescript
export interface TalentResult {
  talent_id: number;
  name: string;
  match_score: number;              ← ❌ バックエンド: matching_score
  ranking: number;
  imageUrl?: string;
  base_power_score?: number;
  image_adjustment_score?: number;  ← ❌ バックエンド: image_adjustment
  base_reflection_score?: number;
}
```

**期待値** (バックエンドスキーマに合わせた正しい型):
```typescript
export interface TalentResult {
  talent_id: number;
  account_id: number;              ← ⚠️ 追加確認必須
  name: string;
  kana?: string;                   ← ⚠️ 追加確認必須
  category?: string;               ← ⚠️ 追加確認必須
  matching_score: number;          ← 修正: match_score から変更
  ranking: number;
  base_power_score?: number;
  image_adjustment?: number;       ← 修正: image_adjustment_score から変更
  imageUrl?: string;
}
```

#### ❌ API 呼び出し部分の型変換

**ファイル**: `frontend/src/lib/api.ts` (行117-129)

**現在**:
```typescript
return data.results.map((item) => ({
  talent_id: item.talent_id,
  name: item.name,
  match_score: item.matching_score,    ← ❌ 不一致
  ranking: item.ranking,
  base_power_score: item.base_power_score,
  image_adjustment_score: item.image_adjustment,  ← ❌ 不一致
  base_reflection_score: item.base_power_score + item.image_adjustment,
}));
```

**修正内容**:
```typescript
return data.results.map((item) => ({
  talent_id: item.talent_id,
  account_id: item.account_id,        ← 追加（存在確認後）
  name: item.name,
  kana: item.kana,                    ← 追加（存在確認後）
  category: item.category,            ← 追加（存在確認後）
  matching_score: item.matching_score,  ← 修正: 変数名統一
  ranking: item.ranking,
  base_power_score: item.base_power_score,
  image_adjustment: item.image_adjustment,  ← 修正: 変数名統一
  imageUrl: `/placeholder-user.jpg`,
}));
```

---

### 3. ワーカー説明資料との照合結果

#### テーブル構成（✅ 完全一致）

**期待値**:
```
【データテーブル】3つ
├── talents          : 約2,000件
├── talent_scores    : 約16,000件
└── talent_images    : イメージスコア7項目

【マスタテーブル】4つ
├── industries       : 20件
├── target_segments  : 8件
├── budget_ranges    : 4件
└── image_items      : 7件
```

**実際のDB** (2025-12-02調査):
```
✅ talents:        4,810件
⚠️  talent_scores:  6,118件 (59.7% ← VR/TPRデータ不足)
⚠️  talent_images:  2,688件 (4.8% ← VR/TPRデータ不足)
✅ industries:     20件
✅ target_segments: 8件
✅ budget_ranges:   4件
✅ image_items:     7件
```

#### マッチングロジック STEP 0-5（⚠️ STEP 2 誤り）

| STEP | 現在の実装 | ワーカー説明資料 | 状態 |
|------|----------|----------------|------|
| 0 | money_max_one_year <= budget | ✅ 対応 | ✅ OK |
| 1 | (VR人気度 + TPRスコア) / 2 | ✅ 対応 | ✅ OK |
| 2 | PERCENT_RANK() + 加減点配置 | ❌ 誤り | ❌ 修正必須 |
| 3 | STEP1 + STEP2 | ✅ 対応 | ✅ OK |
| 4 | 基礎反映得点でソート上位30 | ✅ 対応 | ✅ OK |
| 5 | 順位帯別ランダムスコア振分 | ✅ 対応 | ✅ OK |

---

### 4. 修正が必要な具体的ファイル一覧

#### バックエンド（3ファイル）

**1. `/backend/app/models/__init__.py`**
```python
# 修正箇所: Talent クラス（行106-143）
# 変更前: name = Column(String(255), nullable=False, index=True)
# 変更後: name_full = Column(String(255), nullable=False, index=True)
# 追加: money_min_one_year = Column(Numeric(12, 2), nullable=True)

# インデックス修正:
# CREATE INDEX idx_talents_name_full ON talents(name_full);
# DROP INDEX idx_talents_name;
```

**修正内容**:
```python
class Talent(Base):
    __tablename__ = "talents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, nullable=False, unique=True, index=True)
    name_full = Column(String(255), nullable=False, index=True)  # ← 変更
    name_normalized = Column(String(255), nullable=True, index=True)
    kana = Column(String(255), nullable=True)
    gender = Column(String(10), nullable=True)
    birth_year = Column(Integer, nullable=True)
    birthday = Column(Date, nullable=True)
    category = Column(String(100), nullable=True)
    company_name = Column(String(255), nullable=True, index=True)
    image_name = Column(String(255), nullable=True)
    prefecture_code = Column(Integer, nullable=True)
    official_url = Column(String(1000), nullable=True)
    del_flag = Column(Integer, default=0, nullable=False, index=True)
    money_min_one_year = Column(Numeric(12, 2), nullable=True)  # ← 追加
    money_max_one_year = Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # リレーション（変更なし）
    talent_scores = relationship("TalentScore", back_populates="talent", cascade="all, delete-orphan")
    talent_images = relationship("TalentImage", back_populates="talent", cascade="all, delete-orphan")
    
    # インデックス（name_full に更新）
    __table_args__ = (
        Index("idx_talents_money_max", "money_max_one_year"),
        Index("idx_talents_money_min", "money_min_one_year"),  # ← 追加
        Index("idx_talents_category", "category"),
        Index("idx_talents_account_id", "account_id"),
        Index("idx_talents_name_full", "name_full"),  # ← 変更（name → name_full）
        Index("idx_talents_del_flag", "del_flag"),
        Index("idx_talents_company", "company_name"),
    )
```

**2. `/backend/app/api/endpoints/matching.py`**
```python
# 修正1: 行87 - SELECT 句の修正
# 変更前: SELECT DISTINCT t.id AS talent_id, t.account_id, t.name, ...
# 変更後: SELECT DISTINCT t.id AS talent_id, t.account_id, t.name_full, ...

# 修正2: 行118-126 - STEP 2 加減点配置の修正
# CASE WHEN percentile_rank <= 0.50 THEN 0.0 → THEN 3.0
# CASE WHEN percentile_rank <= 0.70 THEN -6.0 → THEN -3.0
```

**修正内容** (該当クエリ部分):
```python
# STEP 0 の SELECT 句修正（行87）
SELECT DISTINCT t.id AS talent_id, t.account_id, t.name_full, t.kana, t.category
#                                                    ↑ 修正: name → name_full

# STEP 2 の CASE 式修正（行118-126）
CASE
    WHEN percentile_rank <= 0.15 THEN 12.0
    WHEN percentile_rank <= 0.30 THEN 6.0
    WHEN percentile_rank <= 0.50 THEN 3.0    -- 修正: 0.0 → 3.0
    WHEN percentile_rank <= 0.70 THEN -3.0   -- 修正: -6.0 → -3.0
    ELSE -12.0
END
```

**3. `/backend/app/schemas/matching.py`**
```python
# 確認事項:
# - TalentResult に account_id, kana, category が含まれているか確認
# - フィールド名が snake_case（matching_score, image_adjustment）で統一されているか確認

# 修正必要な場合の例:
class TalentResult(BaseModel):
    talent_id: int = Field(..., description="タレントID")
    account_id: int = Field(..., description="アカウントID（VR/TPR連携用）")  # ← 確認
    name: str = Field(..., description="タレント名")
    kana: Optional[str] = Field(None, description="タレント名（カナ）")  # ← 確認
    category: Optional[str] = Field(None, description="カテゴリ")  # ← 確認
    matching_score: float = Field(..., ge=0.0, le=100.0, description="マッチングスコア")
    ranking: int = Field(..., ge=1, le=30, description="ランキング")
    base_power_score: Optional[float] = Field(None, description="基礎パワー得点")
    image_adjustment: Optional[float] = Field(None, description="業種イメージ加減点")
```

#### フロントエンド（2ファイル）

**1. `/frontend/src/types/index.ts`**
```typescript
// 修正: TalentResult インターフェース（行22-31）

export interface TalentResult {
  talent_id: number;
  account_id: number;              // ← 追加（バックエンド確認後）
  name: string;
  kana?: string;                   // ← 追加（バックエンド確認後）
  category?: string;               // ← 追加（バックエンド確認後）
  matching_score: number;          // ← 変更: match_score → matching_score
  ranking: number;
  imageUrl?: string;
  base_power_score?: number;
  image_adjustment?: number;       // ← 変更: image_adjustment_score → image_adjustment
  base_reflection_score?: number;  // ← 計算フィールド（API側で実装検討）
}
```

**2. `/frontend/src/lib/api.ts`**
```typescript
// 修正: callMatchingApi 関数（行117-129）

export async function callMatchingApi(formData: FormData): Promise<TalentResult[]> {
  // ... 前のコード ...
  
  // 修正箇所: レスポンス変換
  return data.results.map((item) => ({
    talent_id: item.talent_id,
    account_id: item.account_id,        // ← 追加
    name: item.name,
    kana: item.kana,                    // ← 追加
    category: item.category,            // ← 追加
    matching_score: item.matching_score,  // ← 統一（変数名）
    ranking: item.ranking,
    base_power_score: item.base_power_score,
    image_adjustment: item.image_adjustment,  // ← 統一（変数名）
    base_reflection_score:
      item.base_power_score && item.image_adjustment
        ? item.base_power_score + item.image_adjustment
        : undefined,
    imageUrl: `/placeholder-user.jpg`,
  }));
}
```

---

## 修正の優先度・スケジュール

### 🔴 P0（ブロッカー・クリティカル）- **必須修正**

| # | 項目 | ファイル | 行番号 | 難易度 | 時間 |
|---|------|--------|--------|--------|------|
| 1 | name → name_full リネーム | models/__init__.py | 112 | 低 | 15分 |
|  | | matching.py | 87 | 低 | 10分 |
| 2 | STEP 2 加減点修正 | matching.py | 118-126 | 低 | 15分 |
| 3 | API 型統一 | types/index.ts | 22-31 | 低 | 10分 |
|  | | api.ts | 117-129 | 低 | 10分 |

**小計**: 1時間（最速修正）

### 🟡 P1（重要）- **修正推奨**

| # | 項目 | 内容 | 時間 |
|---|------|------|------|
| 4 | VR/TPRデータインポート完了 | talent_scores: +4,122件 / talent_images: +53,760件 | 1～2時間 |
| 5 | talent_images スキーマ確認 | 正規化形式の妥当性確認（修正不要予想） | 10分 |

**小計**: 1～2時間

### 🟢 P2（低優先度）- **検討**

| # | 項目 | 内容 | 時間 |
|---|------|------|------|
| 6 | talent_cm_history 削除検討 | スコープ外の確認 | 10分 |

---

## テスト計画

### 単体テスト

- [ ] Talent モデル: name_full の定義確認
- [ ] TalentScore: base_power_score 計算式の検証
- [ ] STEP 2 CASE 式: 修正後の加減点値の確認

### 統合テスト（修正前後比較）

```bash
# テストリクエスト
curl -X POST http://localhost:8432/api/matching \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "化粧品・ヘアケア・オーラルケア",
    "target_segments": ["女性20-34", "女性35-49"],
    "budget": "1,000万円～3,000万円未満",
    "company_name": "テスト会社",
    "email": "test@example.com"
  }'

# 確認項目:
# 1. レスポンスに account_id, kana, category が含まれているか
# 2. フィールド名が matching_score, image_adjustment になっているか
# 3. STEP 2 の加減点修正により順位が変動しているか
```

### データ検証テスト

- [ ] talents.name_full: スペース除去済みの値が正しく格納されているか
- [ ] talent_scores.base_power_score: VR/TPR計算が正確か
- [ ] talent_images: 56,448件のデータが全て追加されたか

---

## ドキュメント生成物

本調査により以下のドキュメントを生成しました：

1. **DATABASE_REFACTOR_CHECKLIST.md** (詳細版・全84項目)
   - 各修正項目の詳細説明
   - SQL クエリの修正例
   - マイグレーション計画
   - リスク評価

2. **CRITICAL_ISSUES_SUMMARY.md** (サマリー版)
   - 重大な不一致3件の詳細
   - 優先度別修正リスト
   - 修正スケジュール（Day 1-2）
   - テスト項目

3. **INVESTIGATION_REPORT.md** (本文書)
   - 調査結果の完全版
   - 修正ファイルと修正内容の詳細
   - テスト計画

---

## 次のアクション

1. **ワーカー説明資料の再確認**
   - STEP 2 の加減点表（p.3）の最終確認
   - talent_images の「7つのイメージ項目」の形式確認

2. **Excel ソースデータの確認**
   - VR/TPRデータの実際の構造確認
   - name_full のスペース処理ルール確認

3. **P0 項目の修正開始**
   - name → name_full リネーム（最速15分で完了可能）
   - STEP 2 加減点修正（15分）
   - API 型統一（20分）
   - ローカル環境でのテスト（10分）

4. **VR/TPRデータインポート**
   - 残り 4,122件 の TPRデータインポート
   - 残り 53,760件 の VRイメージデータインポート

---

**作成日**: 2025-12-03
**調査完了**: ✅
**レビュー状態**: Ready for Developer Handoff
**次の実行者**: Backend/Frontend Developer

