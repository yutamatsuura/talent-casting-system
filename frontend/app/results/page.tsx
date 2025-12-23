'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PublicLayout } from '@/layouts/PublicLayout';
import { ResultsPage } from '@/components/diagnosis/Results/ResultsPage';
import { FormData, TalentResult } from '@/types';
import { Box, Typography, Button, Alert } from '@mui/material';
import { Home, Refresh } from '@mui/icons-material';

export default function ResultsStandalonePage() {
  const router = useRouter();
  const [formData, setFormData] = useState<FormData | null>(null);
  const [apiResults, setApiResults] = useState<TalentResult[]>([]);
  const [apiError, setApiError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  // ページ離脱時にセッションデータをクリア
  useEffect(() => {
    const handleBeforeUnload = () => {
      // ページ離脱時（タブを閉じる、ブラウザを閉じる、別ページへ移動など）にデータをクリア
      sessionStorage.removeItem('talentResults');
      sessionStorage.removeItem('talentFormData');
      sessionStorage.removeItem('talentApiError');
      sessionStorage.removeItem('talentSessionId');

      console.log('🧹 結果ページ離脱時にセッションデータをクリアしました');
    };

    const handleVisibilityChange = () => {
      // ページがバックグラウンドになった時もクリア（別タブに移動など）
      if (document.visibilityState === 'hidden') {
        sessionStorage.removeItem('talentResults');
        sessionStorage.removeItem('talentFormData');
        sessionStorage.removeItem('talentApiError');
        sessionStorage.removeItem('talentSessionId');

        console.log('🧹 結果ページがバックグラウンドになったためセッションデータをクリアしました');
      }
    };

    // イベントリスナー追加
    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // クリーンアップ
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  useEffect(() => {
    console.log('🔍 結果ページ: URLパラメータからデータ読み込み開始');

    try {
      // URLからエンコードされたデータを取得
      const urlParams = new URLSearchParams(window.location.search);
      const encodedData = urlParams.get('data');

      console.log('📦 受信したエンコードデータ:', encodedData ? `${encodedData.length}文字` : 'null');

      if (!encodedData) {
        // エンコードデータがない場合は従来のSessionStorage方式を試す
        console.log('⚠️ URLパラメータなし、SessionStorageを確認');
        const storedResults = sessionStorage.getItem('talentResults');
        const storedFormData = sessionStorage.getItem('talentFormData');
        const storedApiError = sessionStorage.getItem('talentApiError');
        const storedSessionId = sessionStorage.getItem('talentSessionId');

        if (!storedResults || !storedFormData) {
          console.log('❌ URLパラメータもSessionStorageデータも存在しません');
          setHasError(true);
          setIsLoading(false);
          return;
        }

        // SessionStorageからのデータ処理（従来通り）
        const results: TalentResult[] = JSON.parse(storedResults);
        const formDataParsed: FormData = JSON.parse(storedFormData);
        const errorParsed: string | null = storedApiError ? JSON.parse(storedApiError) : null;
        const sessionIdParsed: string | undefined = storedSessionId || undefined;

        setApiResults(results);
        setFormData(formDataParsed);
        setApiError(errorParsed);
        setSessionId(sessionIdParsed);
        setIsLoading(false);
        console.log('✅ SessionStorageからデータ読み込み成功');
        return;
      }

      // URLデコードとJSONパース（Base64は使用しない）
      console.log('🔓 URLエンコードされたデータをデコード中...');
      const decodedJsonString = decodeURIComponent(encodedData);
      const parsedData = JSON.parse(decodedJsonString);

      // 圧縮データ形式をチェック（新形式は r, f, e キーを使用）
      if (parsedData.r && parsedData.f) {
        console.log('📦 圧縮データ形式を検出、展開中...');

        // 圧縮データを元の形式に展開
        const results: TalentResult[] = parsedData.r.map((t: any) => ({
          account_id: t.i,
          name: t.n,
          kana: t.k,
          category: t.c,
          company_name: t.cn, // 事務所名を追加
          matching_score: t.s,
          ranking: t.rk,
          base_power_score: 0,
          image_adjustment: 0,
          is_recommended: t.rk <= 3,
          is_currently_in_cm: false
        }));

        const formDataParsed: FormData = {
          q2: parsedData.f.i,  // 業界選択（必須）
          q3: parsedData.f.t,  // ターゲット層選択（必須、単一選択）
          q3_2: parsedData.f.p, // タレント起用理由（必須）
          q3_3: parsedData.f.b, // 予算区分（必須）
          q4: parsedData.f.cn,  // 会社名（必須）
          q5: '',              // 担当者名（圧縮対象外）
          q6: '',              // メールアドレス（圧縮対象外）
          q7: '',              // 携帯電話番号（圧縮対象外）
          q7_2: '',            // 希望ジャンル選択（圧縮対象外）
          q7_2_genres: [],     // 具体的ジャンル選択（圧縮対象外）
          privacyAgreed: true  // プライバシー同意（圧縮対象外）
        };

        const errorParsed: string | null = parsedData.e || null;

        console.log('🔍 圧縮データ詳細確認:', {
          fullParsedData: parsedData,
          fData: parsedData.f,
          fKeys: parsedData.f ? Object.keys(parsedData.f) : 'undefined'
        });

        console.log('✅ 圧縮データ展開完了:', {
          resultsCount: results.length,
          formDataKeys: Object.keys(formDataParsed),
          hasError: !!errorParsed
        });

        // ステートに設定
        setApiResults(results);
        setFormData(formDataParsed);
        setApiError(errorParsed);
        setIsLoading(false);
        console.log('🎯 結果ページ: 圧縮データ設定完了');

      } else {
        // 従来の非圧縮形式（下位互換）
        console.log('📦 従来データ形式を検出');
        const results: TalentResult[] = parsedData.results;
        const formDataParsed: FormData = parsedData.formData;
        const errorParsed: string | null = parsedData.apiError;

        console.log('✅ 従来データパース成功:', {
          resultsCount: results.length,
          formDataKeys: Object.keys(formDataParsed),
          hasError: !!errorParsed
        });

        // ステートに設定
        setApiResults(results);
        setFormData(formDataParsed);
        setApiError(errorParsed);
        setIsLoading(false);
        console.log('🎯 結果ページ: 従来データ設定完了');
      }

      // URLからパラメータを削除（セキュリティ）
      window.history.replaceState({}, '', window.location.pathname);
      console.log('🗑️ URLパラメータを削除');

    } catch (error) {
      console.error('❌ データデコード・読み込み失敗:', error);
      setHasError(true);
      setIsLoading(false);
    }
  }, []);

  const handleReset = () => {
    console.log('🔄 診断リセット開始');

    // 完全なデータクリア（ブラウザの全てのストレージをクリア）
    try {
      // SessionStorage完全クリア
      sessionStorage.clear();

      // LocalStorage内の診断関連データクリア
      const keysToRemove = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.includes('talent') || key.includes('diagnosis') || key.includes('form'))) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(key => localStorage.removeItem(key));

      console.log('✅ 全データクリア完了');
    } catch (error) {
      console.error('⚠️ データクリア時にエラー:', error);
    }

    // iframe内で実行されているかチェック
    const isInIframe = window.self !== window.top;

    if (isInIframe) {
      // iframeの場合：親ウィンドウにリセット要求を送信
      console.log('📤 iframe内検出: 親ウィンドウにリセット要求送信');
      try {
        window.parent.postMessage({
          type: 'diagnosis_reset',
          data: {
            action: 'clear_and_reload',
            timestamp: new Date().getTime()
          }
        }, '*');

        // メッセージ送信後、少し待ってからフォールバック
        setTimeout(() => {
          console.log('⏱️ タイムアウト: フォールバック処理実行');
          performCompleteReset();
        }, 3000);

      } catch (error) {
        console.error('❌ postMessage送信エラー:', error);
        performCompleteReset();
      }
    } else {
      // スタンドアロン表示の場合：直接リセット実行
      console.log('🖥️ スタンドアロン検出: 直接リセット実行');
      performCompleteReset();
    }
  };

  // 完全リセット実行関数
  const performCompleteReset = () => {
    console.log('🔄 完全リセット実行中...');

    // URLにリセットフラグを追加してランディングページに遷移
    const resetUrl = 'https://e-spirit.vercel.app/?reset=true&timestamp=' + new Date().getTime();
    console.log('🏠 リセット状態でランディングページに遷移:', resetUrl);

    // 強制的にページをリロード
    window.location.replace(resetUrl);
  };

  const handleBackToLanding = () => {
    // ランディングページに戻る
    window.location.href = 'https://e-spirit.vercel.app/';
  };

  if (isLoading) {
    return (
      <PublicLayout maxWidth="md" showHeader={false}>
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6">診断結果を読み込んでいます...</Typography>
        </Box>
      </PublicLayout>
    );
  }

  if (hasError || !formData) {
    return (
      <PublicLayout maxWidth="md" showHeader={false}>
        <Box sx={{ py: 4 }}>
          <Alert severity="warning" sx={{ mb: 4 }}>
            <Typography variant="body1" fontWeight="bold" gutterBottom>
              診断結果が見つかりません
            </Typography>
            <Typography variant="body2">
              診断を実行してから結果ページにアクセスしてください。
            </Typography>
          </Alert>

          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<Home />}
              onClick={handleBackToLanding}
              sx={{
                py: 2,
                px: 4,
                fontSize: '1.1rem',
                background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(90deg, #5a6fd8 0%, #6a4190 100%)',
                },
              }}
            >
              診断を開始する
            </Button>
          </Box>
        </Box>
      </PublicLayout>
    );
  }

  // 正常に結果がある場合は、既存のResultsPageコンポーネントをそのまま使用
  return (
    <PublicLayout maxWidth="lg" showHeader={false}>
      <ResultsPage
        formData={formData}
        onReset={handleReset}
        apiResults={apiResults}
        apiError={apiError}
        sessionId={sessionId}
      />
    </PublicLayout>
  );
}