export type CMHistory = {
  brand: string
  industry: string
  industryCode: string
  year: string
}

export type Talent = {
  id: number
  name: string
  maskedName: string
  kana: string
  category: string
  categoryColor: string
  title: string
  awarenessScore: number
  matchScore: number
  introduction?: string
  highlights: string[]
  instagram: string | null
  youtube: string | null
  twitter: string | null
  tiktok: string | null
  industries: string[]
  feeRange: string
  imageUrl: string
  age?: number
  industryFit: {
    beauty_cosmetics: number
    food_beverage: number
    automotive: number
    finance_insurance: number
    it_technology: number
    real_estate: number
    retail_ec: number
    fashion_apparel: number
    game_entertainment: number
    sports_fitness: number
    travel_hotel: number
    education: number
    medical_healthcare: number
    telecom: number
    btob_services: number
    other: number
  }
  cmHistory: CMHistory[]
  currentUsageIndustries: string[]
  detailData?: DetailData
}

export type ScoreBreakdown = {
  targetFit: {
    score: number
    f1?: { favorability: number; recognition: number }
    f2?: { favorability: number; recognition: number }
  }
  industryExp: {
    score: number
    [key: string]: any
  }
  brandAffinity: {
    score: number
    imageMatch?: number
    targetEmpathy?: number
  }
  costEff: {
    score: number
  }
}

export type HighlightData = {
  title: string
  vrData?: Record<string, number>
  imageData?: Record<string, number>
  ageRecognition?: Record<string, number>
  reach?: string
}

export type CMHistoryCategory = {
  category: string
  count: number
  items: Array<{
    brand: string
    period: string
    results?: Record<string, number>
    masked?: boolean
  }>
}

export type CostInfo = {
  tvCm?: {
    range: string
    duration: string
    shootingDays: string
  }
  webCm?: {
    range: string
    duration: string
    shootingDays: string
  }
  event?: {
    range: string
    duration: string
  }
  sns?: {
    range: string
    duration: string
  }
  packages?: {
    planA?: {
      name: string
      contents: string[]
      regularPrice: string
      packagePrice: string
      discount: string
    }
    planB?: {
      name: string
      contents: string[]
      regularPrice: string
      packagePrice: string
      discount: string
    }
    planC?: {
      name: string
      contents: string[]
      regularPrice: string
      packagePrice: string
      discount: string
    }
  }
  assetReuse?: {
    modelA?: {
      name: string
      description: string
      regularCost: string
      reuseCost: string
      savings: string
    }
    modelB?: {
      name: string
      description: string
      regularCost: string
      reuseCost: string
      savings: string
    }
    modelC?: {
      name: string
      description: string
      regularCost: string
      reuseCost: string
      savings: string
    }
  }
  designSets?: {
    setA?: {
      name: string
      contents: string[]
      regularPrice: string
      setPrice: string
      discount: string
    }
    setB?: {
      name: string
      contents: string[]
      regularPrice: string
      setPrice: string
      discount: string
    }
    setC?: {
      name: string
      contents: string[]
      regularPrice: string
      setPrice: string
      discount: string
    }
  }
}

export type DetailData = {
  scoreBreakdown: ScoreBreakdown
  highlights: HighlightData[]
  cmHistory: CMHistoryCategory[]
  cost: CostInfo
}

export const industryCodeMap: Record<string, string> = {
  "美容・化粧品": "IND-004",
  "食品・飲料": "IND-002",
  "自動車・モビリティ": "IND-003",
  "金融・保険": "IND-005",
  "IT・テクノロジー": "IND-006",
  "不動産・住宅": "IND-011",
  "小売・EC": "IND-012",
  "ファッション・アパレル": "IND-008",
  "ゲーム・エンタメ": "IND-013",
  "スポーツ・フィットネス": "IND-014",
  "旅行・ホテル": "IND-009",
  "教育・学習": "IND-015",
  "医療・ヘルスケア": "IND-007",
  "通信・キャリア": "IND-006",
  "BtoB・法人向けサービス": "IND-010",
  "その他": "IND-016",
}

export const premiumTalents: Talent[] = [
  {
    id: 1,
    name: "綾瀬はるか",
    maskedName: "◯◯ ◯◯",
    kana: "あやせ はるか",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "国民的女優",
    age: 38,
    awarenessScore: 98,
    matchScore: 98,
    introduction: "幅広い世代に支持される国民的女優。清潔感と信頼感が魅力。",
    highlights: ["F1層・F2層から圧倒的支持", "清潔感・信頼感のあるイメージ", "幅広い年齢層にリーチ可能"],
    instagram: "5.2M",
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["化粧品", "食品", "家電"],
    feeRange: "5000万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 100,
      food_beverage: 95,
      automotive: 75,
      finance_insurance: 85,
      it_technology: 70,
      real_estate: 90,
      retail_ec: 85,
      fashion_apparel: 95,
      game_entertainment: 75,
      sports_fitness: 70,
      travel_hotel: 90,
      education: 80,
      medical_healthcare: 85,
      telecom: 80,
      btob_services: 70,
      other: 80,
    },
    cmHistory: [
      {
        brand: "キリンビール『キリングッドエール』",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2023-2024",
      },
      {
        brand: "アリナミン製薬『ベンザブロックSプレミアムDX』",
        industry: "製薬・ヘルスケア",
        industryCode: "IND-007",
        year: "2024",
      },
      {
        brand: "プロクター・アンド・ギャンブル・ジャパン『ハピネスミスト』",
        industry: "化粧品・トイレタリー",
        industryCode: "IND-004",
        year: "2023",
      },
      {
        brand: "フジパン『本仕込』",
        industry: "食品",
        industryCode: "IND-002",
        year: "2022-2024",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-002", "IND-004", "IND-007"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 98,
          f1: { favorability: 94, recognition: 89 },
          f2: { favorability: 88, recognition: 92 },
        },
        industryExp: {
          score: 95,
        },
        brandAffinity: {
          score: 96,
        },
        costEff: {
          score: 95,
        },
      },
      highlights: [
        {
          title: "F1層・F2層からの圧倒的支持",
          vrData: {
            F1層好感度: 94,
            F2層好感度: 88,
            "20-30代支持率": 92,
            "30-40代支持率": 88,
          },
        },
        {
          title: "清潔感・信頼感のあるイメージ",
          imageData: {
            清潔感: 93,
            信頼感: 90,
            親しみやすさ: 87,
            上品さ: 85,
          },
        },
        {
          title: "幅広い年齢層へのリーチ力",
          reach: "約2,500万人",
        },
      ],
      cmHistory: [
        {
          category: "飲料・アルコール",
          count: 3,
          items: [
            {
              brand: "キリンビール『キリングッドエール』",
              period: "2023年4月〜2024年3月",
              results: {
                brandLift: 18,
                purchaseIntent: 12,
              },
            },
            {
              brand: "サントリー『金麦』",
              period: "2022年4月〜2023年3月",
              results: {
                brandLift: 22,
                marketShare: 3.5,
              },
            },
            {
              brand: "アサヒビール『クリアアサヒ』",
              period: "2023年（短期）",
              results: {
                brandLift: 15,
              },
            },
          ],
        },
        {
          category: "食品",
          count: 2,
          items: [
            {
              brand: "フジパン『本仕込』",
              period: "2022年〜2024年（継続中）",
              results: {
                purchaseIntent: 25,
                brandRecognition: 30,
              },
            },
            {
              brand: "江崎グリコ『BifiXヨーグルト』",
              period: "2023年",
              results: {
                purchaseIntent: 19,
                trialRate: 15,
              },
            },
          ],
        },
        {
          category: "化粧品・トイレタリー",
          count: 2,
          items: [
            {
              brand: "P&G『ハピネスミスト』",
              period: "2023年",
            },
            {
              brand: "資生堂『アクアレーベル』",
              period: "2022年",
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "8,000万円〜1億2,000万円",
          duration: "1年間",
          shootingDays: "8-12日",
        },
        webCm: {
          range: "500万円〜1,500万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "200万円〜300万円",
          duration: "2-3時間",
        },
        sns: {
          range: "50万円〜100万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 2,
    name: "新垣結衣",
    maskedName: "◯◯ ◯◯",
    kana: "あらがき ゆい",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "国民的女優",
    age: 35,
    awarenessScore: 97,
    matchScore: 96,
    introduction: "男女問わず人気の国民的女優。透明感あふれる美しさが魅力。",
    highlights: ["若年層から絶大な人気", "親しみやすく爽やかなイメージ", "SNS波及効果が高い"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["住宅", "保険", "化粧品"],
    feeRange: "6000万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 98,
      food_beverage: 90,
      automotive: 85,
      finance_insurance: 95,
      it_technology: 80,
      real_estate: 100,
      retail_ec: 85,
      fashion_apparel: 95,
      game_entertainment: 80,
      sports_fitness: 98,
      travel_hotel: 90,
      education: 85,
      medical_healthcare: 85,
      telecom: 85,
      btob_services: 80,
      other: 85,
    },
    cmHistory: [
      {
        brand: "資生堂『アネッサ』",
        industry: "化粧品・トイレタリー",
        industryCode: "IND-004",
        year: "2023-2024",
      },
      {
        brand: "ニベア花王『ニベアクリーム』",
        industry: "化粧品・トイレタリー",
        industryCode: "IND-004",
        year: "2022-2024",
      },
      {
        brand: "GMOペイメントゲートウェイ『GMOあおぞらネット銀行』",
        industry: "金融・保険",
        industryCode: "IND-005",
        year: "2023",
      },
    ],
    currentUsageIndustries: ["IND-004", "IND-005"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 96,
          f1: { favorability: 96, recognition: 91 },
          f2: { favorability: 89, recognition: 88 },
        },
        industryExp: {
          score: 78,
        },
        brandAffinity: {
          score: 95,
        },
        costEff: {
          score: 88,
        },
      },
      highlights: [
        {
          title: "若年層から絶大な人気",
          vrData: {
            "20代支持率": 95,
            "30代支持率": 89,
          },
        },
        {
          title: "親しみやすく爽やかなイメージ",
          imageData: {
            好感度: 96,
            爽やかさ: 94,
            親しみやすさ: 92,
          },
        },
        {
          title: "SNS波及効果が高い",
          reach: "約1,800万人",
        },
      ],
      cmHistory: [
        {
          category: "化粧品・トイレタリー",
          count: 2,
          items: [
            {
              brand: "資生堂『アネッサ』",
              period: "2023年〜2024年",
              results: {
                brandLift: 20,
                purchaseIntent: 15,
              },
            },
            {
              brand: "ニベア花王『ニベアクリーム』",
              period: "2022年〜2024年",
              results: {
                brandLift: 18,
                trialRate: 12,
              },
            },
          ],
        },
        {
          category: "金融・保険",
          count: 1,
          items: [
            {
              brand: "GMOあおぞらネット銀行",
              period: "2023年",
              results: {
                brandRecognition: 35,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "1億円〜1億5,000万円",
          duration: "1年間",
          shootingDays: "10-15日",
        },
        webCm: {
          range: "800万円〜2,000万円",
          duration: "3-6ヶ月",
          shootingDays: "2-3日",
        },
        event: {
          range: "300万円〜500万円",
          duration: "2-4時間",
        },
        sns: {
          range: "80万円〜150万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 3,
    name: "有村架純",
    maskedName: "◯◯ ◯◯",
    kana: "ありむら かすみ",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "清純派女優",
    age: 31,
    awarenessScore: 95,
    matchScore: 90,
    introduction: "透明感あふれる演技で人気の女優。清純で誠実なイメージ。",
    highlights: ["清純で誠実なイメージ", "全年齢層から好感度が高い", "家族向け商品との相性良"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["化粧品", "飲料", "ファッション"],
    feeRange: "4000万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 98,
      food_beverage: 92,
      automotive: 75,
      finance_insurance: 80,
      it_technology: 70,
      real_estate: 85,
      retail_ec: 88,
      fashion_apparel: 95,
      game_entertainment: 80,
      sports_fitness: 75,
      travel_hotel: 90,
      education: 85,
      medical_healthcare: 85,
      telecom: 82,
      btob_services: 70,
      other: 80,
    },
    cmHistory: [
      {
        brand: "明治『ザ・チョコレート』",
        industry: "食品",
        industryCode: "IND-002",
        year: "2023",
      },
      {
        brand: "P&G『ジョイ』",
        industry: "化粧品・トイレタリー",
        industryCode: "IND-004",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-002", "IND-004"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 88,
          f1: { favorability: 88, recognition: 85 },
          f2: { favorability: 86, recognition: 87 },
        },
        industryExp: {
          score: 72,
        },
        brandAffinity: {
          score: 90,
        },
        costEff: {
          score: 92,
        },
      },
      highlights: [
        {
          title: "清純で誠実なイメージ",
          imageData: {
            清純さ: 93,
            誠実さ: 90,
            清潔感: 88,
          },
        },
        {
          title: "全年齢層から好感度が高い",
          vrData: {
            "10代": 82,
            "20代": 88,
            "30代": 90,
            "40代": 88,
            "50代以上": 85,
          },
        },
        {
          title: "家族向け商品との相性が良い",
          vrData: {
            家族支持率: 89,
            信頼度: 91,
          },
        },
      ],
      cmHistory: [
        {
          category: "食品",
          count: 1,
          items: [
            {
              brand: "明治『ザ・チョコレート』",
              period: "2023年",
              results: {
                brandLift: 16,
                purchaseIntent: 14,
              },
            },
          ],
        },
        {
          category: "化粧品・トイレタリー",
          count: 1,
          items: [
            {
              brand: "P&G『ジョイ』",
              period: "2024年",
              results: {
                brandLift: 12,
                trialRate: 10,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "6,000万円〜9,000万円",
          duration: "1年間",
          shootingDays: "6-10日",
        },
        webCm: {
          range: "400万円〜1,000万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "150万円〜250万円",
          duration: "2-3時間",
        },
        sns: {
          range: "40万円〜80万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 4,
    name: "今田美桜",
    maskedName: "◯◯ ◯◯",
    kana: "いまだ みお",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "若手人気女優",
    age: 27,
    awarenessScore: 93,
    matchScore: 89,
    introduction: "SNSで話題の若手女優。トレンド感のあるビジュアルが魅力。",
    highlights: ["若年層から急上昇中の人気", "トレンド感のあるビジュアル", "SNSエンゲージメント率が高い"],
    instagram: "2.8M",
    youtube: null,
    twitter: "980K",
    tiktok: null,
    industries: ["化粧品", "ファッション", "飲料"],
    feeRange: "3000万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 98,
      food_beverage: 88,
      automotive: 72,
      finance_insurance: 75,
      it_technology: 80,
      real_estate: 82,
      retail_ec: 88,
      fashion_apparel: 98,
      game_entertainment: 85,
      sports_fitness: 80,
      travel_hotel: 88,
      education: 78,
      medical_healthcare: 78,
      telecom: 85,
      btob_services: 68,
      other: 78,
    },
    cmHistory: [],
    currentUsageIndustries: [],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 91,
          f1: { favorability: 91, recognition: 87 },
          f2: { favorability: 78, recognition: 75 },
        },
        industryExp: {
          score: 45,
        },
        brandAffinity: {
          score: 85,
        },
        costEff: {
          score: 98,
        },
      },
      highlights: [
        {
          title: "若年層から急上昇中の人気",
          vrData: {
            "10代支持率": 88,
            "20代支持率": 91,
            トレンドスコア: 94,
          },
        },
        {
          title: "トレンド感のあるビジュアル",
          imageData: {
            ファッション性: 94,
            現代的魅力: 92,
          },
        },
        {
          title: "SNSエンゲージメント率が高い",
          reach: "Instagramフォロワー120万人",
        },
      ],
      cmHistory: [],
      cost: {
        tvCm: {
          range: "3,000万円〜5,000万円",
          duration: "1年間",
          shootingDays: "4-6日",
        },
        webCm: {
          range: "200万円〜500万円",
          duration: "3-6ヶ月",
          shootingDays: "1日",
        },
        event: {
          range: "80万円〜150万円",
          duration: "2時間",
        },
        sns: {
          range: "30万円〜60万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 5,
    name: "石原さとみ",
    maskedName: "◯◯ ◯◯",
    kana: "いしはら さとみ",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "国民的美女",
    age: 37,
    awarenessScore: 96,
    matchScore: 93,
    introduction: "美しさと知性を兼ね備えた女優。上品で洗練されたイメージ。",
    highlights: ["上品で洗練されたイメージ", "F1-F3層まで幅広く支持", "ラグジュアリーブランドとの親和性"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["化粧品", "ジュエリー", "ファッション"],
    feeRange: "6000万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 100,
      food_beverage: 90,
      automotive: 75,
      finance_insurance: 80,
      it_technology: 70,
      real_estate: 85,
      retail_ec: 90,
      fashion_apparel: 100,
      game_entertainment: 75,
      sports_fitness: 75,
      travel_hotel: 95,
      education: 75,
      medical_healthcare: 80,
      telecom: 80,
      btob_services: 70,
      other: 80,
    },
    cmHistory: [
      {
        brand: "アサヒビール『クリアアサヒ』",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2023",
      },
      {
        brand: "コーセー『雪肌精』",
        industry: "化粧品・トイレタリー",
        industryCode: "IND-004",
        year: "2022-2024",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-004"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 92,
          f1: { favorability: 90, recognition: 94 },
          f2: { favorability: 92, recognition: 95 },
        },
        industryExp: {
          score: 88,
        },
        brandAffinity: {
          score: 94,
        },
        costEff: {
          score: 85,
        },
      },
      highlights: [],
      cmHistory: [],
      cost: {
        tvCm: {
          range: "競合使用中",
          duration: "",
          shootingDays: "",
        },
        webCm: {
          range: "",
          duration: "",
          shootingDays: "",
        },
        event: {
          range: "",
          duration: "",
        },
        sns: {
          range: "",
          duration: "",
        },
      },
    },
  },
  {
    id: 6,
    name: "吉岡里帆",
    maskedName: "◯◯ ◯◯",
    kana: "よしおか りほ",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "親しみやすい女優",
    age: 31,
    awarenessScore: 94,
    matchScore: 91,
    introduction: "明るい笑顔が魅力の女優。親しみやすく柔らかいイメージ。",
    highlights: ["親しみやすく柔らかいイメージ", "20-30代女性からの好感度高", "地方でも認知度が高い"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["自動車", "保険", "飲料"],
    feeRange: "4000万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 90,
      food_beverage: 88,
      automotive: 95,
      finance_insurance: 90,
      it_technology: 75,
      real_estate: 88,
      retail_ec: 85,
      fashion_apparel: 88,
      game_entertainment: 78,
      sports_fitness: 80,
      travel_hotel: 88,
      education: 82,
      medical_healthcare: 85,
      telecom: 82,
      btob_services: 78,
      other: 82,
    },
    cmHistory: [
      {
        brand: "ダイハツ工業『ダイハツ ムーヴ』",
        industry: "自動車",
        industryCode: "IND-003",
        year: "2023-2024",
      },
    ],
    currentUsageIndustries: ["IND-003"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 89,
          f1: { favorability: 85, recognition: 88 },
          f2: { favorability: 80, recognition: 82 },
        },
        industryExp: {
          score: 85,
        },
        brandAffinity: {
          score: 87,
        },
        costEff: {
          score: 93,
        },
      },
      highlights: [
        {
          title: "親しみやすく柔らかいイメージ",
          imageData: {
            親しみやすさ: 93,
            柔らかさ: 90,
            清潔感: 88,
          },
        },
        {
          title: "20-30代女性からの好感度高",
          vrData: {
            "20-30代女性": 90,
          },
        },
        {
          title: "地方でも認知度が高い",
          reach: "全国的な認知度",
        },
      ],
      cmHistory: [
        {
          category: "自動車",
          count: 1,
          items: [
            {
              brand: "ダイハツ工業『ダイハツ ムーヴ』",
              period: "2023年〜2024年",
              results: {
                brandLift: 18,
                purchaseIntent: 15,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "7,000万円〜1億円",
          duration: "1年間",
          shootingDays: "7-11日",
        },
        webCm: {
          range: "500万円〜1,200万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "200万円〜300万円",
          duration: "2-3時間",
        },
        sns: {
          range: "50万円〜100万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 7,
    name: "指原莉乃",
    maskedName: "◯◯ ◯◯",
    kana: "さしはら りの",
    category: "タレント",
    categoryColor: "#FEF3C7",
    title: "バラエティタレント",
    age: 31,
    awarenessScore: 92,
    matchScore: 79,
    introduction: "バラエティ番組で活躍中のタレント。プロデュース力も魅力。",
    highlights: ["バラエティでの活躍", "プロデュース力も高評価", "10-30代女性から支持"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["アパレル", "化粧品", "食品"],
    feeRange: "3000万円〜",
    imageUrl: "/japanese-talent-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 85,
      food_beverage: 80,
      automotive: 65,
      finance_insurance: 70,
      it_technology: 75,
      real_estate: 70,
      retail_ec: 88,
      fashion_apparel: 90,
      game_entertainment: 85,
      sports_fitness: 75,
      travel_hotel: 80,
      education: 75,
      medical_healthcare: 70,
      telecom: 78,
      btob_services: 65,
      other: 75,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 8,
    name: "松本潤",
    maskedName: "◯◯ ◯",
    kana: "まつもと じゅん",
    category: "俳優",
    categoryColor: "#BFDBFE",
    title: "国民的アイドル俳優",
    age: 41,
    awarenessScore: 98,
    matchScore: 94,
    introduction: "嵐のメンバーとして絶大な人気を誇る国民的アイドル俳優。",
    highlights: ["全世代から圧倒的認知度", "高級感のあるイメージ", "CM起用実績豊富"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["自動車", "化粧品", "飲料"],
    feeRange: "8000万円〜",
    imageUrl: "/japanese-actor-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 85,
      food_beverage: 92,
      automotive: 98,
      finance_insurance: 90,
      it_technology: 85,
      real_estate: 90,
      retail_ec: 88,
      fashion_apparel: 92,
      game_entertainment: 85,
      sports_fitness: 85,
      travel_hotel: 92,
      education: 80,
      medical_healthcare: 82,
      telecom: 88,
      btob_services: 85,
      other: 85,
    },
    cmHistory: [
      {
        brand: "トヨタ自動車『カローラ』",
        industry: "自動車",
        industryCode: "IND-003",
        year: "2023-2024",
      },
      {
        brand: "KOSE『ONE BY KOSE』",
        industry: "化粧品・トイレタリー",
        industryCode: "IND-004",
        year: "2023",
      },
      {
        brand: "キリンビール『一番搾り』",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2023-2024",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-003", "IND-004"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 94,
          f1: { favorability: 96, recognition: 95 },
          f2: { favorability: 90, recognition: 92 },
        },
        industryExp: {
          score: 90,
        },
        brandAffinity: {
          score: 95,
        },
        costEff: {
          score: 88,
        },
      },
      highlights: [
        {
          title: "全世代から圧倒的認知度",
          vrData: {
            全世代認知度: 98,
            "30代支持率": 94,
            "40代支持率": 93,
          },
        },
        {
          title: "高級感のあるイメージ",
          imageData: {
            高級感: 95,
            信頼感: 92,
            男性人気: 90,
          },
        },
        {
          title: "CM起用実績豊富",
          reach: "年間CM出演本数10本以上",
        },
      ],
      cmHistory: [
        {
          category: "自動車",
          count: 1,
          items: [
            {
              brand: "トヨタ自動車『カローラ』",
              period: "2023年〜2024年",
              results: {
                brandLift: 25,
                purchaseIntent: 20,
              },
            },
          ],
        },
        {
          category: "化粧品・トイレタリー",
          count: 1,
          items: [
            {
              brand: "KOSE『ONE BY KOSE』",
              period: "2023年",
              results: {
                brandLift: 18,
                trialRate: 15,
              },
            },
          ],
        },
        {
          category: "飲料・アルコール",
          count: 1,
          items: [
            {
              brand: "キリンビール『一番搾り』",
              period: "2023年〜2024年",
              results: {
                brandLift: 22,
                marketShare: 4.0,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "1億円〜1億5,000万円",
          duration: "1年間",
          shootingDays: "10-14日",
        },
        webCm: {
          range: "700万円〜1,800万円",
          duration: "3-6ヶ月",
          shootingDays: "2-3日",
        },
        event: {
          range: "300万円〜500万円",
          duration: "2-4時間",
        },
        sns: {
          range: "80万円〜150万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 9,
    name: "二宮和也",
    maskedName: "◯◯ ◯◯",
    kana: "にのみや かずなり",
    category: "俳優",
    categoryColor: "#BFDBFE",
    title: "実力派俳優",
    age: 41,
    awarenessScore: 96,
    matchScore: 91,
    introduction: "演技力に定評のある実力派俳優。親しみやすいキャラクター。",
    highlights: ["幅広い年齢層から支持", "親しみやすいキャラクター", "演技力が高評価"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["金融", "食品", "家電"],
    feeRange: "6000万円〜",
    imageUrl: "/japanese-actor-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 75,
      food_beverage: 88,
      automotive: 85,
      finance_insurance: 95,
      it_technology: 82,
      real_estate: 88,
      retail_ec: 85,
      fashion_apparel: 80,
      game_entertainment: 85,
      sports_fitness: 78,
      travel_hotel: 85,
      education: 82,
      medical_healthcare: 82,
      telecom: 85,
      btob_services: 88,
      other: 82,
    },
    cmHistory: [
      {
        brand: "SMBC",
        industry: "金融・保険",
        industryCode: "IND-005",
        year: "2023-2024",
      },
      {
        brand: "日清食品『カップヌードル』",
        industry: "食品",
        industryCode: "IND-002",
        year: "2023",
      },
      {
        brand: "パナソニック",
        industry: "家電",
        industryCode: "IND-006",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-002", "IND-005", "IND-006"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 91,
          f1: { favorability: 90, recognition: 89 },
          f2: { favorability: 85, recognition: 82 },
        },
        industryExp: {
          score: 85,
        },
        brandAffinity: {
          score: 92,
        },
        costEff: {
          score: 90,
        },
      },
      highlights: [
        {
          title: "幅広い年齢層から支持",
          vrData: {
            "20代支持率": 88,
            "30代支持率": 90,
            "40代支持率": 92,
            "50代支持率": 85,
          },
        },
        {
          title: "親しみやすいキャラクター",
          imageData: {
            親しみやすさ: 93,
            ユーモア: 90,
            誠実さ: 88,
          },
        },
        {
          title: "演技力が高評価",
          reach: "数々の受賞歴",
        },
      ],
      cmHistory: [
        {
          category: "金融・保険",
          count: 1,
          items: [
            {
              brand: "SMBC",
              period: "2023年〜2024年",
              results: {
                brandLift: 20,
                brandRecognition: 42,
              },
            },
          ],
        },
        {
          category: "食品",
          count: 1,
          items: [
            {
              brand: "日清食品『カップヌードル』",
              period: "2023年",
              results: {
                brandLift: 18,
                purchaseIntent: 15,
              },
            },
          ],
        },
        {
          category: "IT・テクノロジー",
          count: 1,
          items: [
            {
              brand: "パナソニック",
              period: "2024年",
              results: {
                brandLift: 16,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "9,000万円〜1億2,000万円",
          duration: "1年間",
          shootingDays: "8-12日",
        },
        webCm: {
          range: "600万円〜1,500万円",
          duration: "3-6ヶ月",
          shootingDays: "2-3日",
        },
        event: {
          range: "250万円〜400万円",
          duration: "2-4時間",
        },
        sns: {
          range: "70万円〜120万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 10,
    name: "櫻井翔",
    maskedName: "◯◯ ◯",
    kana: "さくらい しょう",
    category: "俳優",
    categoryColor: "#BFDBFE",
    title: "キャスター・タレント",
    age: 42,
    awarenessScore: 97,
    matchScore: 92,
    introduction: "ニュースキャスターとしても活躍する知的なタレント。",
    highlights: ["知的で信頼感のあるイメージ", "幅広い層から支持", "ニュース番組での活躍"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["金融", "不動産", "教育"],
    feeRange: "7000万円〜",
    imageUrl: "/japanese-actor-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 75,
      food_beverage: 85,
      automotive: 88,
      finance_insurance: 98,
      it_technology: 85,
      real_estate: 95,
      retail_ec: 82,
      fashion_apparel: 82,
      game_entertainment: 80,
      sports_fitness: 80,
      travel_hotel: 88,
      education: 95,
      medical_healthcare: 85,
      telecom: 88,
      btob_services: 92,
      other: 85,
    },
    cmHistory: [
      {
        brand: "みずほ銀行",
        industry: "金融・保険",
        industryCode: "IND-005",
        year: "2023-2024",
      },
      {
        brand: "三井不動産",
        industry: "不動産・住宅",
        industryCode: "IND-011",
        year: "2024",
      },
      {
        brand: "ベネッセコーポレーション『進研ゼミ』",
        industry: "教育・学習",
        industryCode: "IND-015",
        year: "2023",
      },
    ],
    currentUsageIndustries: ["IND-005", "IND-011", "IND-015"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 92,
          f1: { favorability: 93, recognition: 91 },
          f2: { favorability: 88, recognition: 87 },
        },
        industryExp: {
          score: 90,
        },
        brandAffinity: {
          score: 94,
        },
        costEff: {
          score: 85,
        },
      },
      highlights: [
        {
          title: "知的で信頼感のあるイメージ",
          imageData: {
            知性: 97,
            信頼感: 96,
            真面目さ: 93,
          },
        },
        {
          title: "幅広い層から支持",
          vrData: {
            "30代支持率": 94,
            "40代支持率": 96,
            "50代以上支持率": 95,
          },
        },
        {
          title: "ニュース番組での活躍",
          reach: "News ZEROキャスター",
        },
      ],
      cmHistory: [
        {
          category: "金融・保険",
          count: 1,
          items: [
            {
              brand: "みずほ銀行",
              period: "2023年〜2024年",
              results: {
                brandLift: 20,
                brandRecognition: 45,
              },
            },
          ],
        },
        {
          category: "不動産・住宅",
          count: 1,
          items: [
            {
              brand: "三井不動産",
              period: "2024年",
              results: {
                brandLift: 15,
              },
            },
          ],
        },
        {
          category: "教育・学習",
          count: 1,
          items: [
            {
              brand: "ベネッセコーポレーション『進研ゼミ』",
              period: "2023年",
              results: {
                brandLift: 18,
                purchaseIntent: 14,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "1億〜1億5,000万円",
          duration: "1年間",
          shootingDays: "10-14日",
        },
        webCm: {
          range: "700万円〜1,800万円",
          duration: "3-6ヶ月",
          shootingDays: "2-3日",
        },
        event: {
          range: "300万円〜500万円",
          duration: "2-4時間",
        },
        sns: {
          range: "80万円〜150万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 11,
    name: "相葉雅紀",
    maskedName: "◯◯ ◯◯",
    kana: "あいば まさき",
    category: "俳優",
    categoryColor: "#BFDBFE",
    title: "バラエティタレント",
    age: 41,
    awarenessScore: 95,
    matchScore: 89,
    introduction: "明るく親しみやすいキャラクターで人気のタレント。",
    highlights: ["明るく親しみやすい", "家族層から高い支持", "動物・自然番組で活躍"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["食品", "飲料", "ペット"],
    feeRange: "5000万円〜",
    imageUrl: "/japanese-actor-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 70,
      food_beverage: 95,
      automotive: 82,
      finance_insurance: 80,
      it_technology: 75,
      real_estate: 82,
      retail_ec: 85,
      fashion_apparel: 78,
      game_entertainment: 85,
      sports_fitness: 82,
      travel_hotel: 88,
      education: 85,
      medical_healthcare: 80,
      telecom: 80,
      btob_services: 75,
      other: 82,
    },
    cmHistory: [
      {
        brand: "キリンビール『淡麗グリーンラベル』",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2023-2024",
      },
      {
        brand: "アサヒ飲料『三ツ矢サイダー』",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2024",
      },
      {
        brand: "ユニ・チャーム『デオトイレ』",
        industry: "その他",
        industryCode: "IND-016",
        year: "2023",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-016"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 89,
          f1: { favorability: 88, recognition: 87 },
          f2: { favorability: 82, recognition: 80 },
        },
        industryExp: {
          score: 85,
        },
        brandAffinity: {
          score: 89,
        },
        costEff: {
          score: 93,
        },
      },
      highlights: [
        {
          title: "明るく親しみやすい",
          imageData: {
            親しみやすさ: 94,
            明るさ: 93,
            爽やかさ: 90,
          },
        },
        {
          title: "家族層から高い支持",
          vrData: {
            家族支持率: 91,
            "30-50代支持率": 88,
          },
        },
        {
          title: "動物・自然番組で活躍",
          reach: "「動物のお医者さん」など",
        },
      ],
      cmHistory: [
        {
          category: "飲料・アルコール",
          count: 2,
          items: [
            {
              brand: "キリンビール『淡麗グリーンラベル』",
              period: "2023年〜2024年",
              results: {
                brandLift: 18,
                purchaseIntent: 15,
              },
            },
            {
              brand: "アサヒ飲料『三ツ矢サイダー』",
              period: "2024年",
              results: {
                brandLift: 16,
                trialRate: 12,
              },
            },
          ],
        },
        {
          category: "その他",
          count: 1,
          items: [
            {
              brand: "ユニ・チャーム『デオトイレ』",
              period: "2023年",
              results: {
                brandLift: 15,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "8,000万円〜1億1,000万円",
          duration: "1年間",
          shootingDays: "7-11日",
        },
        webCm: {
          range: "500万円〜1,300万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "250万円〜400万円",
          duration: "2-3時間",
        },
        sns: {
          range: "60万円〜110万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 12,
    name: "大野智",
    maskedName: "◯◯ ◯",
    kana: "おおの さとし",
    category: "俳優",
    categoryColor: "#BFDBFE",
    title: "アーティスト俳優",
    age: 44,
    awarenessScore: 94,
    matchScore: 88,
    introduction: "芸術的センスと演技力を兼ね備えたアーティスト俳優。",
    highlights: ["芸術的センス", "独特の世界観", "30-40代から支持"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["ゲーム", "アート", "飲料"],
    feeRange: "5500万円〜",
    imageUrl: "/japanese-actor-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 72,
      food_beverage: 85,
      automotive: 78,
      finance_insurance: 75,
      it_technology: 80,
      real_estate: 78,
      retail_ec: 80,
      fashion_apparel: 85,
      game_entertainment: 95,
      sports_fitness: 75,
      travel_hotel: 82,
      education: 78,
      medical_healthcare: 75,
      telecom: 78,
      btob_services: 72,
      other: 80,
    },
    cmHistory: [
      {
        brand: "スクウェア・エニックス『ドラゴンクエストウォーク』",
        industry: "ゲーム・エンタメ",
        industryCode: "IND-013",
        year: "2023",
      },
      {
        brand: "サントリー『ボス』",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2023",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-013"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 88,
          f1: { favorability: 85, recognition: 86 },
          f2: { favorability: 80, recognition: 78 },
        },
        industryExp: {
          score: 80,
        },
        brandAffinity: {
          score: 88,
        },
        costEff: {
          score: 85,
        },
      },
      highlights: [
        {
          title: "芸術的センス",
          imageData: {
            創造性: 95,
            独自性: 92,
          },
        },
        {
          title: "独特の世界観",
          vrData: {
            アートファン支持率: 90,
          },
        },
        {
          title: "30-40代から支持",
          vrData: {
            "30代支持率": 85,
            "40代支持率": 88,
          },
        },
      ],
      cmHistory: [
        {
          category: "ゲーム・エンタメ",
          count: 1,
          items: [
            {
              brand: "スクウェア・エニックス『ドラゴンクエストウォーク』",
              period: "2023年",
              results: {
                brandLift: 20,
                trialRate: 18,
              },
            },
          ],
        },
        {
          category: "飲料・アルコール",
          count: 1,
          items: [
            {
              brand: "サントリー『ボス』",
              period: "2023年",
              results: {
                brandLift: 17,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "8,000万円〜1億円",
          duration: "1年間",
          shootingDays: "7-10日",
        },
        webCm: {
          range: "500万円〜1,200万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "200万円〜300万円",
          duration: "2-3時間",
        },
        sns: {
          range: "50万円〜100万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 13,
    name: "橋本環奈",
    maskedName: "◯◯ ◯◯",
    kana: "はしもと かんな",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "若手人気女優",
    age: 25,
    awarenessScore: 96,
    matchScore: 94,
    introduction: "1000年に一人の美少女として注目を集める若手女優。",
    highlights: ["若年層から絶大な支持", "清純で可愛らしいイメージ", "SNS拡散力が高い"],
    instagram: "2.8M",
    youtube: null,
    twitter: "980K",
    tiktok: null,
    industries: ["化粧品", "ファッション", "飲料"],
    feeRange: "3000万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 98,
      food_beverage: 92,
      automotive: 75,
      finance_insurance: 78,
      it_technology: 85,
      real_estate: 80,
      retail_ec: 90,
      fashion_apparel: 95,
      game_entertainment: 98,
      sports_fitness: 80,
      travel_hotel: 88,
      education: 82,
      medical_healthcare: 80,
      telecom: 85,
      btob_services: 70,
      other: 82,
    },
    cmHistory: [
      {
        brand: "ヤマザキビスケット『チップスター』",
        industry: "食品",
        industryCode: "IND-002",
        year: "2024",
      },
      {
        brand: "ハウス食品『バーモントカレー』",
        industry: "食品",
        industryCode: "IND-002",
        year: "2024",
      },
      {
        brand: "アサヒビール『スーパードライ ドライクリスタル』",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-002"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 94,
          f1: { favorability: 96, recognition: 93 },
          f2: { favorability: 85, recognition: 82 },
        },
        industryExp: {
          score: 68,
        },
        brandAffinity: {
          score: 92,
        },
        costEff: {
          score: 96,
        },
      },
      highlights: [
        {
          title: "若年層から絶大な支持",
          vrData: {
            "10代支持率": 94,
            "20代支持率": 96,
            SNS拡散力: 95,
          },
        },
        {
          title: "清純で可愛らしいイメージ",
          imageData: {
            可愛らしさ: 98,
            清純さ: 94,
            親しみやすさ: 90,
          },
        },
        {
          title: "SNS拡散力が高い",
          reach: "Twitter98万フォロワー",
        },
      ],
      cmHistory: [
        {
          category: "食品",
          count: 2,
          items: [
            {
              brand: "ヤマザキビスケット『チップスター』",
              period: "2024年8月〜",
              results: {
                brandLift: 22,
                purchaseIntent: 18,
              },
            },
            {
              brand: "ハウス食品『バーモントカレー』",
              period: "2024年4月〜",
              results: {
                brandLift: 20,
                trialRate: 16,
              },
            },
          ],
        },
        {
          category: "飲料・アルコール",
          count: 1,
          items: [
            {
              brand: "アサヒビール『スーパードライ ドライクリスタル』",
              period: "2024年10月〜",
              results: {
                brandLift: 25,
                purchaseIntent: 20,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "5,000万円〜8,000万円",
          duration: "1年間",
          shootingDays: "5-8日",
        },
        webCm: {
          range: "300万円〜800万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "150万円〜250万円",
          duration: "2-3時間",
        },
        sns: {
          range: "50万円〜100万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 14,
    name: "浜辺美波",
    maskedName: "◯◯ ◯◯",
    kana: "はまべ みなみ",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "次世代エース女優",
    age: 24,
    awarenessScore: 94,
    matchScore: 92,
    introduction: "透明感と演技力を兼ね備えた次世代エース女優。",
    highlights: ["10-20代から圧倒的人気", "透明感のあるビジュアル", "映画・ドラマで主演多数"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["化粧品", "ファッション", "飲料"],
    feeRange: "4000万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 96,
      food_beverage: 90,
      automotive: 75,
      finance_insurance: 78,
      it_technology: 82,
      real_estate: 82,
      retail_ec: 88,
      fashion_apparel: 96,
      game_entertainment: 85,
      sports_fitness: 80,
      travel_hotel: 88,
      education: 80,
      medical_healthcare: 80,
      telecom: 82,
      btob_services: 70,
      other: 80,
    },
    cmHistory: [
      {
        brand: "コカ・コーラ『い・ろ・は・す』",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2023",
      },
      {
        brand: "UBE",
        industry: "BtoB・法人向けサービス",
        industryCode: "IND-010",
        year: "2024",
      },
      {
        brand: "JR東日本",
        industry: "旅行・ホテル",
        industryCode: "IND-009",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-009", "IND-010"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 92,
          f1: { favorability: 94, recognition: 90 },
          f2: { favorability: 83, recognition: 80 },
        },
        industryExp: {
          score: 70,
        },
        brandAffinity: {
          score: 90,
        },
        costEff: {
          score: 94,
        },
      },
      highlights: [
        {
          title: "10-20代から圧倒的人気",
          vrData: {
            "10代支持率": 92,
            "20代支持率": 94,
          },
        },
        {
          title: "透明感のあるビジュアル",
          imageData: {
            透明感: 96,
            清潔感: 94,
            上品さ: 88,
          },
        },
        {
          title: "映画・ドラマで主演多数",
          reach: "主演作品20本以上",
        },
      ],
      cmHistory: [
        {
          category: "飲料・アルコール",
          count: 1,
          items: [
            {
              brand: "コカ・コーラ『い・ろ・は・す』",
              period: "2023年",
              results: {
                brandLift: 18,
                purchaseIntent: 15,
              },
            },
          ],
        },
        {
          category: "BtoB・法人向けサービス",
          count: 1,
          items: [
            {
              brand: "UBE",
              period: "2024年10月〜",
              results: {
                brandRecognition: 30,
              },
            },
          ],
        },
        {
          category: "旅行・ホテル",
          count: 1,
          items: [
            {
              brand: "JR東日本",
              period: "2024年2月〜",
              results: {
                brandLift: 20,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "6,000万円〜9,000万円",
          duration: "1年間",
          shootingDays: "6-10日",
        },
        webCm: {
          range: "400万円〜1,000万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "150万円〜250万円",
          duration: "2-3時間",
        },
        sns: {
          range: "40万円〜80万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 15,
    name: "広瀬すず",
    maskedName: "◯◯ ◯◯",
    kana: "ひろせ すず",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "国民的若手女優",
    age: 26,
    awarenessScore: 97,
    matchScore: 95,
    introduction: "爽やかで明るいキャラクターが魅力の国民的若手女優。",
    highlights: ["全世代から高い認知度", "爽やかで明るいイメージ", "CM起用実績多数"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["化粧品", "飲料", "通信"],
    feeRange: "6000万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 98,
      food_beverage: 95,
      automotive: 85,
      finance_insurance: 85,
      it_technology: 88,
      real_estate: 88,
      retail_ec: 92,
      fashion_apparel: 96,
      game_entertainment: 88,
      sports_fitness: 90,
      travel_hotel: 92,
      education: 85,
      medical_healthcare: 85,
      telecom: 95,
      btob_services: 75,
      other: 85,
    },
    cmHistory: [
      {
        brand: "サントリー『ザ・プレミアム・モルツ』",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2023-2024",
      },
      {
        brand: "資生堂『dプログラム』",
        industry: "化粧品・トイレタリー",
        industryCode: "IND-004",
        year: "2023",
      },
      {
        brand: "マクドナルド『マックカフェ』",
        industry: "食品",
        industryCode: "IND-002",
        year: "2023",
      },
      {
        brand: "AGC",
        industry: "BtoB・法人向けサービス",
        industryCode: "IND-010",
        year: "2023-2024",
      },
      {
        brand: "スズキ『ワゴンR』",
        industry: "自動車",
        industryCode: "IND-003",
        year: "2023-2024",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-002", "IND-003", "IND-004", "IND-010"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 95,
          f1: { favorability: 95, recognition: 94 },
          f2: { favorability: 90, recognition: 91 },
        },
        industryExp: {
          score: 92,
        },
        brandAffinity: {
          score: 94,
        },
        costEff: {
          score: 90,
        },
      },
      highlights: [
        {
          title: "全世代から高い認知度",
          vrData: {
            全世代認知度: 97,
            "20代支持率": 95,
            "30代支持率": 94,
          },
        },
        {
          title: "爽やかで明るいイメージ",
          imageData: {
            爽やかさ: 96,
            明るさ: 95,
            親しみやすさ: 93,
          },
        },
        {
          title: "CM起用実績多数",
          reach: "年間CM出演本数15本以上",
        },
      ],
      cmHistory: [
        {
          category: "飲料・アルコール",
          count: 1,
          items: [
            {
              brand: "サントリー『ザ・プレミアム・モルツ』",
              period: "2023年7月〜2024年",
              results: {
                brandLift: 24,
                purchaseIntent: 20,
              },
            },
          ],
        },
        {
          category: "化粧品・トイレタリー",
          count: 1,
          items: [
            {
              brand: "資生堂『dプログラム』",
              period: "2023年",
              results: {
                brandLift: 18,
                trialRate: 14,
              },
            },
          ],
        },
        {
          category: "食品",
          count: 1,
          items: [
            {
              brand: "マクドナルド『マックカフェ』",
              period: "2023年",
              results: {
                brandLift: 22,
                purchaseIntent: 18,
              },
            },
          ],
        },
        {
          category: "自動車",
          count: 1,
          items: [
            {
              brand: "スズキ『ワゴンR』",
              period: "2023年〜2024年",
              results: {
                brandLift: 20,
                purchaseIntent: 16,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "9,000万円〜1億3,000万円",
          duration: "1年間",
          shootingDays: "8-12日",
        },
        webCm: {
          range: "600万円〜1,500万円",
          duration: "3-6ヶ月",
          shootingDays: "2-3日",
        },
        event: {
          range: "250万円〜400万円",
          duration: "2-4時間",
        },
        sns: {
          range: "70万円〜120万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 16,
    name: "永野芽郁",
    maskedName: "◯◯ ◯◯",
    kana: "ながの めい",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "実力派若手女優",
    age: 25,
    awarenessScore: 95,
    matchScore: 93,
    introduction: "演技力と親しみやすさを兼ね備えた実力派若手女優。",
    highlights: ["幅広い年齢層から支持", "親しみやすい笑顔", "ドラマ・映画で高評価"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["化粧品", "飲料", "保険"],
    feeRange: "4500万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 94,
      food_beverage: 92,
      automotive: 82,
      finance_insurance: 88,
      it_technology: 80,
      real_estate: 85,
      retail_ec: 88,
      fashion_apparel: 92,
      game_entertainment: 82,
      sports_fitness: 82,
      travel_hotel: 88,
      education: 85,
      medical_healthcare: 85,
      telecom: 85,
      btob_services: 75,
      other: 82,
    },
    cmHistory: [],
    currentUsageIndustries: [],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 93,
          f1: { favorability: 93, recognition: 90 },
          f2: { favorability: 88, recognition: 87 },
        },
        industryExp: {
          score: 88,
        },
        brandAffinity: {
          score: 92,
        },
        costEff: {
          score: 91,
        },
      },
      highlights: [
        {
          title: "幅広い年齢層から支持",
          vrData: {
            "20代支持率": 92,
            "30代支持率": 91,
            "40代支持率": 88,
          },
        },
        {
          title: "親しみやすい笑顔",
          imageData: {
            親しみやすさ: 95,
            笑顔: 94,
            清潔感: 90,
          },
        },
        {
          title: "ドラマ・映画で高評価",
          reach: "主演作品多数",
        },
      ],
      cmHistory: [
        {
          category: "化粧品・トイレタリー",
          count: 1,
          items: [
            {
              brand: "KOSE『雪肌精』",
              period: "2024年",
              results: {
                brandLift: 15,
                purchaseIntent: 12,
              },
            },
          ],
        },
        {
          category: "飲料・アルコール",
          count: 1,
          items: [
            {
              brand: "サントリー『クラフトボス』",
              period: "2023年",
              results: {
                brandLift: 17,
                trialRate: 13,
              },
            },
          ],
        },
        {
          category: "金融・保険",
          count: 1,
          items: [
            {
              brand: "第一生命",
              period: "2023年",
              results: {
                brandRecognition: 40,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "7,000万円〜1億円",
          duration: "1年間",
          shootingDays: "7-10日",
        },
        webCm: {
          range: "500万円〜1,200万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "200万円〜350万円",
          duration: "2-3時間",
        },
        sns: {
          range: "50万円〜100万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 17,
    name: "北川景子",
    maskedName: "◯◯ ◯◯",
    kana: "きたがわ けいこ",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "美人女優",
    age: 38,
    awarenessScore: 96,
    matchScore: 93,
    introduction: "端正な美貌と演技力を兼ね備えた美人女優。",
    highlights: ["端正な美貌", "高級感のあるイメージ", "30-40代女性から支持"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["化粧品", "ジュエリー", "ファッション"],
    feeRange: "6000万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 98,
      food_beverage: 88,
      automotive: 85,
      finance_insurance: 88,
      it_technology: 78,
      real_estate: 90,
      retail_ec: 88,
      fashion_apparel: 98,
      game_entertainment: 80,
      sports_fitness: 80,
      travel_hotel: 92,
      education: 80,
      medical_healthcare: 82,
      telecom: 82,
      btob_services: 75,
      other: 82,
    },
    cmHistory: [
      {
        brand: "コーセー『雪肌精』",
        industry: "化粧品・トイレタリー",
        industryCode: "IND-004",
        year: "2022-2024",
      },
      {
        brand: "ティファニー",
        industry: "その他",
        industryCode: "IND-016",
        year: "2023",
      },
      {
        brand: "三越",
        industry: "小売・EC",
        industryCode: "IND-012",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-004", "IND-012", "IND-016"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 93,
          f1: { favorability: 94, recognition: 92 },
          f2: { favorability: 90, recognition: 89 },
        },
        industryExp: {
          score: 88,
        },
        brandAffinity: {
          score: 95,
        },
        costEff: {
          score: 86,
        },
      },
      highlights: [
        {
          title: "端正な美貌",
          imageData: {
            美しさ: 98,
            上品さ: 95,
            洗練: 92,
          },
        },
        {
          title: "高級感のあるイメージ",
          imageData: {
            高級感: 96,
            ブランドイメージ: 94,
          },
        },
        {
          title: "30-40代女性から支持",
          vrData: {
            "30代女性支持率": 93,
            "40代女性支持率": 91,
          },
        },
      ],
      cmHistory: [
        {
          category: "化粧品・トイレタリー",
          count: 1,
          items: [
            {
              brand: "コーセー『雪肌精』",
              period: "2022年〜2024年",
              results: {
                brandLift: 20,
                purchaseIntent: 18,
              },
            },
          ],
        },
        {
          category: "その他",
          count: 1,
          items: [
            {
              brand: "ティファニー",
              period: "2023年",
              results: {
                brandLift: 15,
              },
            },
          ],
        },
        {
          category: "小売・EC",
          count: 1,
          items: [
            {
              brand: "三越",
              period: "2024年",
              results: {
                brandLift: 12,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "9,000万円〜1億3,000万円",
          duration: "1年間",
          shootingDays: "8-12日",
        },
        webCm: {
          range: "600万円〜1,500万円",
          duration: "3-6ヶ月",
          shootingDays: "2-3日",
        },
        event: {
          range: "250万円〜400万円",
          duration: "2-4時間",
        },
        sns: {
          range: "70万円〜120万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 18,
    name: "深田恭子",
    maskedName: "◯◯ ◯◯",
    kana: "ふかだ きょうこ",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "ベテラン女優",
    age: 42,
    awarenessScore: 95,
    matchScore: 90,
    introduction: "長年活躍し続けるベテラン女優。可愛らしさと色気を兼ね備える。",
    highlights: ["長年の実績", "可愛らしさと色気", "30-50代から支持"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["化粧品", "ファッション", "飲料"],
    feeRange: "5500万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 95,
      food_beverage: 88,
      automotive: 80,
      finance_insurance: 82,
      it_technology: 75,
      real_estate: 85,
      retail_ec: 88,
      fashion_apparel: 95,
      game_entertainment: 82,
      sports_fitness: 85,
      travel_hotel: 88,
      education: 78,
      medical_healthcare: 80,
      telecom: 80,
      btob_services: 72,
      other: 80,
    },
    cmHistory: [
      {
        brand: "ロート製薬『肌ラボ』",
        industry: "化粧品・トイレタリー",
        industryCode: "IND-004",
        year: "2023-2024",
      },
      {
        brand: "アサヒビール『クリアアサヒ』",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2023",
      },
      {
        brand: "GUCCI",
        industry: "ファッション・アパレル",
        industryCode: "IND-008",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-004", "IND-008"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 90,
          f1: { favorability: 90, recognition: 88 },
          f2: { favorability: 87, recognition: 85 },
        },
        industryExp: {
          score: 85,
        },
        brandAffinity: {
          score: 93,
        },
        costEff: {
          score: 88,
        },
      },
      highlights: [
        {
          title: "長年の実績",
          reach: "デビュー25年以上",
        },
        {
          title: "可愛らしさと色気",
          imageData: {
            可愛らしさ: 94,
            色気: 92,
            魅力: 90,
          },
        },
        {
          title: "30-50代から支持",
          vrData: {
            "30代支持率": 90,
            "40代支持率": 92,
            "50代支持率": 88,
          },
        },
      ],
      cmHistory: [
        {
          category: "化粧品・トイレタリー",
          count: 1,
          items: [
            {
              brand: "ロート製薬『肌ラボ』",
              period: "2023年〜2024年",
              results: {
                brandLift: 18,
                purchaseIntent: 15,
              },
            },
          ],
        },
        {
          category: "飲料・アルコール",
          count: 1,
          items: [
            {
              brand: "アサヒビール『クリアアサヒ』",
              period: "2023年",
              results: {
                brandLift: 16,
              },
            },
          ],
        },
        {
          category: "ファッション・アパレル",
          count: 1,
          items: [
            {
              brand: "GUCCI",
              period: "2024年",
              results: {
                brandLift: 12,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "8,000万円〜1億1,000万円",
          duration: "1年間",
          shootingDays: "7-10日",
        },
        webCm: {
          range: "500万円〜1,200万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "200万円〜300万円",
          duration: "2-3時間",
        },
        sns: {
          range: "50万円〜100万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 19,
    name: "長澤まさみ",
    maskedName: "◯◯ ◯◯",
    kana: "ながさわ まさみ",
    category: "女優",
    categoryColor: "#DBEAFE",
    title: "実力派女優",
    age: 37,
    awarenessScore: 96,
    matchScore: 92,
    introduction: "演技力と美貌を兼ね備えた実力派女優。",
    highlights: ["高い演技力", "幅広い役柄に対応", "全世代から支持"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["化粧品", "飲料", "自動車"],
    feeRange: "6500万円〜",
    imageUrl: "/japanese-actress-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 96,
      food_beverage: 92,
      automotive: 88,
      finance_insurance: 85,
      it_technology: 80,
      real_estate: 88,
      retail_ec: 88,
      fashion_apparel: 94,
      game_entertainment: 82,
      sports_fitness: 85,
      travel_hotel: 92,
      education: 82,
      medical_healthcare: 82,
      telecom: 85,
      btob_services: 78,
      other: 82,
    },
    cmHistory: [
      {
        brand: "資生堂『エリクシール』",
        industry: "化粧品・トイレタリー",
        industryCode: "IND-004",
        year: "2023-2024",
      },
      {
        brand: "サントリー『クラフトボス』",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2024",
      },
      {
        brand: "SUBARU『フォレスター』",
        industry: "自動車",
        industryCode: "IND-003",
        year: "2023",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-003", "IND-004"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 92,
          f1: { favorability: 93, recognition: 91 },
          f2: { favorability: 89, recognition: 88 },
        },
        industryExp: {
          score: 90,
        },
        brandAffinity: {
          score: 94,
        },
        costEff: {
          score: 87,
        },
      },
      highlights: [
        {
          title: "高い演技力",
          reach: "数々の受賞歴",
        },
        {
          title: "幅広い役柄に対応",
          vrData: {
            演技幅: 95,
          },
        },
        {
          title: "全世代から支持",
          vrData: {
            "20代支持率": 90,
            "30代支持率": 93,
            "40代支持率": 94,
            "50代以上支持率": 88,
          },
        },
      ],
      cmHistory: [
        {
          category: "化粧品・トイレタリー",
          count: 1,
          items: [
            {
              brand: "資生堂『エリクシール』",
              period: "2023年〜2024年",
              results: {
                brandLift: 22,
                purchaseIntent: 19,
              },
            },
          ],
        },
        {
          category: "飲料・アルコール",
          count: 1,
          items: [
            {
              brand: "サントリー『クラフトボス』",
              period: "2024年",
              results: {
                brandLift: 19,
                trialRate: 16,
              },
            },
          ],
        },
        {
          category: "自動車",
          count: 1,
          items: [
            {
              brand: "SUBARU『フォレスター』",
              period: "2023年",
              results: {
                brandLift: 20,
                purchaseIntent: 17,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "1億円〜1億4,000万円",
          duration: "1年間",
          shootingDays: "9-13日",
        },
        webCm: {
          range: "600万円〜1,600万円",
          duration: "3-6ヶ月",
          shootingDays: "2-3日",
        },
        event: {
          range: "250万円〜400万円",
          duration: "2-4時間",
        },
        sns: {
          range: "70万円〜130万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 20,
    name: "羽生結弦",
    maskedName: "◯◯ ◯◯",
    kana: "はにゅう ゆづる",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "フィギュアスケーター",
    age: 30,
    awarenessScore: 99,
    matchScore: 96,
    introduction: "オリンピック2連覇の国民的フィギュアスケーター。",
    highlights: ["国民的人気", "高い品格とイメージ", "全世代から尊敬"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["スポーツ", "保険", "飲料"],
    feeRange: "1億円〜",
    imageUrl: "/japanese-figure-skater-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 75,
      food_beverage: 92,
      automotive: 85,
      finance_insurance: 95,
      it_technology: 82,
      real_estate: 88,
      retail_ec: 85,
      fashion_apparel: 88,
      game_entertainment: 85,
      sports_fitness: 100,
      travel_hotel: 90,
      education: 92,
      medical_healthcare: 88,
      telecom: 85,
      btob_services: 85,
      other: 88,
    },
    cmHistory: [
      {
        brand: "ANA",
        industry: "旅行・ホテル",
        industryCode: "IND-009",
        year: "2023-2024",
      },
      {
        brand: "明治『プロテインダイエット』",
        industry: "食品",
        industryCode: "IND-002",
        year: "2023",
      },
      {
        brand: "日本生命",
        industry: "金融・保険",
        industryCode: "IND-005",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-002", "IND-005", "IND-009"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 96,
          f1: { favorability: 98, recognition: 97 },
          f2: { favorability: 92, recognition: 90 },
        },
        industryExp: {
          score: 98,
        },
        brandAffinity: {
          score: 99,
        },
        costEff: {
          score: 80,
        },
      },
      highlights: [
        {
          title: "国民的人気",
          vrData: {
            国民認知度: 99,
            "10代支持率": 95,
            "20代支持率": 97,
            "30代支持率": 98,
            "40代支持率": 99,
          },
        },
        {
          title: "高い品格とイメージ",
          imageData: {
            品格: 99,
            誠実さ: 98,
            アスリートイメージ: 97,
          },
        },
        {
          title: "全世代から尊敬",
          reach: "オリンピック2連覇",
        },
      ],
      cmHistory: [
        {
          category: "旅行・ホテル",
          count: 1,
          items: [
            {
              brand: "ANA",
              period: "2023年〜2024年",
              results: {
                brandLift: 25,
                brandRecognition: 50,
              },
            },
          ],
        },
        {
          category: "食品",
          count: 1,
          items: [
            {
              brand: "明治『プロテインダイエット』",
              period: "2023年",
              results: {
                brandLift: 18,
                purchaseIntent: 15,
              },
            },
          ],
        },
        {
          category: "金融・保険",
          count: 1,
          items: [
            {
              brand: "日本生命",
              period: "2024年",
              results: {
                brandLift: 20,
                brandRecognition: 48,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "1億5,000万円〜2億円",
          duration: "1年間",
          shootingDays: "12-15日",
        },
        webCm: {
          range: "1,000万円〜2,000万円",
          duration: "3-6ヶ月",
          shootingDays: "2-4日",
        },
        event: {
          range: "400万円〜600万円",
          duration: "2-4時間",
        },
        sns: {
          range: "100万円〜200万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 21,
    name: "YOASOBI",
    maskedName: "◯◯◯◯◯◯",
    kana: "よあそび",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "音楽ユニット",
    age: 26,
    awarenessScore: 96,
    matchScore: 94,
    introduction: "若年層に絶大な人気を誇る音楽ユニット。小説を音楽にする独自のスタイル。",
    highlights: ["10代・20代から圧倒的支持", "グローバル展開", "SNS拡散力"],
    instagram: "2.8M",
    youtube: "8.5M",
    twitter: "1.2M",
    tiktok: "3.5M",
    industries: ["飲料", "IT・テクノロジー", "ゲーム・エンタメ"],
    feeRange: "3000万円〜",
    imageUrl: "/japanese-music-duo-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 85,
      food_beverage: 92,
      automotive: 75,
      finance_insurance: 70,
      it_technology: 95,
      real_estate: 70,
      retail_ec: 88,
      fashion_apparel: 90,
      game_entertainment: 98,
      sports_fitness: 75,
      travel_hotel: 85,
      education: 80,
      medical_healthcare: 65,
      telecom: 90,
      btob_services: 70,
      other: 80,
    },
    cmHistory: [
      {
        brand: "リクルート",
        industry: "BtoB・サービス",
        industryCode: "IND-015",
        year: "2024",
      },
      {
        brand: "マクドナルド『夜マック』",
        industry: "食品・飲料",
        industryCode: "IND-002",
        year: "2024",
      },
      {
        brand: "みずほ銀行",
        industry: "金融・保険",
        industryCode: "IND-005",
        year: "2024",
      },
      {
        brand: "サントリー生ビール",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2025",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-002", "IND-005", "IND-015"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 94,
          f1: { favorability: 98, recognition: 96 },
          f2: { favorability: 85, recognition: 82 },
        },
        industryExp: {
          score: 92,
        },
        brandAffinity: {
          score: 95,
        },
        costEff: {
          score: 88,
        },
      },
      highlights: [
        {
          title: "若年層への圧倒的リーチ",
          vrData: {
            "10代認知度": 98,
            "20代認知度": 96,
            "10代好感度": 97,
            "20代好感度": 95,
          },
        },
        {
          title: "SNS拡散力",
          imageData: {
            TikTok総再生数: "10億回超",
            YouTube登録者: "850万人",
            Instagram: "280万人",
          },
        },
        {
          title: "グローバル展開",
          reach: "Billboard Japan Hot 100 1位獲得多数",
        },
      ],
      cmHistory: [
        {
          category: "飲料・アルコール",
          count: 1,
          items: [
            {
              brand: "サントリー生ビール",
              period: "2025年",
              results: {
                brandLift: 28,
                brandRecognition: 55,
              },
            },
          ],
        },
        {
          category: "食品・飲料",
          count: 1,
          items: [
            {
              brand: "マクドナルド『夜マック』",
              period: "2024年",
              results: {
                brandLift: 32,
                purchaseIntent: 28,
              },
            },
          ],
        },
        {
          category: "金融・保険",
          count: 1,
          items: [
            {
              brand: "みずほ銀行",
              period: "2024年",
              results: {
                brandLift: 22,
                brandRecognition: 45,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "5,000万円〜8,000万円",
          duration: "1年間",
          shootingDays: "3-5日",
        },
        webCm: {
          range: "800万円〜1,500万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "300万円〜500万円",
          duration: "2-3時間",
        },
        sns: {
          range: "150万円〜250万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 22,
    name: "米津玄師",
    maskedName: "◯◯ ◯◯",
    kana: "よねづ けんし",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "シンガーソングライター",
    age: 33,
    awarenessScore: 97,
    matchScore: 95,
    introduction: "独創的な音楽性で幅広い世代に支持されるアーティスト。",
    highlights: ["全世代認知", "クリエイティブ性", "映画・アニメタイアップ多数"],
    instagram: "3.2M",
    youtube: "7.8M",
    twitter: "2.1M",
    tiktok: null,
    industries: ["ゲーム・エンタメ", "IT・テクノロジー", "自動車"],
    feeRange: "5000万円〜",
    imageUrl: "/japanese-music-artist-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 80,
      food_beverage: 88,
      automotive: 92,
      finance_insurance: 75,
      it_technology: 95,
      real_estate: 75,
      retail_ec: 85,
      fashion_apparel: 88,
      game_entertainment: 98,
      sports_fitness: 75,
      travel_hotel: 85,
      education: 80,
      medical_healthcare: 70,
      telecom: 90,
      btob_services: 75,
      other: 82,
    },
    cmHistory: [
      {
        brand: "PlayStation",
        industry: "ゲーム・エンタメ",
        industryCode: "IND-008",
        year: "2023",
      },
      {
        brand: "映画『シン・ウルトラマン』主題歌",
        industry: "ゲーム・エンタメ",
        industryCode: "IND-008",
        year: "2022",
      },
    ],
    currentUsageIndustries: ["IND-008"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 95,
          f1: { favorability: 96, recognition: 95 },
          f2: { favorability: 90, recognition: 88 },
        },
        industryExp: {
          score: 96,
        },
        brandAffinity: {
          score: 97,
        },
        costEff: {
          score: 82,
        },
      },
      highlights: [
        {
          title: "全世代への高い認知度",
          vrData: {
            "10代認知度": 95,
            "20代認知度": 97,
            "30代認知度": 96,
            "40代認知度": 92,
          },
        },
        {
          title: "クリエイティブ性",
          imageData: {
            独創性: 98,
            芸術性: 97,
            先進性: 96,
          },
        },
        {
          title: "映画・アニメタイアップ実績",
          reach: "Billboard Japan年間チャート1位獲得",
        },
      ],
      cmHistory: [
        {
          category: "ゲーム・エンタメ",
          count: 2,
          items: [
            {
              brand: "PlayStation",
              period: "2023年",
              results: {
                brandLift: 35,
                brandRecognition: 60,
              },
            },
            {
              brand: "映画『シン・ウルトラマン』主題歌",
              period: "2022年",
              results: {
                brandLift: 40,
                purchaseIntent: 35,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "8,000万円〜1億2,000万円",
          duration: "1年間",
          shootingDays: "3-5日",
        },
        webCm: {
          range: "1,000万円〜2,000万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "500万円〜800万円",
          duration: "2-3時間",
        },
        sns: {
          range: "200万円〜300万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 23,
    name: "あいみょん",
    maskedName: "◯◯◯◯",
    kana: "あいみょん",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "シンガーソングライター",
    age: 29,
    awarenessScore: 94,
    matchScore: 92,
    introduction: "共感性の高い歌詞で若年層から絶大な支持を得るアーティスト。",
    highlights: ["F1層への強い訴求力", "共感性の高い楽曲", "ライブ動員力"],
    instagram: "1.8M",
    youtube: "3.2M",
    twitter: "850K",
    tiktok: null,
    industries: ["化粧品・美容", "ファッション・アパレル", "食品・飲料"],
    feeRange: "3000万円〜",
    imageUrl: "/japanese-singer-songwriter-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 95,
      food_beverage: 90,
      automotive: 70,
      finance_insurance: 72,
      it_technology: 85,
      real_estate: 70,
      retail_ec: 88,
      fashion_apparel: 95,
      game_entertainment: 88,
      sports_fitness: 75,
      travel_hotel: 85,
      education: 80,
      medical_healthcare: 70,
      telecom: 85,
      btob_services: 68,
      other: 78,
    },
    cmHistory: [
      {
        brand: "映画『ドラえもん』主題歌",
        industry: "ゲーム・エンタメ",
        industryCode: "IND-008",
        year: "2025",
      },
    ],
    currentUsageIndustries: ["IND-008"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 92,
          f1: { favorability: 97, recognition: 94 },
          f2: { favorability: 88, recognition: 85 },
        },
        industryExp: {
          score: 88,
        },
        brandAffinity: {
          score: 93,
        },
        costEff: {
          score: 90,
        },
      },
      highlights: [
        {
          title: "F1層への強い訴求力",
          vrData: {
            F1層好感度: 97,
            F1層認知度: 94,
            "20代女性支持率": 96,
          },
        },
        {
          title: "共感性の高い楽曲",
          imageData: {
            共感性: 96,
            親しみやすさ: 95,
            等身大感: 94,
          },
        },
        {
          title: "ライブ動員力",
          reach: "全国ツアー完売実績多数",
        },
      ],
      cmHistory: [
        {
          category: "ゲーム・エンタメ",
          count: 1,
          items: [
            {
              brand: "映画『ドラえもん』主題歌",
              period: "2025年",
              results: {
                brandLift: 30,
                brandRecognition: 52,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "5,000万円〜7,000万円",
          duration: "1年間",
          shootingDays: "2-4日",
        },
        webCm: {
          range: "800万円〜1,200万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "300万円〜500万円",
          duration: "2-3時間",
        },
        sns: {
          range: "150万円〜200万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 24,
    name: "Official髭男dism",
    maskedName: "◯◯◯◯◯◯◯◯◯◯",
    kana: "おふぃしゃるひげだんでぃずむ",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "バンド",
    age: 32,
    awarenessScore: 95,
    matchScore: 93,
    introduction: "ポップで洗練された楽曲で幅広い層に支持されるバンド。",
    highlights: ["ドラマ・映画タイアップ多数", "ポジティブなイメージ", "幅広い年齢層にリーチ"],
    instagram: "1.5M",
    youtube: "4.8M",
    twitter: "920K",
    tiktok: null,
    industries: ["自動車", "飲料", "IT・テクノロジー"],
    feeRange: "4000万円〜",
    imageUrl: "/japanese-rock-band-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 82,
      food_beverage: 92,
      automotive: 95,
      finance_insurance: 80,
      it_technology: 90,
      real_estate: 78,
      retail_ec: 88,
      fashion_apparel: 88,
      game_entertainment: 92,
      sports_fitness: 85,
      travel_hotel: 90,
      education: 85,
      medical_healthcare: 75,
      telecom: 90,
      btob_services: 75,
      other: 82,
    },
    cmHistory: [
      {
        brand: "トヨタ自動車",
        industry: "自動車",
        industryCode: "IND-004",
        year: "2023",
      },
    ],
    currentUsageIndustries: ["IND-004"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 93,
          f1: { favorability: 94, recognition: 92 },
          f2: { favorability: 90, recognition: 88 },
        },
        industryExp: {
          score: 92,
        },
        brandAffinity: {
          score: 94,
        },
        costEff: {
          score: 88,
        },
      },
      highlights: [
        {
          title: "ドラマ・映画タイアップ実績",
          vrData: {
            タイアップ認知度: 96,
            楽曲好感度: 94,
            "20代認知度": 95,
            "30代認知度": 93,
          },
        },
        {
          title: "ポジティブなイメージ",
          imageData: {
            ポジティブ: 95,
            爽やか: 93,
            洗練: 92,
          },
        },
        {
          title: "幅広い年齢層にリーチ",
          reach: "ストリーミング累計100億回超",
        },
      ],
      cmHistory: [
        {
          category: "自動車",
          count: 1,
          items: [
            {
              brand: "トヨタ自動車",
              period: "2023年",
              results: {
                brandLift: 28,
                brandRecognition: 50,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "6,000万円〜9,000万円",
          duration: "1年間",
          shootingDays: "3-5日",
        },
        webCm: {
          range: "900万円〜1,500万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "400万円〜600万円",
          duration: "2-3時間",
        },
        sns: {
          range: "180万円〜250万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 25,
    name: "Mrs. GREEN APPLE",
    maskedName: "◯◯◯ ◯◯◯◯◯ ◯◯◯◯◯",
    kana: "みせす ぐりーん あっぷる",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "バンド",
    age: 28,
    awarenessScore: 94,
    matchScore: 92,
    introduction: "エネルギッシュなパフォーマンスで若年層に人気のバンド。",
    highlights: ["若年層への高い訴求力", "ライブパフォーマンス", "SNS拡散力"],
    instagram: "1.2M",
    youtube: "3.5M",
    twitter: "780K",
    tiktok: "2.1M",
    industries: ["飲料", "金融・保険", "ゲーム・エンタメ"],
    feeRange: "3500万円〜",
    imageUrl: "/japanese-pop-band-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 85,
      food_beverage: 92,
      automotive: 85,
      finance_insurance: 88,
      it_technology: 90,
      real_estate: 75,
      retail_ec: 88,
      fashion_apparel: 90,
      game_entertainment: 95,
      sports_fitness: 88,
      travel_hotel: 85,
      education: 85,
      medical_healthcare: 72,
      telecom: 90,
      btob_services: 75,
      other: 82,
    },
    cmHistory: [
      {
        brand: "第一生命保険",
        industry: "金融・保険",
        industryCode: "IND-005",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-005"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 92,
          f1: { favorability: 95, recognition: 93 },
          f2: { favorability: 87, recognition: 84 },
        },
        industryExp: {
          score: 90,
        },
        brandAffinity: {
          score: 93,
        },
        costEff: {
          score: 89,
        },
      },
      highlights: [
        {
          title: "若年層への高い訴求力",
          vrData: {
            "10代認知度": 96,
            "20代認知度": 94,
            "10代好感度": 95,
            "20代好感度": 93,
          },
        },
        {
          title: "エネルギッシュなパフォーマンス",
          imageData: {
            エネルギー: 96,
            ポジティブ: 94,
            若々しさ: 95,
          },
        },
        {
          title: "SNS拡散力",
          reach: "TikTok総再生数5億回超",
        },
      ],
      cmHistory: [
        {
          category: "金融・保険",
          count: 1,
          items: [
            {
              brand: "第一生命保険",
              period: "2024年",
              results: {
                brandLift: 25,
                brandRecognition: 48,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "5,500万円〜8,000万円",
          duration: "1年間",
          shootingDays: "3-5日",
        },
        webCm: {
          range: "850万円〜1,400万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "350万円〜550万円",
          duration: "2-3時間",
        },
        sns: {
          range: "170万円〜240万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 26,
    name: "Ado",
    maskedName: "◯◯◯",
    kana: "あど",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "歌手",
    age: 22,
    awarenessScore: 95,
    matchScore: 93,
    introduction: "圧倒的な歌唱力で若年層を中心に絶大な人気を誇る歌手。",
    highlights: ["Z世代への強い訴求力", "グローバル展開", "アニメタイアップ"],
    instagram: "2.5M",
    youtube: "6.2M",
    twitter: "1.8M",
    tiktok: "4.2M",
    industries: ["ゲーム・エンタメ", "ファッション・アパレル", "化粧品・美容"],
    feeRange: "4000万円〜",
    imageUrl: "/japanese-singer-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 92,
      food_beverage: 88,
      automotive: 72,
      finance_insurance: 70,
      it_technology: 90,
      real_estate: 68,
      retail_ec: 90,
      fashion_apparel: 95,
      game_entertainment: 98,
      sports_fitness: 78,
      travel_hotel: 82,
      education: 75,
      medical_healthcare: 68,
      telecom: 88,
      btob_services: 65,
      other: 78,
    },
    cmHistory: [
      {
        brand: "映画『ONE PIECE FILM RED』主題歌",
        industry: "ゲーム・エンタメ",
        industryCode: "IND-008",
        year: "2022",
      },
    ],
    currentUsageIndustries: ["IND-008"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 93,
          f1: { favorability: 98, recognition: 95 },
          f2: { favorability: 82, recognition: 80 },
        },
        industryExp: {
          score: 90,
        },
        brandAffinity: {
          score: 94,
        },
        costEff: {
          score: 88,
        },
      },
      highlights: [
        {
          title: "Z世代への強い訴求力",
          vrData: {
            "10代認知度": 98,
            "20代認知度": 95,
            "10代好感度": 97,
          },
        },
        {
          title: "圧倒的な歌唱力",
          imageData: {
            歌唱力: 99,
            個性: 97,
            インパクト: 98,
          },
        },
        {
          title: "グローバル展開",
          reach: "Billboard Global 200チャートイン",
        },
      ],
      cmHistory: [
        {
          category: "ゲーム・エンタメ",
          count: 1,
          items: [
            {
              brand: "映画『ONE PIECE FILM RED』主題歌",
              period: "2022年",
              results: {
                brandLift: 45,
                purchaseIntent: 40,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "6,000万円〜9,000万円",
          duration: "1年間",
          shootingDays: "2-4日",
        },
        webCm: {
          range: "900万円〜1,500万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "400万円〜600万円",
          duration: "2-3時間",
        },
        sns: {
          range: "200万円〜300万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 27,
    name: "星野源",
    maskedName: "◯◯ ◯",
    kana: "ほしの げん",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "シンガーソングライター・俳優",
    age: 44,
    awarenessScore: 96,
    matchScore: 94,
    introduction: "音楽と俳優業で活躍するマルチタレント。幅広い世代に支持される。",
    highlights: ["全世代認知", "マルチタレント", "ドラマ主題歌多数"],
    instagram: "2.1M",
    youtube: "2.8M",
    twitter: "1.5M",
    tiktok: null,
    industries: ["飲料", "自動車", "IT・テクノロジー"],
    feeRange: "5000万円〜",
    imageUrl: "/japanese-music-artist-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 85,
      food_beverage: 95,
      automotive: 92,
      finance_insurance: 88,
      it_technology: 90,
      real_estate: 85,
      retail_ec: 88,
      fashion_apparel: 88,
      game_entertainment: 92,
      sports_fitness: 80,
      travel_hotel: 90,
      education: 88,
      medical_healthcare: 82,
      telecom: 90,
      btob_services: 80,
      other: 85,
    },
    cmHistory: [],
    currentUsageIndustries: [],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 94,
          f1: { favorability: 92, recognition: 94 },
          f2: { favorability: 95, recognition: 96 },
        },
        industryExp: {
          score: 95,
        },
        brandAffinity: {
          score: 96,
        },
        costEff: {
          score: 85,
        },
      },
      highlights: [
        {
          title: "全世代への高い認知度",
          vrData: {
            "20代認知度": 94,
            "30代認知度": 96,
            "40代認知度": 97,
            "50代認知度": 95,
          },
        },
        {
          title: "マルチタレント",
          imageData: {
            多才さ: 97,
            親しみやすさ: 96,
            信頼感: 95,
          },
        },
        {
          title: "ドラマ主題歌実績",
          reach: "紅白歌合戦出場多数",
        },
      ],
      cmHistory: [],
      cost: {
        tvCm: {
          range: "8,000万円〜1億2,000万円",
          duration: "1年間",
          shootingDays: "5-7日",
        },
        webCm: {
          range: "1,000万円〜2,000万円",
          duration: "3-6ヶ月",
          shootingDays: "2-3日",
        },
        event: {
          range: "500万円〜800万円",
          duration: "2-3時間",
        },
        sns: {
          range: "200万円〜300万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 28,
    name: "Perfume",
    maskedName: "◯◯◯◯◯◯◯",
    kana: "ぱふゅーむ",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "テクノポップユニット",
    age: 35,
    awarenessScore: 93,
    matchScore: 91,
    introduction: "先進的なパフォーマンスで国内外から支持されるユニット。",
    highlights: ["テクノロジー親和性", "グローバル展開", "先進的イメージ"],
    instagram: "1.8M",
    youtube: "2.5M",
    twitter: "1.2M",
    tiktok: null,
    industries: ["IT・テクノロジー", "化粧品・美容", "自動車"],
    feeRange: "4000万円〜",
    imageUrl: "/japanese-pop-group-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 95,
      food_beverage: 85,
      automotive: 90,
      finance_insurance: 80,
      it_technology: 98,
      real_estate: 78,
      retail_ec: 90,
      fashion_apparel: 95,
      game_entertainment: 92,
      sports_fitness: 75,
      travel_hotel: 88,
      education: 82,
      medical_healthcare: 75,
      telecom: 95,
      btob_services: 80,
      other: 82,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 29,
    name: "LiSA",
    maskedName: "◯◯◯◯",
    kana: "りさ",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "アニソン歌手",
    age: 37,
    awarenessScore: 92,
    matchScore: 90,
    introduction: "アニメ主題歌で絶大な人気を誇る歌手。",
    highlights: ["アニメファン層への訴求力", "ライブパフォーマンス", "若年層支持"],
    instagram: "1.5M",
    youtube: "3.8M",
    twitter: "1.1M",
    tiktok: null,
    industries: ["ゲーム・エンタメ", "飲料", "ファッション・アパレル"],
    feeRange: "3000万円〜",
    imageUrl: "/japanese-singer-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 88,
      food_beverage: 90,
      automotive: 70,
      finance_insurance: 68,
      it_technology: 88,
      real_estate: 65,
      retail_ec: 88,
      fashion_apparel: 92,
      game_entertainment: 98,
      sports_fitness: 75,
      travel_hotel: 80,
      education: 75,
      medical_healthcare: 65,
      telecom: 85,
      btob_services: 65,
      other: 75,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 30,
    name: "King Gnu",
    maskedName: "◯◯◯◯ ◯◯◯",
    kana: "きんぐ ぬー",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "バンド",
    age: 31,
    awarenessScore: 93,
    matchScore: 91,
    introduction: "独創的な音楽性で若年層を中心に人気のバンド。",
    highlights: ["音楽性の高さ", "ドラマタイアップ", "若年層支持"],
    instagram: "1.3M",
    youtube: "3.2M",
    twitter: "850K",
    tiktok: null,
    industries: ["自動車", "IT・テクノロジー", "ファッション・アパレル"],
    feeRange: "4000万円〜",
    imageUrl: "/japanese-rock-band-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 82,
      food_beverage: 88,
      automotive: 95,
      finance_insurance: 78,
      it_technology: 92,
      real_estate: 75,
      retail_ec: 85,
      fashion_apparel: 92,
      game_entertainment: 90,
      sports_fitness: 80,
      travel_hotel: 85,
      education: 80,
      medical_healthcare: 70,
      telecom: 90,
      btob_services: 75,
      other: 80,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 31,
    name: "back number",
    maskedName: "◯◯◯◯ ◯◯◯◯◯◯",
    kana: "ばっく なんばー",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "バンド",
    age: 38,
    awarenessScore: 94,
    matchScore: 92,
    introduction: "恋愛ソングで幅広い世代に支持されるバンド。",
    highlights: ["ドラマ主題歌多数", "共感性の高い楽曲", "幅広い年齢層"],
    instagram: "980K",
    youtube: "2.8M",
    twitter: "720K",
    tiktok: null,
    industries: ["飲料", "化粧品・美容", "小売・EC"],
    feeRange: "3500万円〜",
    imageUrl: "/japanese-rock-band-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 90,
      food_beverage: 92,
      automotive: 85,
      finance_insurance: 80,
      it_technology: 82,
      real_estate: 78,
      retail_ec: 90,
      fashion_apparel: 88,
      game_entertainment: 88,
      sports_fitness: 75,
      travel_hotel: 88,
      education: 82,
      medical_healthcare: 75,
      telecom: 85,
      btob_services: 72,
      other: 80,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 32,
    name: "Vaundy",
    maskedName: "◯◯◯◯◯◯",
    kana: "ばうんでぃ",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "シンガーソングライター",
    age: 26,
    awarenessScore: 90,
    matchScore: 88,
    introduction: "独創的な音楽性で若年層から支持されるアーティスト。",
    highlights: ["Z世代への訴求力", "クリエイティブ性", "SNS拡散力"],
    instagram: "1.1M",
    youtube: "2.2M",
    twitter: "650K",
    tiktok: "1.8M",
    industries: ["ファッション・アパレル", "IT・テクノロジー", "ゲーム・エンタメ"],
    feeRange: "2500万円〜",
    imageUrl: "/japanese-music-artist-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 88,
      food_beverage: 85,
      automotive: 78,
      finance_insurance: 70,
      it_technology: 92,
      real_estate: 70,
      retail_ec: 88,
      fashion_apparel: 95,
      game_entertainment: 92,
      sports_fitness: 75,
      travel_hotel: 82,
      education: 78,
      medical_healthcare: 68,
      telecom: 88,
      btob_services: 70,
      other: 78,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 33,
    name: "BUMP OF CHICKEN",
    maskedName: "◯◯◯◯ ◯◯ ◯◯◯◯◯◯",
    kana: "ばんぷ おぶ ちきん",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "バンド",
    age: 46,
    awarenessScore: 95,
    matchScore: 93,
    introduction: "長年にわたり幅広い世代に支持されるロックバンド。",
    highlights: ["全世代認知", "ドラマ・映画タイアップ", "ライブ動員力"],
    instagram: "850K",
    youtube: "3.5M",
    twitter: "980K",
    tiktok: null,
    industries: ["自動車", "飲料", "ゲーム・エンタメ"],
    feeRange: "5000万円〜",
    imageUrl: "/japanese-rock-band-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 78,
      food_beverage: 90,
      automotive: 95,
      finance_insurance: 85,
      it_technology: 88,
      real_estate: 80,
      retail_ec: 85,
      fashion_apparel: 85,
      game_entertainment: 95,
      sports_fitness: 82,
      travel_hotel: 88,
      education: 88,
      medical_healthcare: 78,
      telecom: 88,
      btob_services: 78,
      other: 82,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 34,
    name: "RADWIMPS",
    maskedName: "◯◯◯◯◯◯◯◯",
    kana: "らっどうぃんぷす",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "バンド",
    age: 40,
    awarenessScore: 94,
    matchScore: 92,
    introduction: "映画『君の名は。』主題歌で知られる人気バンド。",
    highlights: ["映画タイアップ実績", "幅広い年齢層", "ライブパフォーマンス"],
    instagram: "1.2M",
    youtube: "3.8M",
    twitter: "1.1M",
    tiktok: null,
    industries: ["ゲーム・エンタメ", "飲料", "IT・テクノロジー"],
    feeRange: "4500万円〜",
    imageUrl: "/japanese-rock-band-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 80,
      food_beverage: 90,
      automotive: 88,
      finance_insurance: 80,
      it_technology: 90,
      real_estate: 78,
      retail_ec: 85,
      fashion_apparel: 88,
      game_entertainment: 96,
      sports_fitness: 80,
      travel_hotel: 88,
      education: 85,
      medical_healthcare: 75,
      telecom: 88,
      btob_services: 75,
      other: 82,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 35,
    name: "Aimer",
    maskedName: "◯◯◯◯◯",
    kana: "えめ",
    category: "アーティスト",
    categoryColor: "#FEF3C7",
    title: "歌手",
    age: 34,
    awarenessScore: 89,
    matchScore: 87,
    introduction: "独特のハスキーボイスで人気の歌手。アニメタイアップ多数。",
    highlights: ["アニメファン層への訴求力", "独特の歌声", "大人っぽいイメージ"],
    instagram: "920K",
    youtube: "2.8M",
    twitter: "780K",
    tiktok: null,
    industries: ["ゲーム・エンタメ", "化粧品・美容", "ファッション・アパレル"],
    feeRange: "2500万円〜",
    imageUrl: "/japanese-singer-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 92,
      food_beverage: 82,
      automotive: 75,
      finance_insurance: 72,
      it_technology: 85,
      real_estate: 70,
      retail_ec: 85,
      fashion_apparel: 92,
      game_entertainment: 96,
      sports_fitness: 70,
      travel_hotel: 82,
      education: 75,
      medical_healthcare: 70,
      telecom: 82,
      btob_services: 68,
      other: 75,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 36,
    name: "大谷翔平",
    maskedName: "◯◯ ◯◯",
    kana: "おおたに しょうへい",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "プロ野球選手",
    age: 30,
    awarenessScore: 99,
    matchScore: 98,
    introduction: "MLB史上初の二刀流スーパースター。国民的人気を誇る。",
    highlights: ["国民的人気", "グローバル展開", "全世代認知"],
    instagram: "6.5M",
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["スポーツ", "飲料", "自動車"],
    feeRange: "2億円〜",
    imageUrl: "/japanese-baseball-player-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 85,
      food_beverage: 98,
      automotive: 95,
      finance_insurance: 92,
      it_technology: 90,
      real_estate: 88,
      retail_ec: 90,
      fashion_apparel: 92,
      game_entertainment: 95,
      sports_fitness: 100,
      travel_hotel: 92,
      education: 95,
      medical_healthcare: 90,
      telecom: 92,
      btob_services: 85,
      other: 90,
    },
    cmHistory: [
      {
        brand: "伊藤園『お〜いお茶』",
        industry: "飲料",
        industryCode: "IND-001",
        year: "2024",
      },
      {
        brand: "ニューバランス",
        industry: "ファッション・アパレル",
        industryCode: "IND-007",
        year: "2024",
      },
      {
        brand: "コーセー『コスメデコルテ』",
        industry: "化粧品・美容",
        industryCode: "IND-003",
        year: "2024",
      },
      {
        brand: "BOSS",
        industry: "ファッション・アパレル",
        industryCode: "IND-007",
        year: "2024",
      },
      {
        brand: "コナミ『プロ野球スピリッツA』",
        industry: "ゲーム・エンタメ",
        industryCode: "IND-008",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-001", "IND-003", "IND-007", "IND-008"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 98,
          f1: { favorability: 97, recognition: 99 },
          f2: { favorability: 98, recognition: 99 },
        },
        industryExp: {
          score: 99,
        },
        brandAffinity: {
          score: 99,
        },
        costEff: {
          score: 75,
        },
      },
      highlights: [
        {
          title: "国民的人気",
          vrData: {
            国民認知度: 99,
            "10代支持率": 98,
            "20代支持率": 99,
            "30代支持率": 99,
            "40代支持率": 99,
          },
        },
        {
          title: "グローバル展開",
          imageData: {
            グローバル認知: 98,
            信頼感: 99,
            憧れ: 98,
          },
        },
        {
          title: "全世代から尊敬",
          reach: "MLB MVP・ワールドシリーズ優勝",
        },
      ],
      cmHistory: [
        {
          category: "飲料",
          count: 1,
          items: [
            {
              brand: "伊藤園『お〜いお茶』",
              period: "2024年",
              results: {
                brandLift: 40,
                brandRecognition: 65,
              },
            },
          ],
        },
        {
          category: "ファッション・アパレル",
          count: 2,
          items: [
            {
              brand: "ニューバランス",
              period: "2024年",
              results: {
                brandLift: 45,
                purchaseIntent: 38,
              },
            },
            {
              brand: "BOSS",
              period: "2024年",
              results: {
                brandLift: 35,
                purchaseIntent: 30,
              },
            },
          ],
        },
        {
          category: "ゲーム・エンタメ",
          count: 1,
          items: [
            {
              brand: "コナミ『プロ野球スピリッツA』",
              period: "2024年",
              results: {
                brandLift: 50,
                purchaseIntent: 45,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "3億円〜5億円",
          duration: "1年間",
          shootingDays: "15-20日",
        },
        webCm: {
          range: "3,000万円〜5,000万円",
          duration: "3-6ヶ月",
          shootingDays: "3-5日",
        },
        event: {
          range: "1,000万円〜1,500万円",
          duration: "2-4時間",
        },
        sns: {
          range: "500万円〜800万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 37,
    name: "八村塁",
    maskedName: "◯◯ ◯",
    kana: "はちむら るい",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "プロバスケットボール選手",
    age: 27,
    awarenessScore: 92,
    matchScore: 90,
    introduction: "NBA で活躍する日本人バスケットボール選手。若年層に人気。",
    highlights: ["若年層への訴求力", "グローバル展開", "バスケ人気"],
    instagram: "1.8M",
    youtube: null,
    twitter: "520K",
    tiktok: null,
    industries: ["スポーツ", "飲料", "ファッション・アパレル"],
    feeRange: "5000万円〜",
    imageUrl: "/japanese-basketball-player-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 75,
      food_beverage: 92,
      automotive: 85,
      finance_insurance: 80,
      it_technology: 88,
      real_estate: 75,
      retail_ec: 88,
      fashion_apparel: 95,
      game_entertainment: 92,
      sports_fitness: 98,
      travel_hotel: 85,
      education: 85,
      medical_healthcare: 80,
      telecom: 88,
      btob_services: 75,
      other: 82,
    },
    cmHistory: [
      {
        brand: "アサヒスーパードライ",
        industry: "飲料・アルコール",
        industryCode: "IND-001",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-001"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 90,
          f1: { favorability: 92, recognition: 90 },
          f2: { favorability: 85, recognition: 82 },
        },
        industryExp: {
          score: 88,
        },
        brandAffinity: {
          score: 91,
        },
        costEff: {
          score: 87,
        },
      },
      highlights: [
        {
          title: "若年層への訴求力",
          vrData: {
            "10代認知度": 95,
            "20代認知度": 93,
            "10代好感度": 94,
            "20代好感度": 92,
          },
        },
        {
          title: "グローバル展開",
          imageData: {
            グローバル認知: 90,
            かっこよさ: 95,
            憧れ: 93,
          },
        },
        {
          title: "バスケ人気上昇",
          reach: "NBA優勝・日本代表",
        },
      ],
      cmHistory: [
        {
          category: "飲料・アルコール",
          count: 1,
          items: [
            {
              brand: "アサヒスーパードライ",
              period: "2024年",
              results: {
                brandLift: 30,
                brandRecognition: 52,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "8,000万円〜1億2,000万円",
          duration: "1年間",
          shootingDays: "5-8日",
        },
        webCm: {
          range: "1,000万円〜1,800万円",
          duration: "3-6ヶ月",
          shootingDays: "2-3日",
        },
        event: {
          range: "400万円〜600万円",
          duration: "2-3時間",
        },
        sns: {
          range: "200万円〜300万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 38,
    name: "久保建英",
    maskedName: "◯◯ ◯◯",
    kana: "くぼ たけふさ",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "プロサッカー選手",
    age: 23,
    awarenessScore: 94,
    matchScore: 92,
    introduction: "欧州で活躍する日本代表の若きエース。",
    highlights: ["若年層への訴求力", "欧州での活躍", "将来性"],
    instagram: "2.5M",
    youtube: null,
    twitter: "680K",
    tiktok: null,
    industries: ["スポーツ", "飲料", "自動車"],
    feeRange: "6000万円〜",
    imageUrl: "/japanese-soccer-player-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 78,
      food_beverage: 92,
      automotive: 90,
      finance_insurance: 82,
      it_technology: 88,
      real_estate: 78,
      retail_ec: 88,
      fashion_apparel: 92,
      game_entertainment: 90,
      sports_fitness: 98,
      travel_hotel: 88,
      education: 88,
      medical_healthcare: 80,
      telecom: 90,
      btob_services: 78,
      other: 85,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 39,
    name: "三笘薫",
    maskedName: "◯◯ ◯",
    kana: "みとま かおる",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "プロサッカー選手",
    age: 27,
    awarenessScore: 93,
    matchScore: 91,
    introduction: "プレミアリーグで活躍する日本代表選手。",
    highlights: ["若年層への訴求力", "プレミアリーグ", "技術の高さ"],
    instagram: "1.8M",
    youtube: null,
    twitter: "520K",
    tiktok: null,
    industries: ["スポーツ", "飲料", "ファッション・アパレル"],
    feeRange: "5000万円〜",
    imageUrl: "/japanese-soccer-player-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 75,
      food_beverage: 90,
      automotive: 88,
      finance_insurance: 80,
      it_technology: 85,
      real_estate: 75,
      retail_ec: 85,
      fashion_apparel: 90,
      game_entertainment: 88,
      sports_fitness: 96,
      travel_hotel: 85,
      education: 85,
      medical_healthcare: 78,
      telecom: 88,
      btob_services: 75,
      other: 82,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 40,
    name: "南野拓実",
    maskedName: "◯◯ ◯◯",
    kana: "みなみの たくみ",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "プロサッカー選手",
    age: 30,
    awarenessScore: 91,
    matchScore: 89,
    introduction: "欧州で長年活躍する日本代表選手。",
    highlights: ["安定した実績", "欧州での経験", "幅広い年齢層"],
    instagram: "1.2M",
    youtube: null,
    twitter: "420K",
    tiktok: null,
    industries: ["スポーツ", "飲料", "自動車"],
    feeRange: "4000万円〜",
    imageUrl: "/japanese-soccer-player-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 72,
      food_beverage: 88,
      automotive: 88,
      finance_insurance: 80,
      it_technology: 82,
      real_estate: 75,
      retail_ec: 82,
      fashion_apparel: 85,
      game_entertainment: 85,
      sports_fitness: 95,
      travel_hotel: 82,
      education: 82,
      medical_healthcare: 78,
      telecom: 85,
      btob_services: 75,
      other: 80,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 41,
    name: "堂安律",
    maskedName: "◯◯ ◯",
    kana: "どうあん りつ",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "プロサッカー選手",
    age: 26,
    awarenessScore: 90,
    matchScore: 88,
    introduction: "ブンデスリーガで活躍する日本代表選手。",
    highlights: ["若年層への訴求力", "ドイツでの活躍", "攻撃的なプレー"],
    instagram: "980K",
    youtube: null,
    twitter: "380K",
    tiktok: null,
    industries: ["スポーツ", "飲料", "ゲーム・エンタメ"],
    feeRange: "3500万円〜",
    imageUrl: "/japanese-soccer-player-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 70,
      food_beverage: 88,
      automotive: 85,
      finance_insurance: 75,
      it_technology: 82,
      real_estate: 72,
      retail_ec: 82,
      fashion_apparel: 85,
      game_entertainment: 88,
      sports_fitness: 94,
      travel_hotel: 80,
      education: 80,
      medical_healthcare: 75,
      telecom: 85,
      btob_services: 72,
      other: 78,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 42,
    name: "藤井聡太",
    maskedName: "◯◯ ◯◯",
    kana: "ふじい そうた",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "プロ棋士",
    age: 22,
    awarenessScore: 96,
    matchScore: 94,
    introduction: "史上最年少で八冠達成した天才棋士。",
    highlights: ["全世代認知", "知性のイメージ", "若年層への訴求力"],
    instagram: null,
    youtube: null,
    twitter: null,
    tiktok: null,
    industries: ["教育", "金融・保険", "IT・テクノロジー"],
    feeRange: "8000万円〜",
    imageUrl: "/japanese-shogi-player-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 70,
      food_beverage: 85,
      automotive: 82,
      finance_insurance: 95,
      it_technology: 92,
      real_estate: 85,
      retail_ec: 80,
      fashion_apparel: 75,
      game_entertainment: 88,
      sports_fitness: 75,
      travel_hotel: 82,
      education: 98,
      medical_healthcare: 85,
      telecom: 88,
      btob_services: 88,
      other: 85,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 43,
    name: "池江璃花子",
    maskedName: "◯◯ ◯◯◯",
    kana: "いけえ りかこ",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "競泳選手",
    age: 24,
    awarenessScore: 94,
    matchScore: 92,
    introduction: "病気を克服しオリンピックに復帰した感動のストーリー。",
    highlights: ["感動ストーリー", "若年層への訴求力", "前向きなイメージ"],
    instagram: "1.5M",
    youtube: null,
    twitter: "620K",
    tiktok: null,
    industries: ["スポーツ", "医療・ヘルスケア", "化粧品・美容"],
    feeRange: "5000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 92,
      food_beverage: 88,
      automotive: 75,
      finance_insurance: 82,
      it_technology: 80,
      real_estate: 75,
      retail_ec: 85,
      fashion_apparel: 90,
      game_entertainment: 80,
      sports_fitness: 96,
      travel_hotel: 82,
      education: 88,
      medical_healthcare: 95,
      telecom: 82,
      btob_services: 75,
      other: 82,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 44,
    name: "大坂なおみ",
    maskedName: "◯◯ ◯◯◯",
    kana: "おおさか なおみ",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "プロテニス選手",
    age: 27,
    awarenessScore: 95,
    matchScore: 93,
    introduction: "グランドスラム優勝経験を持つ世界的テニスプレーヤー。",
    highlights: ["グローバル展開", "社会的影響力", "若年層への訴求力"],
    instagram: "2.8M",
    youtube: null,
    twitter: "1.1M",
    tiktok: null,
    industries: ["スポーツ", "化粧品・美容", "ファッション・アパレル"],
    feeRange: "1億円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 95,
      food_beverage: 88,
      automotive: 85,
      finance_insurance: 85,
      it_technology: 88,
      real_estate: 80,
      retail_ec: 90,
      fashion_apparel: 96,
      game_entertainment: 85,
      sports_fitness: 98,
      travel_hotel: 88,
      education: 85,
      medical_healthcare: 85,
      telecom: 88,
      btob_services: 78,
      other: 85,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 45,
    name: "錦織圭",
    maskedName: "◯◯ ◯",
    kana: "にしこり けい",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "プロテニス選手",
    age: 35,
    awarenessScore: 93,
    matchScore: 91,
    introduction: "日本テニス界のパイオニア。長年世界で活躍。",
    highlights: ["全世代認知", "グローバル展開", "実績"],
    instagram: "850K",
    youtube: null,
    twitter: "520K",
    tiktok: null,
    industries: ["スポーツ", "自動車", "金融・保険"],
    feeRange: "8000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 75,
      food_beverage: 88,
      automotive: 92,
      finance_insurance: 90,
      it_technology: 85,
      real_estate: 85,
      retail_ec: 85,
      fashion_apparel: 90,
      game_entertainment: 82,
      sports_fitness: 96,
      travel_hotel: 88,
      education: 85,
      medical_healthcare: 82,
      telecom: 88,
      btob_services: 82,
      other: 85,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 46,
    name: "渋野日向子",
    maskedName: "◯◯ ◯◯◯",
    kana: "しぶの ひなこ",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "プロゴルファー",
    age: 26,
    awarenessScore: 90,
    matchScore: 88,
    introduction: "全英女子オープン優勝の笑顔が魅力的なゴルファー。",
    highlights: ["親しみやすさ", "若年層への訴求力", "明るいイメージ"],
    instagram: "680K",
    youtube: null,
    twitter: "420K",
    tiktok: null,
    industries: ["スポーツ", "飲料", "化粧品・美容"],
    feeRange: "4000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 90,
      food_beverage: 92,
      automotive: 80,
      finance_insurance: 82,
      it_technology: 75,
      real_estate: 78,
      retail_ec: 85,
      fashion_apparel: 88,
      game_entertainment: 78,
      sports_fitness: 94,
      travel_hotel: 85,
      education: 82,
      medical_healthcare: 80,
      telecom: 82,
      btob_services: 75,
      other: 80,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 47,
    name: "内村航平",
    maskedName: "◯◯ ◯◯",
    kana: "うちむら こうへい",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "体操選手",
    age: 35,
    awarenessScore: 92,
    matchScore: 90,
    introduction: "オリンピック金メダリスト。体操界のレジェンド。",
    highlights: ["全世代認知", "実績", "品格"],
    instagram: "520K",
    youtube: null,
    twitter: "380K",
    tiktok: null,
    industries: ["スポーツ", "教育", "医療・ヘルスケア"],
    feeRange: "5000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 72,
      food_beverage: 85,
      automotive: 80,
      finance_insurance: 85,
      it_technology: 78,
      real_estate: 78,
      retail_ec: 80,
      fashion_apparel: 80,
      game_entertainment: 78,
      sports_fitness: 96,
      travel_hotel: 80,
      education: 92,
      medical_healthcare: 88,
      telecom: 80,
      btob_services: 78,
      other: 80,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 48,
    name: "高梨沙羅",
    maskedName: "◯◯ ◯◯",
    kana: "たかなし さら",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "スキージャンプ選手",
    age: 28,
    awarenessScore: 91,
    matchScore: 89,
    introduction: "ワールドカップ最多勝記録を持つスキージャンプ選手。",
    highlights: ["冬季スポーツ", "実績", "若年層への訴求力"],
    instagram: "620K",
    youtube: null,
    twitter: "450K",
    tiktok: null,
    industries: ["スポーツ", "飲料", "化粧品・美容"],
    feeRange: "4000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 88,
      food_beverage: 88,
      automotive: 78,
      finance_insurance: 80,
      it_technology: 75,
      real_estate: 75,
      retail_ec: 82,
      fashion_apparel: 85,
      game_entertainment: 75,
      sports_fitness: 94,
      travel_hotel: 85,
      education: 82,
      medical_healthcare: 78,
      telecom: 80,
      btob_services: 72,
      other: 78,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 49,
    name: "本田真凜",
    maskedName: "◯◯ ◯◯",
    kana: "ほんだ まりん",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "フィギュアスケーター",
    age: 23,
    awarenessScore: 88,
    matchScore: 86,
    introduction: "華やかな演技で人気のフィギュアスケーター。",
    highlights: ["若年層への訴求力", "華やかさ", "SNS発信力"],
    instagram: "1.2M",
    youtube: null,
    twitter: "380K",
    tiktok: null,
    industries: ["化粧品・美容", "ファッション・アパレル", "スポーツ"],
    feeRange: "3000万円〜",
    imageUrl: "/japanese-figure-skater-portrait.jpg",
    industryFit: {
      beauty_cosmetics: 92,
      food_beverage: 82,
      automotive: 72,
      finance_insurance: 75,
      it_technology: 78,
      real_estate: 70,
      retail_ec: 85,
      fashion_apparel: 92,
      game_entertainment: 80,
      sports_fitness: 90,
      travel_hotel: 80,
      education: 78,
      medical_healthcare: 75,
      telecom: 78,
      btob_services: 68,
      other: 75,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 50,
    name: "井上尚弥",
    maskedName: "◯◯ ◯◯",
    kana: "いのうえ なおや",
    category: "アスリート",
    categoryColor: "#D1FAE5",
    title: "プロボクサー",
    age: 31,
    awarenessScore: 91,
    matchScore: 89,
    introduction: "4階級制覇の世界的ボクサー。モンスターの異名を持つ。",
    highlights: ["男性への訴求力", "実績", "グローバル展開"],
    instagram: "850K",
    youtube: null,
    twitter: "520K",
    tiktok: null,
    industries: ["スポーツ", "飲料", "自動車"],
    feeRange: "5000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 68,
      food_beverage: 90,
      automotive: 88,
      finance_insurance: 82,
      it_technology: 80,
      real_estate: 78,
      retail_ec: 80,
      fashion_apparel: 85,
      game_entertainment: 85,
      sports_fitness: 96,
      travel_hotel: 80,
      education: 78,
      medical_healthcare: 80,
      telecom: 82,
      btob_services: 78,
      other: 80,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 51,
    name: "ヒカキン",
    maskedName: "◯◯◯◯",
    kana: "ひかきん",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuber",
    age: 35,
    awarenessScore: 96,
    matchScore: 94,
    introduction: "日本を代表するトップYouTuber。子供から大人まで幅広い支持。",
    highlights: ["子供・若年層への訴求力", "SNS拡散力", "クリーンなイメージ"],
    instagram: "1.5M",
    youtube: "15.2M",
    twitter: "2.8M",
    tiktok: "3.5M",
    industries: ["ゲーム・エンタメ", "食品・飲料", "IT・テクノロジー"],
    feeRange: "3000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 75,
      food_beverage: 95,
      automotive: 75,
      finance_insurance: 70,
      it_technology: 95,
      real_estate: 68,
      retail_ec: 92,
      fashion_apparel: 82,
      game_entertainment: 98,
      sports_fitness: 78,
      travel_hotel: 82,
      education: 85,
      medical_healthcare: 70,
      telecom: 90,
      btob_services: 70,
      other: 80,
    },
    cmHistory: [
      {
        brand: "ファイナルファンタジーXIV",
        industry: "ゲーム・エンタメ",
        industryCode: "IND-008",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-008"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 94,
          f1: { favorability: 92, recognition: 95 },
          f2: { favorability: 88, recognition: 90 },
        },
        industryExp: {
          score: 92,
        },
        brandAffinity: {
          score: 95,
        },
        costEff: {
          score: 90,
        },
      },
      highlights: [
        {
          title: "子供・若年層への訴求力",
          vrData: {
            "10代認知度": 98,
            "20代認知度": 96,
            "10代好感度": 97,
            "20代好感度": 94,
          },
        },
        {
          title: "SNS拡散力",
          imageData: {
            YouTube登録者: "1,520万人",
            Twitter: "280万人",
            TikTok: "350万人",
          },
        },
        {
          title: "クリーンなイメージ",
          reach: "企業案件実績多数",
        },
      ],
      cmHistory: [
        {
          category: "ゲーム・エンタメ",
          count: 1,
          items: [
            {
              brand: "ファイナルファンタジーXIV",
              period: "2024年",
              results: {
                brandLift: 35,
                brandRecognition: 58,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "5,000万円〜8,000万円",
          duration: "1年間",
          shootingDays: "3-5日",
        },
        webCm: {
          range: "800万円〜1,500万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "300万円〜500万円",
          duration: "2-3時間",
        },
        sns: {
          range: "200万円〜350万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 52,
    name: "はじめしゃちょー",
    maskedName: "◯◯◯◯◯◯◯◯",
    kana: "はじめしゃちょー",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuber",
    age: 32,
    awarenessScore: 95,
    matchScore: 93,
    introduction: "実験系動画で人気のトップYouTuber。",
    highlights: ["若年層への訴求力", "SNS拡散力", "エンタメ性"],
    instagram: "1.2M",
    youtube: "10.5M",
    twitter: "2.1M",
    tiktok: "2.8M",
    industries: ["ゲーム・エンタメ", "食品・飲料", "小売・EC"],
    feeRange: "2500万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 72,
      food_beverage: 92,
      automotive: 72,
      finance_insurance: 68,
      it_technology: 90,
      real_estate: 65,
      retail_ec: 90,
      fashion_apparel: 78,
      game_entertainment: 96,
      sports_fitness: 75,
      travel_hotel: 78,
      education: 80,
      medical_healthcare: 65,
      telecom: 85,
      btob_services: 65,
      other: 75,
    },
    cmHistory: [
      {
        brand: "ファイナルファンタジーXIV",
        industry: "ゲーム・エンタメ",
        industryCode: "IND-008",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-008"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 93,
          f1: { favorability: 90, recognition: 94 },
          f2: { favorability: 85, recognition: 88 },
        },
        industryExp: {
          score: 90,
        },
        brandAffinity: {
          score: 93,
        },
        costEff: {
          score: 91,
        },
      },
      highlights: [
        {
          title: "若年層への訴求力",
          vrData: {
            "10代認知度": 97,
            "20代認知度": 95,
            "10代好感度": 96,
          },
        },
        {
          title: "SNS拡散力",
          imageData: {
            YouTube登録者: "1,050万人",
            Twitter: "210万人",
            TikTok: "280万人",
          },
        },
        {
          title: "エンタメ性",
          reach: "実験系動画で高い再生数",
        },
      ],
      cmHistory: [
        {
          category: "ゲーム・エンタメ",
          count: 1,
          items: [
            {
              brand: "ファイナルファンタジーXIV",
              period: "2024年",
              results: {
                brandLift: 32,
                brandRecognition: 55,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "4,000万円〜6,000万円",
          duration: "1年間",
          shootingDays: "3-5日",
        },
        webCm: {
          range: "700万円〜1,200万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "250万円〜400万円",
          duration: "2-3時間",
        },
        sns: {
          range: "180万円〜300万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 53,
    name: "フワちゃん",
    maskedName: "◯◯◯◯◯",
    kana: "ふわちゃん",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuber・タレント",
    age: 30,
    awarenessScore: 93,
    matchScore: 91,
    introduction: "独特のキャラクターで人気のマルチタレント。",
    highlights: ["若年層への訴求力", "バラエティ番組出演", "SNS発信力"],
    instagram: "1.8M",
    youtube: "2.5M",
    twitter: "1.5M",
    tiktok: "2.2M",
    industries: ["ゲーム・エンタメ", "IT・テクノロジー", "食品・飲料"],
    feeRange: "3000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 80,
      food_beverage: 90,
      automotive: 70,
      finance_insurance: 68,
      it_technology: 92,
      real_estate: 65,
      retail_ec: 88,
      fashion_apparel: 85,
      game_entertainment: 95,
      sports_fitness: 75,
      travel_hotel: 82,
      education: 75,
      medical_healthcare: 65,
      telecom: 88,
      btob_services: 65,
      other: 75,
    },
    cmHistory: [
      {
        brand: "Nintendo『僕は少年冒険家』",
        industry: "ゲーム・エンタメ",
        industryCode: "IND-008",
        year: "2024",
      },
      {
        brand: "Google Pixel 8",
        industry: "IT・テクノロジー",
        industryCode: "IND-006",
        year: "2024",
      },
    ],
    currentUsageIndustries: ["IND-006", "IND-008"],
    detailData: {
      scoreBreakdown: {
        targetFit: {
          score: 91,
          f1: { favorability: 93, recognition: 92 },
          f2: { favorability: 85, recognition: 83 },
        },
        industryExp: {
          score: 88,
        },
        brandAffinity: {
          score: 92,
        },
        costEff: {
          score: 89,
        },
      },
      highlights: [
        {
          title: "若年層への訴求力",
          vrData: {
            "10代認知度": 95,
            "20代認知度": 94,
            "10代好感度": 94,
          },
        },
        {
          title: "バラエティ番組出演",
          imageData: {
            エンタメ性: 96,
            親しみやすさ: 95,
            個性: 97,
          },
        },
        {
          title: "SNS発信力",
          reach: "Instagram 180万人・YouTube 250万人",
        },
      ],
      cmHistory: [
        {
          category: "ゲーム・エンタメ",
          count: 1,
          items: [
            {
              brand: "Nintendo『僕は少年冒険家』",
              period: "2024年",
              results: {
                brandLift: 30,
                brandRecognition: 52,
              },
            },
          ],
        },
        {
          category: "IT・テクノロジー",
          count: 1,
          items: [
            {
              brand: "Google Pixel 8",
              period: "2024年",
              results: {
                brandLift: 28,
                purchaseIntent: 22,
              },
            },
          ],
        },
      ],
      cost: {
        tvCm: {
          range: "5,000万円〜7,000万円",
          duration: "1年間",
          shootingDays: "3-5日",
        },
        webCm: {
          range: "800万円〜1,300万円",
          duration: "3-6ヶ月",
          shootingDays: "1-2日",
        },
        event: {
          range: "300万円〜450万円",
          duration: "2-3時間",
        },
        sns: {
          range: "200万円〜300万円",
          duration: "24時間",
        },
      },
    },
  },
  {
    id: 54,
    name: "東海オンエア",
    maskedName: "◯◯◯◯◯◯",
    kana: "とうかいおんえあ",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuberグループ",
    age: 30,
    awarenessScore: 94,
    matchScore: 92,
    introduction: "愛知発の人気YouTuberグループ。",
    highlights: ["若年層への訴求力", "グループ力", "エンタメ性"],
    instagram: "980K",
    youtube: "7.2M",
    twitter: "1.8M",
    tiktok: null,
    industries: ["ゲーム・エンタメ", "食品・飲料", "小売・EC"],
    feeRange: "3000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 70,
      food_beverage: 92,
      automotive: 75,
      finance_insurance: 65,
      it_technology: 88,
      real_estate: 62,
      retail_ec: 90,
      fashion_apparel: 78,
      game_entertainment: 95,
      sports_fitness: 75,
      travel_hotel: 80,
      education: 75,
      medical_healthcare: 62,
      telecom: 82,
      btob_services: 62,
      other: 72,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 55,
    name: "コムドット",
    maskedName: "◯◯◯◯◯",
    kana: "こむどっと",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuberグループ",
    age: 26,
    awarenessScore: 93,
    matchScore: 91,
    introduction: "Z世代に絶大な人気を誇るYouTuberグループ。",
    highlights: ["Z世代への訴求力", "SNS拡散力", "トレンド発信力"],
    instagram: "2.2M",
    youtube: "4.8M",
    twitter: "850K",
    tiktok: "3.5M",
    industries: ["ファッション・アパレル", "ゲーム・エンタメ", "小売・EC"],
    feeRange: "2500万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 78,
      food_beverage: 88,
      automotive: 70,
      finance_insurance: 62,
      it_technology: 88,
      real_estate: 60,
      retail_ec: 92,
      fashion_apparel: 95,
      game_entertainment: 92,
      sports_fitness: 78,
      travel_hotel: 80,
      education: 70,
      medical_healthcare: 60,
      telecom: 85,
      btob_services: 60,
      other: 70,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 56,
    name: "ヒカル",
    maskedName: "◯◯◯",
    kana: "ひかる",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuber",
    age: 33,
    awarenessScore: 91,
    matchScore: 89,
    introduction: "カリスマ性のある人気YouTuber。",
    highlights: ["若年層への訴求力", "企画力", "SNS拡散力"],
    instagram: "1.5M",
    youtube: "5.8M",
    twitter: "1.2M",
    tiktok: null,
    industries: ["ゲーム・エンタメ", "小売・EC", "金融・保険"],
    feeRange: "2500万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 72,
      food_beverage: 85,
      automotive: 75,
      finance_insurance: 80,
      it_technology: 88,
      real_estate: 75,
      retail_ec: 92,
      fashion_apparel: 82,
      game_entertainment: 94,
      sports_fitness: 75,
      travel_hotel: 78,
      education: 72,
      medical_healthcare: 65,
      telecom: 85,
      btob_services: 72,
      other: 75,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 57,
    name: "水溜りボンド",
    maskedName: "◯◯◯◯◯◯",
    kana: "みずたまりぼんど",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuberコンビ",
    age: 30,
    awarenessScore: 90,
    matchScore: 88,
    introduction: "実験・検証系動画で人気のYouTuberコンビ。",
    highlights: ["若年層への訴求力", "実験系コンテンツ", "安定した人気"],
    instagram: "680K",
    youtube: "5.2M",
    twitter: "920K",
    tiktok: null,
    industries: ["ゲーム・エンタメ", "食品・飲料", "IT・テクノロジー"],
    feeRange: "2000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 68,
      food_beverage: 88,
      automotive: 70,
      finance_insurance: 62,
      it_technology: 85,
      real_estate: 60,
      retail_ec: 85,
      fashion_apparel: 72,
      game_entertainment: 92,
      sports_fitness: 72,
      travel_hotel: 75,
      education: 75,
      medical_healthcare: 60,
      telecom: 80,
      btob_services: 60,
      other: 70,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 58,
    name: "フィッシャーズ",
    maskedName: "◯◯◯◯◯◯◯",
    kana: "ふぃっしゃーず",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuberグループ",
    age: 29,
    awarenessScore: 92,
    matchScore: 90,
    introduction: "アスレチック系動画で人気のYouTuberグループ。",
    highlights: ["子供・若年層への訴求力", "アクティブなイメージ", "グループ力"],
    instagram: "850K",
    youtube: "6.8M",
    twitter: "1.1M",
    tiktok: null,
    industries: ["ゲーム・エンタメ", "スポーツ", "食品・飲料"],
    feeRange: "2500万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 65,
      food_beverage: 90,
      automotive: 72,
      finance_insurance: 60,
      it_technology: 82,
      real_estate: 58,
      retail_ec: 85,
      fashion_apparel: 75,
      game_entertainment: 94,
      sports_fitness: 92,
      travel_hotel: 80,
      education: 78,
      medical_healthcare: 60,
      telecom: 78,
      btob_services: 58,
      other: 70,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 59,
    name: "すしらーめん《りく》",
    maskedName: "◯◯◯◯◯◯◯◯◯",
    kana: "すしらーめんりく",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuber",
    age: 27,
    awarenessScore: 88,
    matchScore: 86,
    introduction: "ゲーム実況で人気のYouTuber。",
    highlights: ["若年層への訴求力", "ゲーム実況", "親しみやすさ"],
    instagram: "520K",
    youtube: "4.2M",
    twitter: "780K",
    tiktok: null,
    industries: ["ゲーム・エンタメ", "IT・テクノロジー", "食品・飲料"],
    feeRange: "1800万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 62,
      food_beverage: 85,
      automotive: 65,
      finance_insurance: 58,
      it_technology: 88,
      real_estate: 55,
      retail_ec: 82,
      fashion_apparel: 68,
      game_entertainment: 96,
      sports_fitness: 68,
      travel_hotel: 70,
      education: 70,
      medical_healthcare: 55,
      telecom: 80,
      btob_services: 55,
      other: 65,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 60,
    name: "古川優香",
    maskedName: "◯◯ ◯◯",
    kana: "ふるかわ ゆうか",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuber・モデル",
    age: 27,
    awarenessScore: 89,
    matchScore: 87,
    introduction: "美容・ファッション系で人気のインフルエンサー。",
    highlights: ["F1層への訴求力", "美容・ファッション", "SNS発信力"],
    instagram: "1.8M",
    youtube: "1.5M",
    twitter: "620K",
    tiktok: "980K",
    industries: ["化粧品・美容", "ファッション・アパレル", "小売・EC"],
    feeRange: "2000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 96,
      food_beverage: 82,
      automotive: 65,
      finance_insurance: 62,
      it_technology: 78,
      real_estate: 60,
      retail_ec: 92,
      fashion_apparel: 96,
      game_entertainment: 75,
      sports_fitness: 80,
      travel_hotel: 82,
      education: 70,
      medical_healthcare: 72,
      telecom: 75,
      btob_services: 58,
      other: 70,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 61,
    name: "ゆうこす",
    maskedName: "◯◯◯◯",
    kana: "ゆうこす",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "インフルエンサー・実業家",
    age: 30,
    awarenessScore: 87,
    matchScore: 85,
    introduction: "モテクリエイターとして活躍するインフルエンサー。",
    highlights: ["F1層への訴求力", "美容・コスメ", "ビジネス展開"],
    instagram: "1.2M",
    youtube: "680K",
    twitter: "520K",
    tiktok: "850K",
    industries: ["化粧品・美容", "ファッション・アパレル", "小売・EC"],
    feeRange: "1800万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 98,
      food_beverage: 78,
      automotive: 60,
      finance_insurance: 65,
      it_technology: 75,
      real_estate: 58,
      retail_ec: 90,
      fashion_apparel: 94,
      game_entertainment: 70,
      sports_fitness: 78,
      travel_hotel: 78,
      education: 68,
      medical_healthcare: 70,
      telecom: 72,
      btob_services: 60,
      other: 68,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 62,
    name: "渡辺直美",
    maskedName: "◯◯ ◯◯",
    kana: "わたなべ なおみ",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "タレント・インフルエンサー",
    age: 37,
    awarenessScore: 95,
    matchScore: 93,
    introduction: "グローバルに活躍するタレント・インフルエンサー。",
    highlights: ["全世代認知", "グローバル展開", "ポジティブなイメージ"],
    instagram: "9.8M",
    youtube: "1.2M",
    twitter: "1.5M",
    tiktok: "4.2M",
    industries: ["化粧品・美容", "ファッション・アパレル", "食品・飲料"],
    feeRange: "5000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 92,
      food_beverage: 95,
      automotive: 75,
      finance_insurance: 72,
      it_technology: 82,
      real_estate: 70,
      retail_ec: 92,
      fashion_apparel: 95,
      game_entertainment: 88,
      sports_fitness: 80,
      travel_hotel: 88,
      education: 78,
      medical_healthcare: 72,
      telecom: 85,
      btob_services: 68,
      other: 78,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 63,
    name: "ローランド",
    maskedName: "◯◯◯◯◯",
    kana: "ろーらんど",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "実業家・インフルエンサー",
    age: 32,
    awarenessScore: 90,
    matchScore: 88,
    introduction: "カリスマ性のある実業家・インフルエンサー。",
    highlights: ["男性への訴求力", "高級感", "ビジネス展開"],
    instagram: "2.5M",
    youtube: "1.8M",
    twitter: "1.2M",
    tiktok: null,
    industries: ["化粧品・美容", "ファッション・アパレル", "金融・保険"],
    feeRange: "3000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 90,
      food_beverage: 82,
      automotive: 88,
      finance_insurance: 85,
      it_technology: 80,
      real_estate: 85,
      retail_ec: 85,
      fashion_apparel: 92,
      game_entertainment: 78,
      sports_fitness: 82,
      travel_hotel: 85,
      education: 75,
      medical_healthcare: 72,
      telecom: 80,
      btob_services: 78,
      other: 78,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 64,
    name: "中田敦彦",
    maskedName: "◯◯ ◯◯",
    kana: "なかた あつひこ",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuber・タレント",
    age: 42,
    awarenessScore: 94,
    matchScore: 92,
    introduction: "教育系YouTubeで人気のタレント。",
    highlights: ["全世代認知", "教育コンテンツ", "知的なイメージ"],
    instagram: "1.5M",
    youtube: "5.2M",
    twitter: "1.8M",
    tiktok: null,
    industries: ["教育", "IT・テクノロジー", "金融・保険"],
    feeRange: "4000万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 70,
      food_beverage: 82,
      automotive: 80,
      finance_insurance: 90,
      it_technology: 92,
      real_estate: 85,
      retail_ec: 80,
      fashion_apparel: 75,
      game_entertainment: 80,
      sports_fitness: 72,
      travel_hotel: 82,
      education: 98,
      medical_healthcare: 80,
      telecom: 88,
      btob_services: 85,
      other: 80,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
  {
    id: 65,
    name: "カジサック",
    maskedName: "◯◯◯◯◯",
    kana: "かじさっく",
    category: "インフルエンサー",
    categoryColor: "#FED7AA",
    title: "YouTuber・お笑い芸人",
    age: 49,
    awarenessScore: 91,
    matchScore: 89,
    introduction: "家族系YouTubeで人気のお笑い芸人。",
    highlights: ["ファミリー層への訴求力", "親しみやすさ", "幅広い年齢層"],
    instagram: "1.2M",
    youtube: "4.5M",
    twitter: "980K",
    tiktok: null,
    industries: ["食品・飲料", "教育", "小売・EC"],
    feeRange: "2500万円〜",
    imageUrl: "/placeholder.svg?height=400&width=400",
    industryFit: {
      beauty_cosmetics: 68,
      food_beverage: 92,
      automotive: 78,
      finance_insurance: 75,
      it_technology: 78,
      real_estate: 72,
      retail_ec: 88,
      fashion_apparel: 72,
      game_entertainment: 85,
      sports_fitness: 72,
      travel_hotel: 82,
      education: 90,
      medical_healthcare: 70,
      telecom: 80,
      btob_services: 68,
      other: 75,
    },
    cmHistory: [],
    currentUsageIndustries: [],
  },
]

export const middleTalents: Talent[] = []

export const highEndTalents: Talent[] = []

export const allTalents: Talent[] = [...premiumTalents, ...middleTalents, ...highEndTalents]
