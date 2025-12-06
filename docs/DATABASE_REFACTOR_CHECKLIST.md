# データベース再構築に伴うコード修正チェックリスト

## プロジェクト情報
- **準備日**: 2025-12-03
- **対象**: Excelの正しいDB構造への完全一致
- **現在のコード**: AIが推測で作成した間違ったスキーマに基づく
- **目標**: ワーカー説明資料に完全準拠したDB構造への修正

---

## 1. バックエンド（FastAPI）のDB参照箇所

### 1.1 テーブル名の確認・修正

#### 現在のテーブル名
- ✅ `talents` - OK（正しい）
- ✅ `talent_scores` - OK（正しい）
- ✅ `talent_images` - OK（正しい）
- ✅ `industries` - OK（正しい）
- ✅ `target_segments` - OK（正しい）
- ✅ `budget_ranges` - OK（正しい）
- ✅ `image_items` - OK（正しい）
- ⚠️ `industry_images` - 変更なし（ワーカー説明資料に記載なし）→ 保持推奨
- ❌ `talent_cm_history` - 削除予定（スコープ外）
- ❌ その他追加テーブル - スコープ外

### 1.2 カラム名の確認・修正

#### talents テーブル
**現在の実装**:
```python
id, account_id, name, name_normalized, kana, gender, birth_year, birthday, 
category, company_name, image_name, prefecture_code, official_url, del_flag, 
money_max_one_year
```

**期待値（ワーカー説明資料）**:
```
- account_id      : タレントの一意ID（主キー）✅
- name_full       : タレント名（VR/TPRデータとの照合に使用）❌ 現在は name
- gender          : 性別 ✅
- money_min_one_year : 年間契約金額（最小） ❌ 欠落
- money_max_one_year : 年間契約金額（最大） ✅
```

**修正アクション**:
- [ ] `name` カラムを `name_full` に変更（スペース除去済み）
- [ ] `money_min_one_year` カラムを追加
- [ ] マイグレーション: UPDATE talents SET name_full = name WHERE account_id > 0
- [ ] 依存コード全て修正（後述）

#### talent_scores テーブル
**現在の実装**:
```python
id, talent_id, target_segment_id, vr_popularity, tpr_power_score, 
base_power_score, created_at
```

**期待値（ワーカー説明資料）**:
```
- account_id        : タレントID（外部キー）❌ 現在は talent_id
- target_segment_id : ターゲット層ID（1〜8）✅
- vr_popularity     : VR人気度 ✅
- tpr_power_score   : TPRパワースコア ✅
- base_power_score  : 基礎パワー得点（計算済み）✅
```

**修正アクション**:
- [ ] 外部キーをtalent_idのままとするが、VR/TPRデータ取込時は account_id で照合
- [ ] 照合ロジック確認: talent_idの生成ルール（ワーカー説明資料：「name_full で文字列照合」）
- [ ] base_power_scoreは事前計算で設定されているか確認

#### talent_images テーブル
**現在の実装**:
```python
id, talent_id, target_segment_id, image_item_id, score, created_at
```

**期待値（ワーカー説明資料）**:
```
- account_id        : タレントID（外部キー）❌ 現在は talent_id
- target_segment_id : ターゲット層ID ✅
- image_funny       : おもしろい（スコア）
- image_clean       : 清潔感がある
- image_unique      : 個性的な
- image_trustworthy : 信頼できる
- image_cute        : かわいい
- image_cool        : カッコいい
- image_mature      : 大人の魅力がある
```

**現在の実装問題**:
- スキーマ設計が正反対（image_item_id + score の組み合わせ）
- ワーカー説明資料では「7つのイメージ項目が各行のカラム」

**修正アクション**:
- [ ] **スキーマ再設計検討**: 正規化(現在) vs 非正規化(期待) の確認
- [ ] 現在の正規化形式を保持する場合: クエリ側で変換
- [ ] ワーカー説明資料と完全一致させる場合: テーブル再設計（大規模変更）
- [ ] マッチングロジックのSTEP2で使用、確認必須

---

### 1.3 SQL クエリの確認・修正

#### ファイル: `/backend/app/api/endpoints/matching.py`

**問題箇所1: STEP 0 予算フィルタリング**
```python
# 行89-100: アルコール業界の年齢フィルタ
# birth_year を使用して計算している
# ワーカー説明資料では「money_max_one_year <= ユーザー予算上限」のみ
# 年齢フィルタは期待値に記載なし

修正アクション:
- [ ] requirements.md確認：アルコール業界フィルタは本仕様か
- [ ] 本仕様の場合：コードは正しい
- [ ] スコープ外の場合：削除検討
```

**問題箇所2: talent.name 参照**
```python
# 行87: SELECT DISTINCT t.id AS talent_id, t.account_id, t.name, t.kana, t.category
# 修正後:
# SELECT DISTINCT t.id AS talent_id, t.account_id, t.name_full, t.kana, t.category
```

**問題箇所3: talent_images の集約ロジック**
```python
# 行112-139: STEP2 業種イメージ査定
# 現在: PERCENT_RANK() OVER (... ORDER BY ti.score DESC) で各イメージ項目ごとに順位計算
# ワーカー説明資料と照合確認必須

修正アクション:
- [ ] 「順位は同じターゲット層内での順位」を確認
- [ ] 7つのイメージ項目の取扱い確認
```

#### ファイル: `/backend/app/api/endpoints/industries.py`

**問題箇所: industry_images の参照**
```python
# 行33-41: selectinload で industry_images を取得
# ワーカー説明資料では required_image_id が業種の1個のみ
# 現在: industry_images テーブルは 1:1 マッピング

修正アクション:
- [ ] 1業種 = 1イメージ項目 の関係確認
- [ ] 複数イメージある場合: クエリ修正
```

---

### 1.4 スキーマ（Pydantic）の確認・修正

#### ファイル: `/backend/app/schemas/matching.py`

**TalentResult型**:
```python
# 現在:
talent_id: int
account_id: int
name: str
kana: Optional[str]
category: Optional[str]
matching_score: float
ranking: int
base_power_score: Optional[float]
image_adjustment: Optional[float]

# ワーカー説明資料では特に指定なし（基本情報のみ）
# クライアント表示要件確認後に追加フィールド判定
```

**修正アクション**:
- [ ] account_id は返却必須か確認（VR/TPRリンク用）
- [ ] base_power_score, image_adjustment は内部用か、クライアント表示か確認

---

### 1.5 データ型・型ヒントの確認・修正

#### ファイル: `/backend/app/models/__init__.py`

**Talentモデル**:
```python
# 修正前: name = Column(String(255), nullable=False, index=True)
# 修正後: name_full = Column(String(255), nullable=False, index=True)
修正アクション:
- [ ] カラム名変更: name → name_full
- [ ] マイグレーション実施
- [ ] 既存データ UPDATE
```

**TalentScoreモデル**:
```python
# 現在の実装は正しい可能性が高い
# テスト検証でVR/TPR計算の正確性確認

修正アクション:
- [ ] base_power_score = (vr_popularity + tpr_power_score) / 2 の計算式確認
- [ ] NULL処理の仕様確認
```

**TalentImageモデル**:
```python
# スキーマ正規化の確認（7つのイメージが1行に列として存在する場合）

修正アクション:
- [ ] Excelソースの実際の構造確認
- [ ] 現在の正規化形式で機能するか検証
- [ ] パフォーマンス確認（56,448件）
```

---

## 2. フロントエンド（Next.js）のDB関連箇所

### 2.1 型定義の修正

#### ファイル: `/frontend/src/types/index.ts`

**TalentResult型**:
```typescript
// 現在:
export interface TalentResult {
  talent_id: number;
  name: string;
  match_score: number;
  ranking: number;
  imageUrl?: string;
  base_power_score?: number;
  image_adjustment_score?: number;
  base_reflection_score?: number;
}

// 修正後：
export interface TalentResult {
  talent_id: number;
  account_id: number;              // ❌ 追加必須？
  name: string;                    // バックエンド → name_full
  kana?: string;                   // ❌ 追加推奨
  category?: string;               // ❌ 追加推奨
  matching_score: number;          // 変更: match_score → matching_score
  ranking: number;
  base_power_score?: number;
  image_adjustment?: number;       // 変更: image_adjustment_score
  imageUrl?: string;
}

修正アクション:
- [ ] account_id の使用判定
- [ ] kana, category の使用判定
- [ ] フィールド名の統一（snake_case）
```

**FormData型（STEP 3 の予算フィールド）**:
```typescript
// 現在: q3_3: string（フォーム内部用）
// バックエンド送信時: budget（整形後）

修正アクション:
- [ ] フォーム入力値 → API送信値の変換ロジック確認
- [ ] 予算区分の マッピング: 「1,000万円～3,000万円未満」の正確性
```

---

### 2.2 API呼び出し部分の修正

#### ファイル: `/frontend/src/lib/api.ts`

**MatchingApiRequest型**:
```typescript
// 現在:
interface MatchingApiRequest {
  industry: string;
  target_segments: string[];
  budget: string;
  company_name: string;
  email: string;
}

// バックエンド期待値の確認:
// app/schemas/matching.py MatchingFormData と一致するか確認

修正アクション:
- [ ] target_segments のフォーマット確認
  - 期待値: ["女性20-34", "女性35-49"] のような配列
  - 実装: formData.q3 をそのまま使用
  - 確認: ワーカー説明資料の「ターゲット層選択」と一致するか
  
- [ ] 予算区分の値の確認
  - 期待値: "1,000万円～3,000万円未満"
  - 実装: formData.q3_3 をそのまま使用
  - DB: budget_ranges.name の正確な値と一致するか
```

**transformFormDataToApiRequest 関数**:
```typescript
// 現在の実装は単純な値のマッピング
// 修正不要（値の正確性は フロント/バック両側で検証）

修正アクション:
- [ ] FormData.q2 (業種) → industry: 業種マスタの name と一致するか
- [ ] FormData.q3 (ターゲット層) → target_segments: target_segments マスタの name と一致するか
- [ ] FormData.q3_3 (予算) → budget: budget_ranges マスタの name と一致するか
```

**callMatchingApi 関数のレスポンス変換**:
```typescript
// 現在の変換:
return data.results.map((item) => ({
  talent_id: item.talent_id,
  name: item.name,
  match_score: item.matching_score,    // ❌ 型名不統一
  ranking: item.ranking,
  base_power_score: item.base_power_score,
  image_adjustment_score: item.image_adjustment,  // ❌ 型名不統一
  base_reflection_score: item.base_power_score + item.image_adjustment,
}));

修正箇所:
- [ ] account_id の追加（バックエンドレスポンスに含まれていることを確認）
- [ ] kana, category の追加（バックエンドレスポンスに含まれていることを確認）
- [ ] フィールド名の統一:
  - matching_score vs match_score
  - image_adjustment vs image_adjustment_score
```

---

### 2.3 コンポーネント内の DB参照

#### ファイル: `/frontend/src/components/diagnosis/TalentCastingForm.tsx`

**フォーム送信時のAPI呼び出し**:
```typescript
// 行149: callMatchingApi(formData) の呼び出し
// 変換ロジック確認:
// FormData (内部形式) → MatchingApiRequest (API形式)

修正アクション:
- [ ] formData.q2 (業種) → industry: 正確なマッピング
- [ ] formData.q3 (ターゲット層配列) → target_segments: フォーマット確認
- [ ] formData.q3_3 (予算) → budget: 正確なマッピング
- [ ] formData.q4, q5, q6, q7 (企業情報) → company_name, email の確認
```

#### ファイル: `/frontend/src/components/diagnosis/Results/ResultsPage.tsx`

**結果表示**:
```typescript
// TalentResult[] を表示する部分
// 修正後の型変更に対応

修正アクション:
- [ ] 各フィールドの表示ロジック確認
- [ ] account_id の表示/非表示判定
- [ ] kana, category の表示確認
```

---

## 3. ワーカー説明資料との照合

### 3.1 テーブル構成の確認

**期待値（ワーカー説明資料 p.4）**:
```
【データテーブル】3つ
├── talents          : タレント基本情報（約2,000件）
├── talent_scores    : VR人気度・TPRスコア（約16,000件）
└── talent_images    : イメージスコア7項目（約16,000件）

【マスタテーブル】4つ
├── industries       : 業種マスタ（20件）
├── target_segments  : ターゲット層マスタ（8件）
├── budget_ranges    : 予算区分マスタ（4件）
└── image_items      : イメージ項目マスタ（7件）
```

**実際のDB状況（2025-12-02調査）**:
```
✅ テーブル名は全て一致
⚠️ 件数が異なる：
   - talents: 期待 ~2,000 → 実際 4,810
   - talent_scores: 期待 ~16,000 → 実際 6,118
   - talent_images: 期待 ~16,000 → 実際 2,688
❌ 余分なテーブル: industry_images（使用中）, purpose_objectives（削除推奨）
```

**修正アクション**:
- [ ] talent_images のVRデータ大幅追加（現在 4.8% → 100%）
- [ ] talent_scores のTPRデータ追加（現在 59.7% → 100%）
- [ ] purpose_objectives テーブルの削除検討

### 3.2 カラム対応表

| ワーカー説明資料 | 現在のテーブル | 修正状況 |
|----------------|--------------|--------|
| account_id | talents.account_id | ✅ OK |
| name_full | talents.name | ❌ 変更必須 |
| money_max_one_year | talents.money_max_one_year | ✅ OK |
| target_segment_id | talent_scores.target_segment_id | ✅ OK |
| vr_popularity | talent_scores.vr_popularity | ✅ OK |
| tpr_power_score | talent_scores.tpr_power_score | ✅ OK |
| base_power_score | talent_scores.base_power_score | ✅ OK |
| image_xxx (7項目) | talent_images.image_item_id + score | ⚠️ スキーマ確認必須 |
| industry.required_image_id | industry_images.image_item_id | ⚠️ 1:N vs 1:1 確認 |

---

## 4. マッチングロジック（STEP 0-5）の確認

### 4.1 STEP 0: 予算フィルタリング

**期待値**:
```
WHERE talents.money_max_one_year <= ユーザー選択予算上限
```

**現在の実装**:
```python
# matching.py 行89-100
WHERE (
  t.money_max_one_year IS NULL
  OR (
    ($1 = 0 OR t.money_max_one_year >= $1)  # min_budget
    AND ($2 = 'Infinity'::float8 OR t.money_max_one_year <= $2)  # max_budget
  )
)
```

**問題**: min_budget の条件が逆ではないか

修正アクション:
- [ ] ワーカー説明資料の「予算フィルタリング」をもう一度確認
- [ ] 期待値: 「契約金額3,000万円以下のタレント」の意味確認
- [ ] クエリの >= / <= の方向を確認

### 4.2 STEP 1: 基礎パワー得点

**期待値**:
```
base_power_score = (vr_popularity + tpr_power_score) / 2
```

**現在の実装**:
```python
# talent_scores.base_power_score を直接使用（事前計算済み）
COALESCE(ts.base_power_score, 0) AS base_power_score
```

修正アクション:
- [ ] base_power_score は INSERT時に計算されているか確認
- [ ] VR/TPRデータインポート時の計算ロジック確認
- [ ] NULLの場合の処理確認

### 4.3 STEP 2: 業種イメージ査定

**期待値**:
```
1. 業種の「求められるイメージ」を特定
2. そのイメージでの全タレントの順位（%）を算出
3. 順位帯に応じて加減点

点数表:
- 上位15%: +12点
- 16～30%: +6点
- 31～50%: +3点
- 51～70%: -3点
- 71～85%: -6点
- 86～100%: -12点
```

**現在の実装**:
```python
# matching.py 行112-139
CASE
  WHEN percentile_rank <= 0.15 THEN 12.0
  WHEN percentile_rank <= 0.30 THEN 6.0
  WHEN percentile_rank <= 0.50 THEN 0.0  # ❌ 期待値は +3点
  WHEN percentile_rank <= 0.70 THEN -6.0  # ❌ 期待値は -3点
  ELSE -12.0
END
```

**問題**: 点数配置が異なる

修正アクション:
- [ ] ワーカー説明資料 p.3 「STEP2の加減点表」を再確認
- [ ] 51～70% の -6点 が本当に -3点ではないか確認
- [ ] 修正: WHEN percentile_rank <= 0.50 THEN 3.0
- [ ] 修正: WHEN percentile_rank <= 0.70 THEN -3.0

### 4.4 STEP 5: マッチングスコア振り分け

**期待値**:
```
1～3位: 99.7～97.0点 → ランダム（高い順）
4～10位: 96.9～93.0点
11～20位: 92.9～89.0点
21～30位: 88.9～86.0点
```

**現在の実装**:
```python
# matching.py 行195-210
if 1 <= ranking <= 3:
  score_range = (97.0, 99.7)  # ✅ OK
elif 4 <= ranking <= 10:
  score_range = (93.0, 96.9)  # ✅ OK
elif 11 <= ranking <= 20:
  score_range = (89.0, 92.9)  # ✅ OK
elif 21 <= ranking <= 30:
  score_range = (86.0, 88.9)  # ✅ OK
```

修正アクション:
- [ ] 実装は正しい
- [ ] random.uniform() のランダム性確認

---

## 5. 修正が必要な具体的ファイル一覧

### バックエンド（優先順）

**優先度1（必須修正）**:
- [ ] `/backend/app/models/__init__.py`
  - talents テーブル: name → name_full
  - talents テーブル: money_min_one_year 追加

- [ ] `/backend/app/api/endpoints/matching.py`
  - STEP 2 の加減点修正（-6点 → -3点、0点 → +3点）
  - t.name → t.name_full 参照の修正
  - budget_min 条件の確認

- [ ] `/backend/app/schemas/matching.py`
  - TalentResult に account_id, kana, category を確認
  - フィールド名の統一確認

**優先度2（確認修正）**:
- [ ] `/backend/app/api/endpoints/industries.py`
  - industry_images の1:1マッピング確認

- [ ] `/backend/scripts/import_talent_data.py` (存在確認)
  - VR/TPRデータインポート時の base_power_score 計算

### フロントエンド（優先順）

**優先度1（必須修正）**:
- [ ] `/frontend/src/types/index.ts`
  - TalentResult 型の整理
  - FormData 型の確認

- [ ] `/frontend/src/lib/api.ts`
  - transformFormDataToApiRequest の入力値確認
  - callMatchingApi のレスポンス変換で account_id, kana, category 追加
  - フィールド名の統一

**優先度2（パフォーマンス）**:
- [ ] `/frontend/src/components/diagnosis/Results/ResultsPage.tsx`
  - 新しいフィールドの表示ロジック対応

---

## 6. テスト計画

### 単体テスト

- [ ] Talent モデル: account_id → name_full の ID解決確認
- [ ] TalentScore: base_power_score 計算式の検証
- [ ] TalentImage: PERCENT_RANK() の順位計算検証
- [ ] STEP 2: 加減点配置の修正検証

### 統合テスト

- [ ] API エンドポイント:
  - POST /api/matching の完全フロー検証
  - レスポンスの型・値の確認
  
- [ ] フロントエンド:
  - フォーム送信 → API呼び出し → 結果表示の完全フロー

### データ検証テスト

- [ ] VR/TPRデータインポート後:
  - talents.name_full が正しく設定されているか
  - talent_scores.base_power_score が計算されているか
  - talent_images のカバー率が 100% に達しているか

---

## 7. マイグレーション計画

### Phase 1: スキーマ準備

```sql
-- talents テーブル修正
ALTER TABLE talents RENAME COLUMN name TO name_full;
ALTER TABLE talents ADD COLUMN money_min_one_year NUMERIC(12,2);
UPDATE talents SET money_min_one_year = 0 WHERE money_min_one_year IS NULL;

-- インデックス更新
CREATE INDEX idx_talents_name_full ON talents(name_full);
DROP INDEX idx_talents_name;
```

### Phase 2: コード修正・テスト

- コード修正実施
- ローカル環境でのテスト
- VR/TPRデータインポート検証

### Phase 3: 本番デプロイ

- マイグレーション実行
- API デプロイ
- フロントエンド デプロイ
- 本番環境での動作確認

---

## 8. リスク・懸念事項

### データ整合性
- [ ] VR/TPRデータの name_full マッチングがうまくいくか（スペース処理）
- [ ] talent_id の生成ルール確認
- [ ] 照合できないレコードの処理方法

### パフォーマンス
- [ ] talent_images テーブルの 56,448 件データでの PERCENT_RANK() 処理速度
- [ ] インデックス設定の最適化確認

### ワーカー説明資料との解釈
- [ ] 「順位%」の算出対象: 全タレント vs 同一ターゲット層 vs その他
- [ ] 業種-イメージの 1:1 vs 1:N の関係確認
- [ ] STEP 2 の加減点配置再確認（-6点 vs -3点）

---

## チェックリスト実行順序

1. **準備フェーズ**
   - ワーカー説明資料の最終確認
   - Excel ソースデータの確認
   - 現在の実装との差分リストアップ

2. **修正フェーズ（優先度順）**
   - talents.name → name_full 変更
   - STEP 2 の加減点修正
   - account_id, kana, category の追加
   - VR/TPRデータインポート計算式確認

3. **テストフェーズ**
   - 単体テスト実施
   - 統合テスト実施
   - データ検証テスト実施

4. **デプロイフェーズ**
   - マイグレーション実行
   - 本番環境での動作確認
   - ワーカー説明資料との最終確認

---

**作成日**: 2025-12-03
**ステータス**: 準備中
**次のアクション**: ワーカー説明資料の最終確認 & Excel ソース確認
