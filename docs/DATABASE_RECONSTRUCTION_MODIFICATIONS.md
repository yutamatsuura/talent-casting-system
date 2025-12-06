# データベース再構築後の必要修正箇所リスト

## 📌 概要
データベース再構築に伴い、`talents.name`カラムが`talents.name_full_for_matching`に変更されることを受けて、フロントエンド側で修正が必要な全箇所をリストアップしたドキュメントです。

**作成日**: 2025-12-03
**作成者**: Claude Code
**対象**: フロントエンドコードベース全体の`name`フィールド参照箇所

## 🔍 修正が必要な箇所（完全版）

### 1. 型定義ファイル（最重要）
**ファイル**: `src/types/index.ts`

| 行番号 | 修正箇所 | 内容 |
|--------|----------|------|
| 24 | `TalentResult` interface | `name: string; // タレント名` |
| 43 | `Industry` interface | `name: string;` |
| 51 | `TargetSegment` interface | `name: string;` |
| 60 | `BudgetRange` interface | `name: string;` |
| 234 | `Talent` interface | `name: string;` |
| 325 | `TalentDetailInfo` interface | `name: string;` |

**修正後の想定**:
```typescript
// TalentResult interface（行24）
name_full_for_matching: string; // タレント名（マッチング用完全名）

// 他のinterfaceも同様に更新
```

### 2. API通信層（データマッピング）
**ファイル**: `src/lib/api.ts`

| 行番号 | 修正箇所 | 内容 |
|--------|----------|------|
| 31 | `MatchingApiResponse` interface | `name: string;` |
| 119 | APIレスポンス変換ロジック | `name: item.name,` |

**修正後の想定**:
```typescript
// MatchingApiResponse interface（行31）
name_full_for_matching: string;

// APIレスポンス変換（行119）
name_full_for_matching: item.name_full_for_matching,
```

### 3. UIコンポーネント（表示層）
**ファイル**: `src/components/diagnosis/Results/ResultsPage.tsx`

| 行番号 | 修正箇所 | 内容 |
|--------|----------|------|
| 277 | タレント名表示 | `{talent.name}` |

**修正後の想定**:
```typescript
{talent.name_full_for_matching}
```

**ファイル**: `src/components/diagnosis/Results/TalentDetailModal.tsx`

| 行番号 | 修正箇所 | 内容 |
|--------|----------|------|
| 48 | モックデータ作成 | `name: talent.name,` |
| 170 | モーダル内表示 | `{talent.name}` |

**修正後の想定**:
```typescript
// モックデータ作成（行48）
name_full_for_matching: talent.name_full_for_matching,

// モーダル内表示（行170）
{talent.name_full_for_matching}
```

### 4. レガシー型定義（要確認）
**ファイル**: `src/lib/talent-data.ts`

| 行番号 | 修正箇所 | 内容 |
|--------|----------|------|
| 10 | `Talent` type定義 | `name: string` |

**修正後の想定**:
```typescript
name_full_for_matching: string
```

### 5. データベース仕様書（参照用）
**ファイル**: `ワーカー説明資料_口頭用.md`

| 行番号 | 記載内容 | 備考 |
|--------|----------|------|
| 196 | `name_full : タレント名（VR/TPRデータとの照合に使用）` | 仕様確認用 |
| 257 | `VR/TPRのタレント名 と talents.name_full を文字列照合` | ロジック参照用 |

## 🚨 重要な注意事項

### 修正不要なファイル
- **`src/lib/company-data.ts`**: このファイルの`name`フィールドは企業名であり、タレント名ではないため修正不要

### 修正順序（推奨）
1. **データベース再構築完了**（別エージェントが実施中）
2. **バックエンドAPI修正**（FastAPIのレスポンス構造更新）
3. **フロントエンド修正**（本ドキュメントの箇所を順次修正）

### バックエンド側の対応も必須
フロントエンド修正と並行して、FastAPIのレスポンス構造も`name`→`name_full_for_matching`に更新が必要です。

## ✅ 修正完了の確認手順

データベースカラム名変更後、以下の手順で動作確認を実施：

1. **診断フォーム送信テスト**
   - フォーム入力〜送信が正常に完了するか確認

2. **API通信確認**
   - ブラウザのNetworkタブでAPIレスポンスを確認
   - `name_full_for_matching`フィールドが正しく返されるか確認

3. **結果ページ表示確認**
   - タレント一覧でタレント名が正常表示されるか確認

4. **詳細モーダル表示確認**
   - 各タレントの詳細モーダルでタレント名が正常表示されるか確認

## 📋 チェックリスト

修正完了時に以下をチェック：

- [ ] `src/types/index.ts` - 全interface修正完了
- [ ] `src/lib/api.ts` - API通信層修正完了
- [ ] `src/components/diagnosis/Results/ResultsPage.tsx` - 表示修正完了
- [ ] `src/components/diagnosis/Results/TalentDetailModal.tsx` - モーダル修正完了
- [ ] `src/lib/talent-data.ts` - レガシー型定義修正完了
- [ ] フロントエンド全体のTypeScriptコンパイルエラーなし
- [ ] 実機テストでタレント名正常表示確認済み

---

**📍 このドキュメント作成場所**: `/Users/lennon/projects/talent-casting-form/docs/DATABASE_RECONSTRUCTION_MODIFICATIONS.md`