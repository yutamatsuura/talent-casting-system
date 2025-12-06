/**
 * API Client Utility
 * FastAPI バックエンドとの通信を管理する
 */

import { FormData, TalentResult, TalentDetailInfo } from '@/types';

// 環境変数からAPIベースURL取得（開発時はlocalhost、本番はCloud Run）
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8432';

/**
 * マッチングAPIリクエスト型（フロントエンド → バックエンド型変換）
 */
interface MatchingApiRequest {
  industry: string;
  target_segments: string;
  purpose: string;
  budget: string;
  company_name: string;
  email: string;
  contact_name: string;
  phone: string;
  genre_preference?: string;
  preferred_genres?: string[];
}

/**
 * マッチングAPIレスポンス型（バックエンド仕様準拠）
 */
interface MatchingApiResponse {
  success: boolean;
  total_results: number;
  results: Array<{
    talent_id: number;
    account_id: number;
    name: string;
    kana?: string;
    category?: string;
    matching_score: number;
    ranking: number;
    base_power_score?: number;
    image_adjustment?: number;
    is_recommended: boolean;
    is_currently_in_cm: boolean; // 競合利用中フラグ
  }>;
  processing_time_ms?: number;
  timestamp: string;
  session_id?: string;
}

/**
 * エラーレスポンス型
 */
interface ApiErrorResponse {
  success: false;
  error_code: string;
  error_message: string;
  timestamp: string;
}

/**
 * FormData → MatchingApiRequest 型変換
 */
function transformFormDataToApiRequest(formData: FormData): MatchingApiRequest {
  // ターゲット層は単一の文字列として送信（「歳」付きでバックエンドが期待）
  const apiRequest: MatchingApiRequest = {
    industry: formData.q2,
    target_segments: formData.q3,
    purpose: formData.q3_2,
    budget: formData.q3_3,
    company_name: formData.q4,
    email: formData.q6,
    contact_name: formData.q5,
    phone: formData.q7,
  };

  // ジャンル情報を追加（オプション）
  if (formData.q7_2) {
    apiRequest.genre_preference = formData.q7_2;
  }
  if (formData.q7_2_genres && formData.q7_2_genres.length > 0) {
    apiRequest.preferred_genres = formData.q7_2_genres;
  }

  return apiRequest;
}

/**
 * POST /api/matching - 5段階マッチングロジック実行
 *
 * @param formData - フロントエンドフォームデータ
 * @returns 30件のタレント結果とsession_id
 * @throws API通信エラーまたはバリデーションエラー
 */
export async function callMatchingApi(formData: FormData): Promise<{ results: TalentResult[], sessionId?: string }> {
  const requestBody = transformFormDataToApiRequest(formData);

  // デバッグ情報（本番環境では無効化）
  if (process.env.NODE_ENV !== 'production') {
    console.log('Request URL:', `${API_BASE_URL}/api/matching`);
    console.log('Request Body:', JSON.stringify(requestBody, null, 2));
  }

  const response = await fetch(`${API_BASE_URL}/api/matching`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    // HTTPエラー処理 - デバッグ情報追加
    let errorText: string;
    try {
      const errorData = await response.json();
      if (process.env.NODE_ENV !== 'production') {
        console.error('API Error Response:', errorData);
      }

      if (errorData.error_message && errorData.error_code) {
        errorText = `API Error: ${errorData.error_message} (${errorData.error_code})`;
      } else {
        errorText = `API Error: ${response.status} ${response.statusText} - ${JSON.stringify(errorData)}`;
      }
    } catch (parseError) {
      const rawText = await response.text();
      if (process.env.NODE_ENV !== 'production') {
        console.error('Failed to parse error response:', rawText);
      }
      errorText = `API Error: ${response.status} ${response.statusText} - ${rawText}`;
    }

    throw new Error(errorText);
  }

  const data: MatchingApiResponse = await response.json();

  // レスポンスデバッグログ（本番環境では無効化）
  if (process.env.NODE_ENV !== 'production') {
    console.log('🔍 API Response received:', {
      success: data.success,
      total_results: data.total_results,
      first_talent: data.results[0] || null,
      cm_status_sample: data.results.slice(0, 3).map(t => ({
        name: t.name,
        is_currently_in_cm: t.is_currently_in_cm
      }))
    });
  }

  if (!data.success) {
    throw new Error('Matching API returned success: false');
  }

  // バックエンド型 → フロントエンド型変換
  const results = data.results.map((item) => ({
    account_id: item.account_id,
    name: item.name,
    kana: item.kana,
    category: item.category,
    matching_score: item.matching_score,
    ranking: item.ranking,
    base_power_score: item.base_power_score,
    image_adjustment: item.image_adjustment,
    is_recommended: item.is_recommended,
    is_currently_in_cm: item.is_currently_in_cm, // 競合利用中フラグを追加
    imageUrl: `/placeholder-user.jpg`, // TODO: 実際の画像URL実装
  }));

  return {
    results,
    sessionId: data.session_id
  };
}

/**
 * GET /api/health - ヘルスチェック
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
    });

    if (!response.ok) return false;

    const data = await response.json();
    return data.status === 'healthy' && data.database === 'connected';
  } catch (error) {
    if (process.env.NODE_ENV !== 'production') {
      console.error('Health check failed:', error);
    }
    return false;
  }
}

/**
 * GET /api/talents/{account_id}/details - タレント詳細情報取得
 */
export async function fetchTalentDetails(
  accountId: number,
  targetSegmentId?: number
): Promise<TalentDetailInfo> {
  try {
    // URLの構築
    let url = `${API_BASE_URL}/api/talents/${accountId}/details`;
    if (targetSegmentId) {
      url += `?target_segment_id=${targetSegmentId}`;
    }

    if (process.env.NODE_ENV !== 'production') {
      console.log('🔍 Fetching talent details:', { accountId, targetSegmentId, url });
    }

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    if (process.env.NODE_ENV !== 'production') {
      console.log('✅ Talent details received:', data);
    }

    // APIレスポンスをフロントエンド型に変換
    const talentDetail: TalentDetailInfo = {
      account_id: data.account_id,
      name: data.name,
      kana: data.kana,
      category: data.category,
      age: data.age,
      company_name: data.company_name,
      introduction: data.introduction,
      matching_score: data.matching_score || 0, // モーダル表示時は既存スコア使用
      ranking: data.ranking || 0, // モーダル表示時は既存ランキング使用
      cm_history: data.cm_history || [],
      base_power_score: data.base_power_score,
      image_adjustment: data.image_adjustment,
      imageUrl: data.image_url || '/placeholder-user.jpg'
    };

    return talentDetail;

  } catch (error) {
    if (process.env.NODE_ENV !== 'production') {
      console.error('❌ Failed to fetch talent details:', error);
    }
    throw new Error(`タレント詳細情報の取得に失敗しました: ${error instanceof Error ? error.message : String(error)}`);
  }
}
