/**
 * タレントキャスティングシステム 型定義
 * requirements.mdのFormData型とTalentResult型を実装
 */

// フォームデータ型（7段階入力フォーム）
export interface FormData {
  termsAgreed?: boolean; // 利用規約同意（必須）
  q2: string; // 業種選択（必須）
  q3: string; // ターゲット層選択（必須、単一選択）
  q3_2: string; // タレント起用理由（必須）
  q3_3: string; // 予算区分（必須）
  q4: string; // 会社名（必須）
  q5: string; // 担当者名（必須）
  q6: string; // メールアドレス（必須）
  q7: string; // 携帯電話番号（必須）
  q7_2: string; // 希望ジャンル選択（オプション）
  q7_2_genres: string[]; // 具体的ジャンル選択（オプション、複数選択可）
  privacyAgreed: boolean; // プライバシー同意（必須）
}

// タレント結果型（5段階マッチングロジック結果）
export interface TalentResult {
  account_id: number; // アカウントID（新DB主キー）
  name: string; // タレント名
  kana?: string; // タレント名（カナ）
  category?: string; // カテゴリ（act_genre）
  company_name?: string; // 事務所名（m_account.company_name）
  matching_score: number; // マッチングスコア（86.0-99.7）
  ranking: number; // 順位（1-30）
  imageUrl?: string; // 画像URL
  base_power_score?: number; // 基礎パワー得点（STEP1）
  image_adjustment?: number; // 業種イメージ査定点（STEP2）
  is_recommended: boolean; // おすすめタレントかどうか
  is_currently_in_cm: boolean; // 現在CM出演中かどうか
}

// API レスポンス型（バックエンドの実際のレスポンス構造に合わせて修正）
export interface MatchingApiResponse {
  success: boolean;
  total_results: number;
  results: TalentResult[];
  processing_time_ms: number;
  timestamp: string;
  session_id?: string;
}

// 業種マスタ
export interface Industry {
  id: number;
  name: string;
  display_order: number;
}

// ターゲット層マスタ
export interface TargetSegment {
  id: number;
  code: string; // F1, F2, M1, M2, M3, F3, Teen, Senior
  name: string;
  gender: string;
  age_range: string;
  display_order: number;
}

// 予算区分マスタ
export interface BudgetRange {
  id: number;
  name: string;
  min_amount: number;
  max_amount: number;
  display_order: number;
}

// APIエンドポイント定数
export const API_ENDPOINTS = {
  MATCHING: '/api/matching',
  HEALTH: '/api/health',
  INDUSTRIES: '/api/industries',
  TARGET_SEGMENTS: '/api/target-segments',
  TRACK_BUTTON_CLICK: '/api/track-button-click',
} as const;

// フォーム検証エラー型
export interface FormValidationErrors {
  [key: string]: string;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// ランディングページ関連の型定義
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// LPメタ情報型（SEO・OGP対応）
export interface LandingPageMeta {
  title: string;
  description: string;
  keywords?: string[];
  ogTitle?: string;
  ogDescription?: string;
  ogImage?: string;
  ogUrl?: string;
  canonicalUrl?: string;
}

// LP設定型（環境変数から取得される設定値）
export interface LandingPageConfig {
  // 診断システムへのリダイレクトURL
  diagnosticsAppUrl: string; // app.yourdomain.com

  // LP情報
  version: 'temporary' | 'production'; // 暫定版 or 本格版
  deployedAt?: string; // デプロイ日時

  // フィーチャーフラグ（将来的な機能ON/OFF制御）
  features?: {
    showTestimonialsSection?: boolean;
    showFaqSection?: boolean;
    showNewsSection?: boolean;
  };

  // アナリティクス設定
  analytics?: {
    googleAnalyticsId?: string;
    segmentWriteKey?: string;
    hotjarId?: string;
  };
}

// LPコンテンツ型（将来的なCMS管理を考慮）
export interface LandingPageContent {
  hero: {
    title: string;
    subtitle: string;
    ctaText: string;
    ctaUrl: string;
  };

  features: Array<{
    id: string;
    icon?: string;
    title: string;
    description: string;
  }>;

  footer: {
    copyright: string;
    links?: Array<{
      text: string;
      url: string;
    }>;
  };
}

// LP統計情報型（アクセス解析用）
export interface LandingPageAnalytics {
  pageViews: number;
  uniqueVisitors: number;
  ctaClicks: number;
  conversionRate: number;
  bounceRate: number;
  avgTimeOnPage: number; // 秒単位
}

// LP A/Bテスト型（将来的な最適化用）
export interface LandingPageVariant {
  id: string;
  name: string;
  isControl: boolean;
  traffic: number; // 0-100 (%)
  config: Partial<LandingPageContent>;
  metrics?: LandingPageAnalytics;
}

// LP環境設定型
export interface LandingPageEnvironment {
  isDevelopment: boolean;
  isStaging: boolean;
  isProduction: boolean;
  baseUrl: string; // yourdomain.com
  appUrl: string; // app.yourdomain.com
  apiUrl: string; // API エンドポイント
}

// LP定数（設定値）
export const LANDING_PAGE_CONFIG = {
  // デフォルトリダイレクト先
  DEFAULT_DIAGNOSTICS_URL: 'https://app.yourdomain.com',

  // LP版管理
  VERSIONS: {
    TEMPORARY: 'temporary',
    PRODUCTION: 'production',
  },

  // レスポンシブブレークポイント
  BREAKPOINTS: {
    MOBILE: 768,
    TABLET: 1024,
    DESKTOP: 1280,
  },

  // アニメーション設定
  ANIMATIONS: {
    FADE_DURATION: 300,
    SLIDE_DURATION: 500,
    HOVER_SCALE: 1.05,
  },

  // カラーパレット（デザインシステム統一用）
  COLORS: {
    PRIMARY: '#667eea',
    SECONDARY: '#764ba2',
    GRADIENT: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    TEXT: '#333333',
    TEXT_LIGHT: '#666666',
    BACKGROUND: '#ffffff',
  },
} as const;

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 診断システム関連の型定義（mockups-v0からの移行）
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// タレントCM履歴型
export interface CMHistory {
  brand: string;
  industry: string;
  industryCode: string;
  year: string;
}

// 詳細データ型
export interface DetailData {
  strongPoints: string[];
  weakPoints: string[];
  recommendedUsage: string[];
  targetAudience: string[];
  marketingStrategy: string[];
}

// タレント型（mockups-v0のTalent型を拡張）
export interface Talent {
  id: number;
  name: string;
  maskedName: string;
  kana: string;
  category: string;
  categoryColor: string;
  title: string;
  awarenessScore: number;
  matchScore: number;
  introduction?: string;
  highlights: string[];
  instagram: string | null;
  youtube: string | null;
  twitter: string | null;
  tiktok: string | null;
  industries: string[];
  feeRange: string;
  imageUrl: string;
  age?: number;
  industryFit: {
    beauty_cosmetics: number;
    food_beverage: number;
    automotive: number;
    finance_insurance: number;
    it_technology: number;
    real_estate: number;
    retail_ec: number;
    fashion_apparel: number;
    game_entertainment: number;
    sports_fitness: number;
    travel_hotel: number;
    education: number;
    medical_healthcare: number;
    telecom: number;
    btob_services: number;
    other: number;
  };
  cmHistory: CMHistory[];
  currentUsageIndustries: string[];
  detailData?: DetailData;
}

// ストレージキー定数
export const STORAGE_KEY = 'talent-casting-form-data' as const;

// フォームステップ定数
export const TOTAL_FORM_STEPS = 7 as const;

// 業種コード定数
export const INDUSTRY_CODES = {
  BEAUTY_COSMETICS: 'beauty_cosmetics',
  FOOD_BEVERAGE: 'food_beverage',
  AUTOMOTIVE: 'automotive',
  FINANCE_INSURANCE: 'finance_insurance',
  IT_TECHNOLOGY: 'it_technology',
  REAL_ESTATE: 'real_estate',
  RETAIL_EC: 'retail_ec',
  FASHION_APPAREL: 'fashion_apparel',
  GAME_ENTERTAINMENT: 'game_entertainment',
  SPORTS_FITNESS: 'sports_fitness',
  TRAVEL_HOTEL: 'travel_hotel',
  EDUCATION: 'education',
  MEDICAL_HEALTHCARE: 'medical_healthcare',
  TELECOM: 'telecom',
  BTOB_SERVICES: 'btob_services',
  OTHER: 'other',
} as const;

export type IndustryCode = (typeof INDUSTRY_CODES)[keyof typeof INDUSTRY_CODES];

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// タレント詳細モーダル関連の型定義
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// CM履歴詳細型
export interface CMHistoryDetail {
  client_name: string;        // クライアント名
  product_name: string;       // 商品名
  use_period_start: string;   // 使用開始日
  use_period_end: string;     // 使用終了日
  agency_name?: string;       // 代理店名
  production_name?: string;   // 制作会社名
  director?: string;          // 監督名
  category?: string;          // カテゴリ
  note?: string;             // 備考
  rival_category_type_cd1?: number; // 競合カテゴリコード1
  rival_category_type_cd2?: number; // 競合カテゴリコード2
  rival_category_type_cd3?: number; // 競合カテゴリコード3
  rival_category_type_cd4?: number; // 競合カテゴリコード4
}

// タレント詳細情報型
export interface TalentDetailInfo {
  // 基本情報（TalentResultから継承）
  account_id: number;
  name: string;
  kana?: string;
  category?: string;
  age?: number;
  company_name?: string;
  birthplace?: string;  // 出身地（都道府県名）
  introduction?: string;
  matching_score: number;
  ranking: number;

  // 詳細情報
  cm_history: CMHistoryDetail[];

  // マッチングスコア詳細（APIから取得）
  base_power_score?: number;    // 基礎パワー得点
  image_adjustment?: number;    // 業種イメージ査定調整値
  imageUrl?: string;           // タレント画像URL
}

// タレント詳細モーダルのプロパティ型
export interface TalentDetailModalProps {
  talent: TalentResult;
  isOpen: boolean;
  onClose: () => void;
  formData: FormData;
  bookingUrl: string;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// ボタンクリック追跡関連の型定義
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// ボタンクリックデータ型
export interface ButtonClickData {
  session_id: string;
  button_type: string;
  button_text?: string;
}

// ボタンクリックレスポンス型
export interface ButtonClickResponse {
  success: boolean;
  message: string;
}