'use client';

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  LinearProgress,
  Button,
  Box,
  Stack,
} from '@mui/material';
import { ChevronLeft, ChevronRight } from '@mui/icons-material';
import { FormData, FormValidationErrors } from '@/types';

/**
 * タレントキャスティング診断 メインページ
 * 6段階フォーム → 結果表示
 * 既存mockups-v0のロジックをMUIで再実装
 */

const STORAGE_KEY = 'talent-casting-form-data';

// 初期データの取得
const getInitialData = () => {
  if (typeof window === 'undefined') return { formData: {
    q2: '',
    q3: [],
    q3_2: '',
    q3_3: '',
    q4: '',
    q5: '',
    q6: '',
    q7: '',
    privacyAgreed: false,
  }, currentStep: 1 };

  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      return {
        formData: {
          ...parsed,
          q3: Array.isArray(parsed.q3) ? parsed.q3 : [],
          privacyAgreed: false, // セキュリティのため毎回リセット
        },
        currentStep: parsed.currentStep || 1
      };
    } catch (error) {
      console.warn('Failed to parse saved data:', error);
    }
  }
  return {
    formData: {
      q2: '',
      q3: [],
      q3_2: [],
      q3_3: '',
      q4: '',
      q5: '',
      q6: '',
      q7: '',
      privacyAgreed: false,
    },
    currentStep: 1
  };
};

export function DiagnosisSystemPage() {
  const initialData = getInitialData();
  const [currentStep, setCurrentStep] = useState(initialData.currentStep);
  const [formData, setFormData] = useState<FormData>(initialData.formData);
  const [errors, setErrors] = useState<FormValidationErrors>({});
  const [showResults, setShowResults] = useState(false);

  const totalSteps = 6;

  // ローカルストレージへの保存
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ formData, currentStep }));
  }, [formData, currentStep]);

  // バリデーション
  const validateStep = (step: number): boolean => {
    const newErrors: FormValidationErrors = {};

    if (step === 1 && !formData.q2) newErrors.q2 = '業界を選択してください';
    if (step === 2 && formData.q3.length === 0) newErrors.q3 = '少なくとも1つのターゲット層を選択してください';
    if (step === 3 && !formData.q3_2) newErrors.q3_2 = '理由を選択してください';
    if (step === 4 && !formData.q3_3) newErrors.q3_3 = '予算を選択してください';

    if (step === 5) {
      if (!formData.q4) newErrors.q4 = '会社名を入力してください';
      if (!formData.q5) newErrors.q5 = 'お名前を入力してください';
      if (!formData.q6) newErrors.q6 = 'メールアドレスを入力してください';
      if (!formData.q7) newErrors.q7 = '電話番号を入力してください';
      if (formData.q6 && !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(formData.q6)) {
        newErrors.q6 = '有効なメールアドレスを入力してください';
      }
    }

    if (step === 6 && !formData.privacyAgreed) {
      newErrors.privacyAgreed = 'プライバシーポリシーへの同意が必要です';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 次へ
  const handleNext = () => {
    if (validateStep(currentStep)) {
      if (currentStep < totalSteps) {
        setCurrentStep(currentStep + 1);
      } else {
        // 診断実行
        setShowResults(true);
      }
    }
  };

  // 戻る
  const handleBack = () => {
    setCurrentStep(Math.max(1, currentStep - 1));
  };

  // やり直し
  const handleReset = () => {
    setFormData({
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
    });
    setCurrentStep(1);
    setShowResults(false);
    setErrors({});
    localStorage.removeItem(STORAGE_KEY);
  };

  const progress = (currentStep / totalSteps) * 100;

  if (showResults) {
    return (
      <Card sx={{ maxWidth: 'md', mx: 'auto' }}>
        <CardHeader>
          <Typography variant="h4" component="h1" textAlign="center">
            診断結果
          </Typography>
        </CardHeader>
        <CardContent>
          <Box textAlign="center" sx={{ '& > *': { mb: 3 } }}>
            <Typography variant="h5" color="primary" gutterBottom>
              🎯 マッチングスコア: 98.5点
            </Typography>
            <Typography variant="body1" sx={{ mb: 3 }}>
              {formData.q4 || '貴社'}様に最適なタレントが見つかりました！
            </Typography>
            <Stack spacing={2} direction={{ xs: 'column', sm: 'row' }} justifyContent="center">
              <Button variant="contained" size="large">
                詳細結果を見る
              </Button>
              <Button variant="outlined" onClick={handleReset}>
                最初からやり直す
              </Button>
            </Stack>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ maxWidth: 'lg', mx: 'auto' }}>
      <CardHeader>
        <Box sx={{ mb: 2 }}>
          <LinearProgress variant="determinate" value={progress} sx={{ mb: 1 }} />
          <Typography variant="body2" color="textSecondary" textAlign="center">
            質問 {currentStep} / {totalSteps}
          </Typography>
        </Box>
        <Typography variant="h4" component="h1" textAlign="center">
          タレントキャスティング診断
        </Typography>
      </CardHeader>

      <CardContent sx={{ minHeight: '400px' }}>
        {/* フォームステップの内容はここに実装 */}
        {currentStep === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              貴社の業界は次のうちどれにあてはまりますか？
            </Typography>
            {/* 業界選択フォーム - 次回実装 */}
            <Typography color="primary">
              🚧 業界選択フォーム（次回実装予定）
            </Typography>
            {errors.q2 && (
              <Typography color="error" variant="body2" sx={{ mt: 1 }}>
                {errors.q2}
              </Typography>
            )}
          </Box>
        )}

        {currentStep === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              貴社の商品サービスの主要なターゲットはどの層ですか？
            </Typography>
            {/* ターゲット層選択フォーム - 次回実装 */}
            <Typography color="primary">
              🚧 ターゲット層選択フォーム（次回実装予定）
            </Typography>
          </Box>
        )}

        {/* Steps 3-6 - 次回実装 */}
        {currentStep >= 3 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              ステップ {currentStep}
            </Typography>
            <Typography color="primary">
              🚧 フォーム内容（次回実装予定）
            </Typography>
          </Box>
        )}
      </CardContent>

      {/* ナビゲーションボタン */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', p: 3 }}>
        <Button
          variant="outlined"
          startIcon={<ChevronLeft />}
          onClick={handleBack}
          disabled={currentStep === 1}
        >
          戻る
        </Button>
        <Button
          variant="contained"
          endIcon={currentStep === totalSteps ? undefined : <ChevronRight />}
          onClick={handleNext}
        >
          {currentStep === totalSteps ? '結果を見る' : '次へ'}
        </Button>
      </Box>
    </Card>
  );
}