'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import { ChevronLeft, ChevronRight, Home } from '@mui/icons-material';
import { FormData, STORAGE_KEY, TOTAL_FORM_STEPS, TalentResult } from '@/types';
import { FormStepTerms } from './FormSteps/FormStepTerms';
import { FormStep2 } from './FormSteps/FormStep2';
import { FormStep3 } from './FormSteps/FormStep3';
import { FormStep4 } from './FormSteps/FormStep4';
import { FormStep5 } from './FormSteps/FormStep5';
import { FormStep6 } from './FormSteps/FormStep6';
import { FormStep7 } from './FormSteps/FormStep7';
import { AnalysisLoadingScreen } from './shared/AnalysisLoadingScreen';
import { ResultsPage } from './Results/ResultsPage';
import { callMatchingApi } from '@/lib/api';

const initialFormData: FormData = {
  termsAgreed: false,
  q2: '',
  q3: '',
  q3_2: [],
  q3_3: '',
  q4: '',
  q5: '',
  q6: '',
  q7: '',
  q7_2: '',
  q7_2_genres: [],
  privacyAgreed: false,
};

const stepLabels = [
  '利用規約',
  '業界選択',
  '訴求対象',
  '起用目的',
  '予算設定',
  '企業情報入力',
  'プライバシーポリシー',
];

export function TalentCastingForm() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showResults, setShowResults] = useState(false);
  const [showLoading, setShowLoading] = useState(false);
  const [apiResults, setApiResults] = useState<TalentResult[]>([]);
  const [apiError, setApiError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);

  // ページ離脱時にセッションデータをクリア
  useEffect(() => {
    const handleBeforeUnload = () => {
      // ページ離脱時（タブを閉じる、ブラウザを閉じる、別ページへ移動など）にデータをクリア
      localStorage.removeItem(STORAGE_KEY);
      sessionStorage.removeItem('talentResults');
      sessionStorage.removeItem('talentFormData');
      sessionStorage.removeItem('talentApiError');
      sessionStorage.removeItem('talentSessionId');

      if (process.env.NODE_ENV !== 'production') {
        console.log('🧹 ページ離脱時にセッションデータをクリアしました');
      }
    };

    const handleVisibilityChange = () => {
      // ページがバックグラウンドになった時もクリア（別タブに移動など）
      if (document.visibilityState === 'hidden') {
        localStorage.removeItem(STORAGE_KEY);
        sessionStorage.removeItem('talentResults');
        sessionStorage.removeItem('talentFormData');
        sessionStorage.removeItem('talentApiError');
        sessionStorage.removeItem('talentSessionId');

        if (process.env.NODE_ENV !== 'production') {
          console.log('🧹 ページがバックグラウンドになったためセッションデータをクリアしました');
        }
      }
    };

    // イベントリスナー追加
    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // 初期化時は既存データをクリア（常に最初からスタート）
    localStorage.removeItem(STORAGE_KEY);
    sessionStorage.removeItem('talentResults');
    sessionStorage.removeItem('talentFormData');
    sessionStorage.removeItem('talentApiError');
    sessionStorage.removeItem('talentSessionId');

    if (process.env.NODE_ENV !== 'production') {
      console.log('🔄 診断フォームを初期化しました（常に最初からスタート）');
    }

    // クリーンアップ
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  // セッション内でのステップ進行管理（メモリのみ、LocalStorage使用なし）
  useEffect(() => {
    // 現在のセッション中はメモリ上でのみ状態を保持
    // LocalStorageには保存しない
    if (process.env.NODE_ENV !== 'production') {
      console.log('📊 セッション内進行状況:', { currentStep, formDataKeys: Object.keys(formData) });
    }
  }, [formData, currentStep]);

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (step === 1) {
      if (!formData.termsAgreed) {
        newErrors.termsAgreed = '利用規約への同意が必要です';
      }
    }

    if (step === 2) {
      if (!formData.q2) newErrors.q2 = '業界を選択してください';
    }

    if (step === 3) {
      if (!formData.q3 || formData.q3.trim() === '') {
        newErrors.q3 = '訴求対象を1つ選択してください';
      }
    }

    if (step === 4) {
      if (!formData.q3_2 || formData.q3_2.length === 0) {
        newErrors.q3_2 = '目的を1つ以上選択してください';
      }
    }

    if (step === 5) {
      if (!formData.q3_3) newErrors.q3_3 = '予算を選択してください';
    }

    if (step === 6) {
      if (!formData.q4) newErrors.q4 = '会社名を入力してください';
      if (!formData.q5) newErrors.q5 = '担当者名を入力してください';
      if (!formData.q6) newErrors.q6 = 'メールアドレスを入力してください';
      if (!formData.q7) newErrors.q7 = '携帯電話番号を入力してください';
      if (formData.q6 && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.q6)) {
        newErrors.q6 = '有効なメールアドレスを入力してください';
      }

      // 電話番号の形式チェック（日本の携帯電話番号形式）
      if (formData.q7 && !/^(090|080|070)-?\d{4}-?\d{4}$/.test(formData.q7.replace(/-/g, ''))) {
        newErrors.q7 = '有効な携帯電話番号を入力してください（例：090-1234-5678）';
      }

      // ジャンル希望の必須チェック
      if (!formData.q7_2) {
        newErrors.q7_2 = 'タレントジャンルの希望有無を選択してください';
      }

      // ジャンル具体選択の整合性チェック
      if (formData.q7_2 === '希望ジャンルあり' && (!Array.isArray(formData.q7_2_genres) || formData.q7_2_genres.length === 0)) {
        newErrors.q7_2_genres = '希望ジャンルを選択するか、「希望ジャンルなし」を選択してください';
      }
    }

    if (step === 7) {
      if (!formData.privacyAgreed) {
        newErrors.privacyAgreed = 'プライバシーポリシーへの同意が必要です';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = async () => {
    if (process.env.NODE_ENV !== 'production') {
      console.log('🔘 handleNext呼び出し - currentStep:', currentStep);
    }

    if (validateStep(currentStep)) {
      if (currentStep < TOTAL_FORM_STEPS) {
        setCurrentStep(currentStep + 1);
        // ページトップにスムーズにスクロール
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        if (process.env.NODE_ENV !== 'production') {
          console.log('🚀 診断処理開始 - 最終ステップ');
          console.log('🔄 setShowLoading(true) を実行します');
        }

        // POST /api/matching - 実APIを呼び出してマッチング処理実行
        setShowLoading(true);
        setApiError(null);

        if (process.env.NODE_ENV !== 'production') {
          console.log('🔄 showLoading状態をtrueに設定完了');
        }

        try {
          if (process.env.NODE_ENV !== 'production') {
            console.log('🔄 診断API呼び出し開始:', formData);
          }
          const response = await callMatchingApi(formData);
          if (process.env.NODE_ENV !== 'production') {
            console.log('✅ 診断API呼び出し成功:', response);
          }

          // 結果データをSessionStorageに保存
          sessionStorage.setItem('talentResults', JSON.stringify(response.results));
          sessionStorage.setItem('talentFormData', JSON.stringify(formData));
          sessionStorage.setItem('talentApiError', JSON.stringify(null));
          sessionStorage.setItem('talentSessionId', response.sessionId || '');

          if (process.env.NODE_ENV !== 'production') {
            console.log('💾 SessionStorage保存完了:', {
              resultsLength: response.results.length,
              formData: formData,
              sessionId: response.sessionId
            });

            // SessionStorageに保存されているか確認
            const storedResults = sessionStorage.getItem('talentResults');
            const storedFormData = sessionStorage.getItem('talentFormData');
            console.log('🔍 SessionStorage検証:', {
              storedResults: storedResults ? JSON.parse(storedResults).length : 'なし',
              storedFormData: storedFormData ? 'あり' : 'なし'
            });
          }

          // FormDataをLP側が期待する形式に変換
          const transformedFormData = {
            industry: formData.q2,
            target_segments: formData.q3,
            purpose: formData.q3_2, // 配列で送信
            budget: formData.q3_3,
            company_name: formData.q4,
            contact_name: formData.q5,
            email: formData.q6,
            phone: formData.q7,
            genre_preference: formData.q7_2,
            preferred_genres: formData.q7_2_genres,
            privacyAgreed: formData.privacyAgreed
          };

          // iframe通信で親ページに結果完了を通知（LPとの統合対応）
          const message = {
            type: 'diagnosis_complete',
            data: {
              success: true,
              resultCount: response.results.length,
              results: response.results,
              formData: transformedFormData,
              apiError: null,
              sessionId: response.sessionId
            }
          };
          if (process.env.NODE_ENV !== 'production') {
            console.log('📡 親ページに通知送信（変換済みデータ付き）:', message);
          }
          window.parent.postMessage(message, '*');

          setApiResults(response.results);
          setSessionId(response.sessionId);
          if (process.env.NODE_ENV !== 'production') {
            console.log('🎯 SessionStorageに保存完了、結果ページに遷移します');
          }

          // 結果ページに遷移
          router.push('/results');
        } catch (error) {
          if (process.env.NODE_ENV !== 'production') {
            console.error('🚨 診断API呼び出しエラー:', error);
          }

          const errorMessage = error instanceof Error
            ? error.message
            : '予期しないエラーが発生しました。しばらく後にお試しください。';

          if (process.env.NODE_ENV !== 'production') {
            console.log('💥 エラーメッセージ:', errorMessage);
          }

          // エラー情報もSessionStorageに保存
          sessionStorage.setItem('talentResults', JSON.stringify([]));
          sessionStorage.setItem('talentFormData', JSON.stringify(formData));
          sessionStorage.setItem('talentApiError', JSON.stringify(errorMessage));
          if (process.env.NODE_ENV !== 'production') {
            console.log('💾 エラー情報をSessionStorageに保存');
          }

          // FormDataをLP側が期待する形式に変換（エラー時も同様）
          const transformedFormDataError = {
            industry: formData.q2,
            target_segments: formData.q3,
            purpose: formData.q3_2,
            budget: formData.q3_3,
            company_name: formData.q4,
            contact_name: formData.q5,
            email: formData.q6,
            phone: formData.q7,
            genre_preference: formData.q7_2,
            preferred_genres: formData.q7_2_genres,
            privacyAgreed: formData.privacyAgreed
          };

          // iframe通信で親ページにエラーを通知（変換済みデータも一緒に送信）
          const errorNotification = {
            type: 'DIAGNOSIS_RESULTS_READY',
            payload: {
              success: false,
              error: errorMessage,
              results: [],
              formData: transformedFormDataError,
              apiError: errorMessage
            }
          };
          if (process.env.NODE_ENV !== 'production') {
            console.log('📡 エラー通知を親ページに送信（変換済みデータ付き）:', errorNotification);
          }
          window.parent.postMessage(errorNotification, '*');

          setApiError(errorMessage);
          if (process.env.NODE_ENV !== 'production') {
            console.log('🎯 エラー情報保存完了、結果ページに遷移します');
          }

          // エラー時も結果ページに遷移
          router.push('/results');
        } finally {
          setShowLoading(false);
        }
      }
    }
  };

  const handleBack = () => {
    setCurrentStep(Math.max(1, currentStep - 1));
    // ページトップにスムーズにスクロール
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleReset = () => {
    setFormData(initialFormData);
    setCurrentStep(1);
    setShowResults(false);
    setShowLoading(false);
    setErrors({});
    setApiResults([]);
    setApiError(null);

    // セッションデータもクリア
    sessionStorage.removeItem('talentResults');
    sessionStorage.removeItem('talentFormData');
    sessionStorage.removeItem('talentApiError');
    sessionStorage.removeItem('talentSessionId');

    if (process.env.NODE_ENV !== 'production') {
      console.log('🔄 フォームをリセットしました');
    }

    // ページトップにスムーズにスクロール
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const progress = (currentStep / TOTAL_FORM_STEPS) * 100;

  if (showLoading) {
    if (process.env.NODE_ENV !== 'production') {
      console.log('🔄 AnalysisLoadingScreen を表示中');
    }
    return (
      <AnalysisLoadingScreen
        onComplete={() => {
          // onCompleteは使用しない（API完了を待つため）
          if (process.env.NODE_ENV !== 'production') {
            console.log('⚠️ onComplete が呼ばれましたが、無視します（API完了を待機中）');
          }
        }}
      />
    );
  }

  if (showResults) {
    return (
      <Box sx={{
        maxWidth: '600px',
        mx: 'auto',
        px: 2,
        py: 8,
        textAlign: 'center'
      }}>
        <Typography variant="h5" fontWeight="bold" gutterBottom>
          診断結果を準備中...
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          結果ページに移動します
        </Typography>

        {/* フォールバック：3秒後に手動で遷移を促す */}
        <Typography variant="body2" color="text.secondary">
          自動で移動しない場合は、
          <Button
            variant="text"
            onClick={() => window.parent.postMessage({
              type: 'DIAGNOSIS_RESULTS_READY',
              payload: { success: true, resultCount: apiResults.length }
            }, '*')}
            sx={{ mx: 1 }}
          >
            こちらをクリック
          </Button>
          してください
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: '600px', mx: 'auto', px: { xs: 0, sm: 2 }, pt: 1, pb: { xs: 10, sm: 3, md: 1.5 } }}>

      {/* シンプルなヘッダー */}
      <Box sx={{ mb: 1, textAlign: 'center' }}>
        {/* プログレスバー */}
        <LinearProgress
          variant="determinate"
          value={progress}
          sx={{
            height: 8,
            borderRadius: 4,
            bgcolor: 'grey.200',
            mb: 0.8,
            '& .MuiLinearProgress-bar': {
              borderRadius: 4,
              background: 'linear-gradient(90deg, #3b82f6 0%, #a855f7 100%) !important',
            },
          }}
        />

        {/* 質問番号 */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          質問 {currentStep} / {TOTAL_FORM_STEPS}
        </Typography>

        {/* タイトル */}
        <Typography variant="h3" fontWeight="bold" color="#333">
          タレントキャスティング診断
        </Typography>
      </Box>

      {/* フォームカード */}
      <Card elevation={3}>
        <CardContent sx={{ minHeight: '500px', display: 'flex', flexDirection: 'column' }}>
          {currentStep === 1 && (
            <FormStepTerms formData={formData} setFormData={setFormData} errors={errors} />
          )}
          {currentStep === 2 && (
            <FormStep2 formData={formData} setFormData={setFormData} errors={errors} />
          )}
          {currentStep === 3 && (
            <FormStep3 formData={formData} setFormData={setFormData} errors={errors} />
          )}
          {currentStep === 4 && (
            <FormStep4 formData={formData} setFormData={setFormData} errors={errors} />
          )}
          {currentStep === 5 && (
            <FormStep5 formData={formData} setFormData={setFormData} errors={errors} />
          )}
          {currentStep === 6 && (
            <FormStep6 formData={formData} setFormData={setFormData} errors={errors} />
          )}
          {currentStep === 7 && (
            <FormStep7 formData={formData} setFormData={setFormData} errors={errors} />
          )}
        </CardContent>

        {/* ナビゲーションボタン */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            p: 2,
            pb: { xs: 10, sm: 4 },
            borderTop: 1,
            borderColor: 'divider',
          }}
        >
          <Button
            variant="outlined"
            startIcon={currentStep === 1 ? <Home /> : <ChevronLeft />}
            onClick={currentStep === 1 ? handleReset : handleBack}
          >
            {currentStep === 1 ? 'リセット' : '戻る'}
          </Button>
          <Button
            variant="contained"
            endIcon={<ChevronRight />}
            onClick={handleNext}
            sx={{
              background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
            }}
          >
            {currentStep === TOTAL_FORM_STEPS ? '診断開始' : '次へ'}
          </Button>
        </Box>
      </Card>
    </Box>
  );
}
