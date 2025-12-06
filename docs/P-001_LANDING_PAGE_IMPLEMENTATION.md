# P-001: ランディングページ実装方針確定

## 実装判定結果

### 🎯 **最終決定: HTML/CSS静的サイトのまま使用**

### 判定理由

#### 1. React実装は不要（HTMLのままで十分）

**根拠:**
- CLAUDE.mdの明確な要件: `lp: HTML/CSS + Vercel`
- プロジェクト原則: "必要最小限の実装のみ"
- LPの役割: 診断システムへの誘導のみ（インタラクティブ機能不要）
- モックアップの完成度: `mockups/LandingPage.html`は既に完成済み

**React化しない理由:**
```yaml
React化のメリット:
  - コンポーネント再利用: ✗ LP単ページのみ、再利用先なし
  - 動的UI制御: ✗ 静的コンテンツのみ
  - 型安全性: ✗ TypeScript型定義は診断システム専用

React化のデメリット:
  - 過剰エンジニアリング（CLAUDE.md違反）
  - ビルド時間増加
  - 不要な依存関係
  - Next.jsプロジェクトとの重複構成
```

#### 2. Vercelデプロイ準備が必要

**理由:**
```yaml
サブドメイン分離要件:
  - メインLP: yourdomain.com (Vercel静的ホスティング)
  - 診断システム: app.yourdomain.com (Vercel Next.js)

Vercel無料プラン運用:
  - LP用: 1プロジェクト（静的サイト）
  - 診断システム用: 1プロジェクト（Next.js）
  - 合計: 2プロジェクト並行稼働
```

#### 3. 静的サイトとNext.jsプロジェクトの共存方法

**戦略:**
```yaml
ディレクトリ構造:
  /talent-casting-form/
    ├── lp/                    # 静的LP専用
    │   ├── index.html         # LandingPage.html移行
    │   ├── styles.css         # （将来分離時用）
    │   └── vercel.json        # Vercel設定
    │
    ├── frontend/              # 診断システム（Next.js）
    │   ├── app/
    │   ├── src/
    │   └── package.json
    │
    └── docs/
        └── P-001_LANDING_PAGE_IMPLEMENTATION.md

Vercel統合:
  - LP: Git連携（lp/ディレクトリ監視）
  - 診断システム: Git連携（frontend/ディレクトリ監視）
  - 独立デプロイ: 各ディレクトリ変更時のみビルド
```

---

## 実装タスク

### ✅ Task 1: LP専用ディレクトリ作成
```bash
mkdir -p /Users/lennon/projects/talent-casting-form/lp
```

### ✅ Task 2: HTMLファイル移行
```bash
# mockups/LandingPage.html → lp/index.html に移動
cp /Users/lennon/projects/talent-casting-form/mockups/LandingPage.html \
   /Users/lennon/projects/talent-casting-form/lp/index.html
```

### ✅ Task 3: Vercel設定ファイル作成
`lp/vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### ✅ Task 4: 開発用サーバースクリプト作成
`lp/serve.sh`:
```bash
#!/bin/bash
# LP開発用ローカルサーバー（ポート3247）
python3 -m http.server 3247
```

### ✅ Task 5: .gitignore更新
```gitignore
# .gitignore に追加
lp/.DS_Store
```

### ✅ Task 6: README作成
`lp/README.md`:
```markdown
# タレントキャスティングシステム - ランディングページ

## 技術スタック
- HTML/CSS（静的サイト）
- Vercel静的ホスティング
- サブドメイン: yourdomain.com

## ローカル開発
```bash
cd lp
bash serve.sh  # http://localhost:3247
```

## デプロイ
Vercelプロジェクト設定:
- Project Name: talent-casting-lp
- Framework Preset: Other
- Root Directory: lp
- Build Command: (空白)
- Output Directory: .
```

---

## Vercelデプロイ手順

### Phase 1: Vercelプロジェクト作成

#### A. LP用プロジェクト（静的サイト）
```yaml
Project Settings:
  - Project Name: talent-casting-lp
  - Framework Preset: Other
  - Root Directory: lp
  - Build Command: (空白)
  - Output Directory: .
  - Install Command: (空白)

Environment Variables:
  - NODE_ENV: production

Domain Settings:
  - Production: yourdomain.com
  - Preview: talent-casting-lp.vercel.app
```

#### B. 診断システム用プロジェクト（Next.js）
```yaml
Project Settings:
  - Project Name: talent-casting-diagnosis
  - Framework Preset: Next.js
  - Root Directory: frontend
  - Build Command: npm run build
  - Output Directory: .next
  - Install Command: npm ci

Environment Variables:
  - NODE_ENV: production
  - NEXT_PUBLIC_API_URL: https://api.yourdomain.com
  - API_BASE_URL: https://api.yourdomain.com

Domain Settings:
  - Production: app.yourdomain.com
  - Preview: talent-casting-diagnosis.vercel.app
```

### Phase 2: Git連携設定

```yaml
LP用Vercelプロジェクト:
  - Ignored Build Step: $(git diff HEAD^ HEAD --quiet . ':(exclude)lp/')

診断システム用Vercelプロジェクト:
  - Ignored Build Step: $(git diff HEAD^ HEAD --quiet . ':(exclude)frontend/')
```

この設定により:
- `lp/`ディレクトリ変更時 → LP用プロジェクトのみビルド
- `frontend/`ディレクトリ変更時 → 診断システム用プロジェクトのみビルド

---

## 型定義の位置付け

### frontend/src/types/index.ts のLP関連型

**現状の型定義:**
```typescript
// ランディングページ関連の型定義（77-206行目）
export interface LandingPageMeta { ... }
export interface LandingPageConfig { ... }
export interface LandingPageContent { ... }
export interface LandingPageAnalytics { ... }
export interface LandingPageVariant { ... }
export interface LandingPageEnvironment { ... }
export const LANDING_PAGE_CONFIG = { ... }
```

**判定: これらの型定義は削除しない**

**理由:**
```yaml
1. 将来的な利用可能性:
   - Phase 11以降の本格LP制作時に活用
   - 制作チームがNext.js採用時の型定義として再利用

2. 削除しない原則:
   - 「あったらいいな」機能の追加は禁止
   - しかし「既に存在する機能の削除」も慎重に判断
   - 型定義はコンパイル結果に影響なし（Zero Cost Abstraction）

3. ドキュメント価値:
   - LP設計時の参考資料として機能
   - 将来のLP要件変更時の仕様書代替
```

**運用方針:**
- 現状のHTML/CSS静的サイトでは使用しない
- `frontend/src/types/index.ts`内にそのまま残す
- コメントで「将来用」を明記

---

## @MOCK_TO_APIマークシステムの適用

### 判定: **適用不要**

**理由:**
```yaml
@MOCK_TO_APIの目的:
  - API統合必要箇所の明示
  - フロント実装時のモックデータ暫定利用

LPの実装特性:
  - API呼び出しなし（静的HTML）
  - JavaScriptロジックなし
  - 外部データ取得なし
  - フォーム送信なし

結論:
  - マーク適用箇所が存在しない
  - 診断システム(frontend/)のみ@MOCK_TO_API適用対象
```

---

## ファイルパス一覧

### 作成・更新対象ファイル

```yaml
作成:
  - /Users/lennon/projects/talent-casting-form/lp/index.html
  - /Users/lennon/projects/talent-casting-form/lp/vercel.json
  - /Users/lennon/projects/talent-casting-form/lp/serve.sh
  - /Users/lennon/projects/talent-casting-form/lp/README.md
  - /Users/lennon/projects/talent-casting-form/docs/P-001_LANDING_PAGE_IMPLEMENTATION.md

更新:
  - /Users/lennon/projects/talent-casting-form/.gitignore

保持（変更なし）:
  - /Users/lennon/projects/talent-casting-form/mockups/LandingPage.html
  - /Users/lennon/projects/talent-casting-form/frontend/src/types/index.ts
```

---

## 動作確認手順

### ローカル開発環境
```bash
# 1. LP開発サーバー起動（ポート3247）
cd /Users/lennon/projects/talent-casting-form/lp
bash serve.sh

# ブラウザで確認:
# http://localhost:3247

# 2. 診断システム開発サーバー起動（ポート3248）
cd /Users/lennon/projects/talent-casting-form/frontend
npm run dev -- --port 3248

# ブラウザで確認:
# http://localhost:3248
```

### Vercelプレビュー環境
```yaml
LP:
  - URL: https://talent-casting-lp.vercel.app
  - 確認項目:
    - レスポンシブデザイン（モバイル・タブレット・デスクトップ）
    - CTAボタンリンク先（app.yourdomain.com）
    - セキュリティヘッダー（X-Frame-Options等）

診断システム:
  - URL: https://talent-casting-diagnosis.vercel.app
  - 確認項目:
    - Next.jsビルド成功
    - 環境変数読み込み
    - API接続（将来実装時）
```

---

## 次のステップ

### Phase 4: ページ実装（P-001完了後）
```yaml
1. LP実装完了（本タスク）:
   ✅ lp/index.html 作成
   ✅ Vercel設定完了
   ✅ ローカル開発環境構築

2. 次のタスク（診断システム実装）:
   - P-002: フォーム画面実装
   - P-003: 結果画面実装
   - P-004: API統合（@MOCK_TO_API適用）
```

---

## リスク管理

### 潜在的問題と対策

#### 1. LP差し替え時の影響範囲
**問題:**
- Phase 11以降に本格LP制作時、既存LPの完全差し替え

**対策:**
```yaml
設計原則:
  - 診断システム(frontend/)とLPは完全独立
  - 唯一の結合点: CTAボタンリンク（app.yourdomain.com）
  - LP差し替え時も診断システムは無影響

差し替え手順:
  1. lp/index.htmlを新LPで上書き
  2. CTAボタンリンク先確認（app.yourdomain.com）
  3. Vercelデプロイ
  4. 診断システム側の変更: 不要
```

#### 2. Vercel無料プラン制限
**問題:**
- 100GB/月転送量制限
- 6,000分/月ビルド時間制限

**対策:**
```yaml
LP（静的サイト）:
  - ビルド時間: 0分（静的配信のみ）
  - 転送量最適化: 画像圧縮、CSS最小化

診断システム（Next.js）:
  - ビルド時間: 約3-5分/回
  - 月間ビルド上限: 約1,200回（十分）
  - 転送量最適化: ISR、CDNキャッシュ活用
```

#### 3. サブドメイン設定エラー
**問題:**
- DNS設定ミスによるサブドメイン不通

**対策:**
```yaml
DNS設定手順:
  1. Vercel Dashboard → Domains → Add Domain
  2. yourdomain.com: talent-casting-lp プロジェクトに紐付け
  3. app.yourdomain.com: talent-casting-diagnosis プロジェクトに紐付け
  4. DNS伝播確認（最大48時間）

検証コマンド:
  $ nslookup yourdomain.com
  $ nslookup app.yourdomain.com
```

---

## 完了条件

### ✅ Phase 3完了の定義
```yaml
必須条件:
  ✅ lp/index.html が mockups/LandingPage.html から正常移行
  ✅ lp/vercel.json が正しく設定
  ✅ lp/serve.sh でローカル開発可能（ポート3247）
  ✅ lp/README.md が作成済み
  ✅ .gitignore に lp/.DS_Store 追加
  ✅ docs/P-001_LANDING_PAGE_IMPLEMENTATION.md 作成

Vercelデプロイ条件（Phase 3完了後に実施）:
  - talent-casting-lp プロジェクト作成
  - talent-casting-diagnosis プロジェクト作成
  - サブドメイン設定（yourdomain.com, app.yourdomain.com）
  - 各プロジェクトのプレビュー環境確認
```

---

## 参考資料

### 関連ドキュメント
```yaml
プロジェクト設定:
  - /Users/lennon/projects/talent-casting-form/CLAUDE.md

型定義:
  - /Users/lennon/projects/talent-casting-form/frontend/src/types/index.ts

モックアップ:
  - /Users/lennon/projects/talent-casting-form/mockups/LandingPage.html

進捗管理:
  - /Users/lennon/projects/talent-casting-form/docs/SCOPE_PROGRESS.md
```

### 外部リソース
```yaml
Vercel静的サイトデプロイ:
  - https://vercel.com/docs/concepts/deployments/build-step#html

Vercel複数プロジェクト管理:
  - https://vercel.com/docs/concepts/git/monorepos

サブドメイン設定:
  - https://vercel.com/docs/concepts/projects/domains/add-a-domain
```

---

## 変更履歴

| 日付 | バージョン | 変更内容 | 担当 |
|------|-----------|---------|------|
| 2025-11-28 | 1.0 | P-001初版作成、実装方針確定 | フロントエンドエージェント |
