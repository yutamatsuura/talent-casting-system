# データベース完全再構築による影響範囲分析（修正版）

## 📌 概要
エクセルファイル構造との完全同期に伴う、フロントエンドコードへの影響範囲を**全て**洗い出したドキュメントです。

**⚠️ 重要**: 単なる`name`→`name_full_for_matching`の変更ではなく、データベース構造の根本的変更による大規模修正が必要です。

**作成日**: 2025-12-03 (修正版)
**前提**: エクセル構造と完全同じデータベース構成への移行

---

## 🔥 **予想される主要構造変更**

### 1. **主キー変更**
```diff
- talent_id: number
+ account_id: number  // 主キーが変更
```

### 2. **テーブル正規化**
```sql
-- 現在: フラット構造
-- 変更後: 正規化された複数テーブル
talents          // 基本情報
talent_scores    // VR/TPRスコア（ターゲット層別）
talent_images    // 7つのイメージスコア（ターゲット層別）
```

### 3. **新フィールド追加**
```typescript
// 追加されるイメージスコア
interface TalentImages {
  image_funny: number;       // おもしろい
  image_clean: number;       // 清潔感がある
  image_unique: number;      // 個性的な
  image_trustworthy: number; // 信頼できる
  image_cute: number;        // かわいい
  image_cool: number;        // カッコいい
  image_mature: number;      // 大人の魅力がある
}

// 追加される基本情報
interface TalentBasic {
  gender: string;
  money_min_one_year: number;
  money_max_one_year: number;
  base_power_score: number; // 事前計算済み
}
```

### 4. **ターゲット層正規化**
```diff
- target_segments: string[] // 文字列配列
+ target_segment_id: number // 正規化されたID
```

---

## 🚨 **影響を受けるファイルと修正箇所**

### **【重要度：最高】型定義の全面書き直し**

**ファイル**: `src/types/index.ts`

#### 変更が必要なInterface:

1. **TalentResult interface (行22-31)**
```diff
export interface TalentResult {
- talent_id: number;
+ account_id: number;
- name: string;
+ name_full_for_matching: string;
  match_score: number;
  ranking: number;
  imageUrl?: string;
  base_power_score?: number;
- image_adjustment_score?: number;
+ // 7つのイメージスコア追加
+ image_funny?: number;
+ image_clean?: number;
+ image_unique?: number;
+ image_trustworthy?: number;
+ image_cute?: number;
+ image_cool?: number;
+ image_mature?: number;
+ // 基本情報追加
+ gender?: string;
+ money_min_one_year?: number;
+ money_max_one_year?: number;
+ target_segment_id?: number;
  base_reflection_score?: number;
}
```

2. **TalentDetailInfo interface (行320-336)**
```diff
export interface TalentDetailInfo {
- talent_id: number;
+ account_id: number;
- account_id?: number; // 削除（重複）
- name: string;
+ name_full_for_matching: string;
+ // 以下、TalentResultと同様の追加フィールド
}
```

3. **Talent interface (行232-273)**
```diff
export interface Talent {
- id: number;
+ account_id: number;
- name: string;
+ name_full_for_matching: string;
+ // 7つのイメージスコア、gender、money等を追加
}
```

### **【重要度：高】API通信層の全面改修**

**ファイル**: `src/lib/api.ts`

#### 1. **MatchingApiResponse interface (行28-41)**
```diff
interface MatchingApiResponse {
  success: boolean;
  total_results: number;
  results: Array<{
-   talent_id: number;
+   account_id: number;
-   account_id: number; // 削除（重複）
-   name: string;
+   name_full_for_matching: string;
    kana?: string;
    category?: string;
    matching_score: number;
    ranking: number;
    base_power_score?: number;
-   image_adjustment?: number;
+   // 7つのイメージスコア追加
+   image_funny?: number;
+   image_clean?: number;
+   image_unique?: number;
+   image_trustworthy?: number;
+   image_cute?: number;
+   image_cool?: number;
+   image_mature?: number;
+   // 基本情報追加
+   gender?: string;
+   money_min_one_year?: number;
+   money_max_one_year?: number;
+   target_segment_id?: number;
  }>;
}
```

#### 2. **APIレスポンス変換ロジック (行117-130)**
```diff
return data.results.map((item) => ({
- talent_id: item.talent_id,
+ account_id: item.account_id,
- name: item.name,
+ name_full_for_matching: item.name_full_for_matching,
  match_score: item.matching_score,
  ranking: item.ranking,
  base_power_score: item.base_power_score,
- image_adjustment_score: item.image_adjustment,
+ image_funny: item.image_funny,
+ image_clean: item.image_clean,
+ image_unique: item.image_unique,
+ image_trustworthy: item.image_trustworthy,
+ image_cute: item.image_cute,
+ image_cool: item.image_cool,
+ image_mature: item.image_mature,
+ gender: item.gender,
+ money_min_one_year: item.money_min_one_year,
+ money_max_one_year: item.money_max_one_year,
+ target_segment_id: item.target_segment_id,
  base_reflection_score:
-   item.base_power_score && item.image_adjustment
-     ? item.base_power_score + item.image_adjustment
+   // 業種イメージ査定の計算ロジック変更が必要
    : undefined,
}));
```

### **【重要度：中】UIコンポーネントの修正**

**ファイル**: `src/components/diagnosis/Results/ResultsPage.tsx`

#### 修正箇所:
```diff
// 行186: key属性
- key={talent.talent_id}
+ key={talent.account_id}

// 行277: タレント名表示
- {talent.name}
+ {talent.name_full_for_matching}
```

**ファイル**: `src/components/diagnosis/Results/TalentDetailModal.tsx`

#### 修正箇所:
```diff
// 行47: モックデータ
const mockDetailData: TalentDetailInfo = {
- talent_id: talent.talent_id,
+ account_id: talent.account_id,
- name: talent.name,
+ name_full_for_matching: talent.name_full_for_matching,
  // 以下同様の修正
};

// 行170: 表示
- {talent.name}
+ {talent.name_full_for_matching}
```

### **【重要度：低】レガシー型定義**

**ファイル**: `src/lib/talent-data.ts`

#### 修正箇所:
```diff
export type Talent = {
- id: number
+ account_id: number
- name: string
+ name_full_for_matching: string
  // その他フィールドも同様の修正が必要
}
```

---

## 📋 **修正作業の推奨順序**

### **Phase 1: 型定義の完全書き直し**
1. `src/types/index.ts` - 全interfaceの修正
2. TypeScriptコンパイルエラーの一括確認

### **Phase 2: API層の修正**
1. `src/lib/api.ts` - APIレスポンス構造修正
2. バックエンドとの型整合性確認

### **Phase 3: UI層の修正**
1. 各コンポーネントでの表示修正
2. 実機テストでの動作確認

### **Phase 4: レガシーコードの整理**
1. 不要なフィールド削除
2. 新機能（イメージスコア活用等）の検討

---

## 🎯 **修正完了の確認項目**

### **必須チェック**
- [ ] TypeScriptコンパイルエラーなし
- [ ] 診断フォーム送信成功
- [ ] タレント名正常表示
- [ ] 新しいフィールド（イメージスコア等）の正常取得
- [ ] 主キー（account_id）での正常な表示制御

### **拡張チェック**
- [ ] ターゲット層関連の正規化対応
- [ ] 新機能（7つのイメージスコア活用）の検討
- [ ] パフォーマンステスト

---

## ⚠️ **重要な注意事項**

1. **この修正は大規模な構造変更です**
   - 単純な文字列置換では不十分
   - 各interface、APIレスポンス、表示ロジック全てを見直す必要があります

2. **バックエンドとの密接な連携が必須**
   - フロントエンドの修正前に、バックエンドAPIの構造確定が必要
   - APIレスポンス仕様書の更新が先行条件

3. **段階的な実装を推奨**
   - 一度に全て変更せず、型定義→API→UIの順で段階実装
   - 各段階で動作確認を実施

4. **新機能の検討機会**
   - 7つのイメージスコアの UI表示
   - ターゲット層正規化を活用した新機能
   - パフォーマンス最適化

---

**📍 このドキュメント保存場所**: `/Users/lennon/projects/talent-casting-form/docs/COMPLETE_DATABASE_RECONSTRUCTION_IMPACT.md`