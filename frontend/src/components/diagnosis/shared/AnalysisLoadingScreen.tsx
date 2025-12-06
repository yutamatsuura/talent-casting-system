'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Fade,
  CircularProgress,
} from '@mui/material';
import {
  Search,
  BarChart,
  CheckCircle,
  Circle,
  AutoAwesome,
} from '@mui/icons-material';

type AnalysisStep = {
  id: number;
  title: string;
  description: string;
  duration: number;
  processingText: string;
  maxCount: number;
};

const steps: AnalysisStep[] = [
  {
    id: 1,
    title: '業界データベース検索',
    description: '2,500件のタレントデータを分析',
    duration: 1500,
    processingText: '処理中',
    maxCount: 2500,
  },
  {
    id: 2,
    title: 'ターゲット層マッチング',
    description: 'F1・F2層データとのクロス分析',
    duration: 1000,
    processingText: '処理中',
    maxCount: 20,
  },
  {
    id: 3,
    title: 'CM出演実績の照合',
    description: '過去5年間のCMデータを検証',
    duration: 2000,
    processingText: '処理中',
    maxCount: 3500,
  },
  {
    id: 4,
    title: '起用コスト最適化',
    description: '予算シミュレーション実行',
    duration: 1000,
    processingText: '最適プランを計算中...',
    maxCount: 100,
  },
  {
    id: 5,
    title: '競合起用状況チェック',
    description: '最新の契約状況を確認',
    duration: 1000,
    processingText: 'バッティング確認中...',
    maxCount: 100,
  },
  {
    id: 6,
    title: '総合スコア算出',
    description: 'マッチング精度を計算',
    duration: 1000,
    processingText: 'スコアリング中...',
    maxCount: 100,
  },
];

export function AnalysisLoadingScreen({ onComplete }: { onComplete: () => void }) {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);

  console.log('🔄 AnalysisLoadingScreen コンポーネント開始');

  useEffect(() => {
    const totalDuration = steps.reduce((sum, step) => sum + step.duration, 0);
    let elapsed = 0;

    const interval = setInterval(() => {
      elapsed += 50;
      const newProgress = Math.min((elapsed / totalDuration) * 100, 100);
      setProgress(newProgress);

      // Calculate current step based on elapsed time
      let cumulativeDuration = 0;
      for (let i = 0; i < steps.length; i++) {
        cumulativeDuration += steps[i].duration;
        if (elapsed < cumulativeDuration) {
          setCurrentStep(i);
          break;
        }
      }

      // プログレスバーのアニメーションのみ継続し、自動完了しない
    }, 50);

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <Box
      sx={{
        minHeight: '600px',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #e3f2fd 0%, #c5cae9 100%)',
        px: 1,
        py: 2,
      }}
    >
      <Box sx={{ width: '100%', maxWidth: '900px' }}>
        {/* ヘッダー */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Box
            sx={{
              display: 'inline-flex',
              p: 2,
              bgcolor: 'primary.main',
              borderRadius: '50%',
              mb: 2,
              animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
              '@keyframes pulse': {
                '0%, 100%': { opacity: 1 },
                '50%': { opacity: 0.5 },
              },
            }}
          >
            <Search sx={{ fontSize: 40, color: 'white' }} />
          </Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            AIマッチング分析中
          </Typography>
          <Typography variant="body2" color="text.secondary">
            貴社に最適なタレントを解析しています
          </Typography>
        </Box>

        {/* プログレスバー */}
        <Box sx={{ mb: 4 }}>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 12,
              borderRadius: 6,
              mb: 1,
              '& .MuiLinearProgress-bar': {
                borderRadius: 6,
                background: 'linear-gradient(90deg, #1976d2 0%, #5e35b1 100%)',
              },
            }}
          />
          <Typography
            variant="h5"
            fontWeight="bold"
            color="primary"
            textAlign="right"
          >
            {Math.round(progress)}%
          </Typography>
        </Box>

        {/* 分析ステップ */}
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <BarChart sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" fontWeight="bold">
              分析ステップ
            </Typography>
          </Box>

          <List sx={{ maxHeight: 400, overflowY: 'auto' }}>
            {steps.map((step, index) => {
              const isCompleted = index < currentStep;
              const isCurrent = index === currentStep;
              const isPending = index > currentStep;

              return (
                <Fade in key={step.id} timeout={500}>
                  <ListItem
                    sx={{
                      borderRadius: 2,
                      mb: 1,
                      p: isCurrent ? 2 : 1,
                      bgcolor: isCompleted
                        ? 'success.lighter'
                        : isCurrent
                          ? 'primary.lighter'
                          : 'grey.100',
                      opacity: isPending ? 0.4 : 1,
                      border: 1,
                      borderColor: isCompleted
                        ? 'success.main'
                        : isCurrent
                          ? 'primary.main'
                          : 'grey.300',
                      transition: 'all 0.5s ease-in-out',
                      animation: isCurrent
                        ? 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
                        : 'none',
                    }}
                  >
                    <ListItemIcon>
                      {isCompleted ? (
                        <CheckCircle color="success" />
                      ) : isCurrent ? (
                        <CircularProgress size={24} />
                      ) : (
                        <Circle sx={{ color: 'grey.400' }} />
                      )}
                    </ListItemIcon>
                    <Box sx={{ flex: 1 }}>
                      <Typography
                        variant={isCurrent ? 'body1' : 'body2'}
                        component="div"
                        fontWeight={isCurrent ? 'bold' : 'normal'}
                        color={
                          isCompleted
                            ? 'text.primary'
                            : isCurrent
                              ? 'primary.main'
                              : 'text.secondary'
                        }
                        sx={{ mb: 0.5 }}
                      >
                        {step.title}
                      </Typography>

                      {isCurrent && (
                        <>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            component="div"
                            sx={{ mb: 1 }}
                          >
                            {step.description}
                          </Typography>
                          <Typography
                            variant="caption"
                            color="primary"
                            fontWeight="medium"
                            component="div"
                            sx={{ mb: 0.5 }}
                          >
                            {step.processingText}
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={
                              ((progress % (100 / steps.length)) /
                                (100 / steps.length)) *
                              100
                            }
                            sx={{
                              height: 8,
                              borderRadius: 4,
                              bgcolor: 'primary.lighter',
                            }}
                          />
                        </>
                      )}

                      {isCompleted && (
                        <Typography
                          variant="caption"
                          color="success.main"
                          fontWeight="medium"
                          component="div"
                        >
                          ✓ 完了
                        </Typography>
                      )}

                      {isPending && (
                        <Typography variant="caption" color="text.disabled" component="div">
                          待機中
                        </Typography>
                      )}
                    </Box>
                  </ListItem>
                </Fade>
              );
            })}
          </List>
        </Paper>

        <Paper
          elevation={2}
          sx={{
            p: 2,
            textAlign: 'center',
            background: 'linear-gradient(90deg, #1976d2 0%, #5e35b1 100%)',
            color: 'white',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 0.5 }}>
            <AutoAwesome sx={{ mr: 1, fontSize: 20 }} />
            <Typography variant="caption" fontWeight="medium">
              高度なAIアルゴリズム
            </Typography>
          </Box>
          <Typography variant="caption" sx={{ opacity: 0.9 }}>
            20,000以上のデータポイントから最適なタレントを選定
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
}
