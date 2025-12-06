/**
 * CMカテゴリIDから業界名へのマッピング機能
 * データベース分析結果に基づいて作成
 */

// カテゴリIDマッピング（データベース分析結果）
export const CATEGORY_MAPPING: Record<number, string> = {
  1: '食品',
  2: '菓子・氷菓',
  3: '乳製品',
  4: 'フードサービス',
  5: 'アルコール飲料',
  6: '清涼飲料水',
  7: 'サプリメント',
  8: '医薬品・医療',
  9: '化粧品・美容',
  10: 'ヘアケア',
  11: 'オーラルケア',
  12: 'トイレタリー',
  13: '自動車',
  14: '家電',
  15: '通信・IT',
  16: 'ソフトウェア',
  17: 'ゲーム・エンタメ',
  18: 'スポーツ・娯楽',
  19: 'エンターテイメント',
  20: '趣味',
  21: 'ファッション',
  22: '貴金属・ジュエリー',
  23: '金融・保険',
  24: 'エネルギー',
  25: '不動産',
  26: 'リース・レンタル',
  27: '出版・メディア',
  28: '公共・行政',
  29: '教育',
  30: 'アイスクリーム',
  31: '住宅設備',
  32: 'アプリ・サービス',
  33: '交通・輸送',
  34: '観光・旅行',
  35: 'ホテル・宿泊',
  98: 'その他サービス',
  99: 'その他'
};

/**
 * カテゴリIDからカテゴリ名を取得
 * @param categoryId カテゴリID
 * @returns カテゴリ名（見つからない場合はnull）
 */
export function getCategoryName(categoryId: number | null | undefined): string | null {
  if (!categoryId || categoryId === 0) {
    return null;
  }

  return CATEGORY_MAPPING[categoryId] || null;
}

/**
 * カテゴリIDからラベル用の色を取得
 * @param categoryId カテゴリID
 * @returns Material-UIのカラー名
 */
export function getCategoryColor(categoryId: number | null | undefined): 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' | 'default' {
  if (!categoryId) {
    return 'default';
  }

  // カテゴリ系統別に色分け
  if (categoryId >= 1 && categoryId <= 6) {
    // 食品・飲料系
    return 'success';
  } else if (categoryId >= 8 && categoryId <= 12) {
    // ヘルスケア・美容系
    return 'info';
  } else if (categoryId >= 13 && categoryId <= 17) {
    // 工業・IT系
    return 'primary';
  } else if (categoryId >= 21 && categoryId <= 25) {
    // 消費財・金融系
    return 'warning';
  } else if (categoryId >= 28 && categoryId <= 35) {
    // サービス・公共系
    return 'secondary';
  } else {
    // その他
    return 'default';
  }
}

/**
 * 複数のカテゴリIDから主要カテゴリを取得
 * @param categories カテゴリIDの配列
 * @returns 主要カテゴリ名（見つからない場合はnull）
 */
export function getPrimaryCategoryName(categories: (number | null)[]): string | null {
  const validCategories = categories.filter((cat): cat is number => cat !== null && cat !== undefined && cat !== 0);

  if (validCategories.length === 0) {
    return null;
  }

  // 最初のカテゴリを主要カテゴリとする
  return getCategoryName(validCategories[0]);
}

/**
 * CMの全カテゴリを取得（最大4つ）
 * @param cd1 カテゴリ1
 * @param cd2 カテゴリ2
 * @param cd3 カテゴリ3
 * @param cd4 カテゴリ4
 * @returns カテゴリ名の配列（有効なカテゴリのみ）
 */
export function getAllCategoryNames(
  cd1?: number | null,
  cd2?: number | null,
  cd3?: number | null,
  cd4?: number | null
): string[] {
  const categories = [cd1, cd2, cd3, cd4];
  return categories
    .filter((cat): cat is number => cat !== null && cat !== undefined && cat !== 0)
    .map(getCategoryName)
    .filter((name): name is string => name !== null);
}