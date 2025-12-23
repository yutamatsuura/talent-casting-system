'use client';

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  Box,
  Typography,
  Button,
  IconButton,
  Chip,
  useTheme,
  useMediaQuery,
  CircularProgress,
} from '@mui/material';
import {
  Close as CloseIcon,
  Star,
  Person,
  Business,
  Cake,
  LocationOn,
} from '@mui/icons-material';
import { TalentDetailModalProps, TalentDetailInfo } from '@/types';
import { fetchTalentDetails } from '@/lib/api';

export function TalentDetailModal({ talent, isOpen, onClose, formData, bookingUrl }: TalentDetailModalProps) {
  const [talentDetails, setTalentDetails] = useState<TalentDetailInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // レスポンシブデザイン用
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // モーダルが開かれた際にタレント詳細情報を取得
  useEffect(() => {
    if (isOpen && talent) {
      const loadTalentDetails = async () => {
        setIsLoading(true);
        setError(null);
        try {
          console.log('🔍 タレント詳細取得開始:', talent.account_id);
          const details = await fetchTalentDetails(talent.account_id);
          console.log('✅ タレント詳細取得成功:', details);

          // マッチングスコアとランキングを元の結果から保持
          const detailsWithScore = {
            ...details,
            matching_score: talent.matching_score,
            ranking: talent.ranking
          };

          setTalentDetails(detailsWithScore);
        } catch (err) {
          console.error('❌ タレント詳細取得失敗:', err);
          setError('タレント詳細情報の取得に失敗しました');
        } finally {
          setIsLoading(false);
        }
      };

      loadTalentDetails();
    }
  }, [isOpen, talent]);

  // モーダルが閉じられた際にデータをリセット
  useEffect(() => {
    if (!isOpen) {
      setTalentDetails(null);
      setError(null);
    }
  }, [isOpen]);

  if (!isOpen || !talent) return null;

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      fullScreen={isMobile}
      PaperProps={{
        sx: {
          borderRadius: { xs: 0, md: 3 },
          maxHeight: { xs: '100vh', md: '90vh' },
          margin: { xs: 0, md: 'auto' },
          maxWidth: { xs: '100%', md: 480 },
        }
      }}
    >
      <DialogContent sx={{ p: 0 }}>
        {/* ヘッダーセクション - 縦型コンパクトレイアウト */}
        <Box sx={{
          position: 'sticky',
          top: 0,
          zIndex: 10,
          bgcolor: 'white',
          borderBottom: '1px solid #e0e0e0',
          p: { xs: 2, md: 3 },
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}>
          <IconButton
            onClick={onClose}
            sx={{
              position: 'absolute',
              top: { xs: 12, md: 16 },
              right: { xs: 12, md: 16 },
              bgcolor: 'grey.100',
              '&:hover': { bgcolor: 'grey.200' }
            }}
          >
            <CloseIcon />
          </IconButton>

          {/* タレント画像 */}
          <Box
            sx={{
              width: { xs: 80, md: 96 },
              height: { xs: 80, md: 96 },
              borderRadius: 3,
              bgcolor: 'linear-gradient(to bottom right, #f3f4f6, #e5e7eb)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid #e0e0e0',
              mx: 'auto',
              mb: 2
            }}
          >
            <Person sx={{ fontSize: { xs: 40, md: 48 }, color: '#9ca3af' }} />
          </Box>

          {/* タレント名とふりがな */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="h4" fontWeight="bold" color="#2c3e50" sx={{
              fontSize: { xs: '1.5rem', md: '1.8rem' },
              mb: 0.5
            }}>
              {talentDetails ? talentDetails.name : talent.name}
            </Typography>
            {(talentDetails?.kana || talent.kana) && (
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.9rem' }}>
                ({talentDetails?.kana || talent.kana})
              </Typography>
            )}
          </Box>

          {/* カテゴリ */}
          {(talentDetails?.category || talent.category) && (
            <Box sx={{ mb: 3 }}>
              <Chip
                label={talentDetails?.category || talent.category}
                sx={{
                  bgcolor: '#e3f2fd',
                  color: '#1976d2',
                  fontSize: '0.9rem',
                  height: 32
                }}
              />
            </Box>
          )}

          {/* 詳細情報（事務所名、年齢、出身地、マッチング度）*/}
          <Box sx={{
            display: 'flex',
            flexDirection: 'column',
            gap: 1.5,
            alignItems: 'center',
            maxWidth: 300,
            mx: 'auto'
          }}>
            {/* 事務所名 */}
            {(talentDetails?.company_name || talent.company_name) && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Business sx={{ fontSize: 20, color: 'text.secondary' }} />
                <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.95rem' }}>
                  {talentDetails?.company_name || talent.company_name}
                </Typography>
              </Box>
            )}

            {/* 年齢 */}
            {talentDetails?.age && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Cake sx={{ fontSize: 20, color: 'text.secondary' }} />
                <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.95rem' }}>
                  {talentDetails.age}歳
                </Typography>
              </Box>
            )}

            {/* 出身地 */}
            {talentDetails?.birthplace && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocationOn sx={{ fontSize: 20, color: 'text.secondary' }} />
                <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.95rem' }}>
                  {talentDetails.birthplace}出身
                </Typography>
              </Box>
            )}

            {/* マッチングスコア */}
            <Box sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 1.5,
              bgcolor: 'linear-gradient(135deg, #e3f2fd 0%, #e8f0ff 100%)',
              p: 2,
              borderRadius: 2,
              border: '1px solid #1976d2',
              mt: 1
            }}>
              <Star sx={{ color: '#1976d2', fontSize: 24 }} />
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h5" fontWeight="bold" color="#1976d2" sx={{
                  fontSize: '1.5rem',
                  lineHeight: 1
                }}>
                  {talentDetails ? talentDetails.matching_score : talent.matching_score}%
                </Typography>
                <Typography variant="caption" color="text.secondary" fontWeight="medium" sx={{
                  fontSize: '0.75rem'
                }}>
                  マッチング度
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>

        {/* メインコンテンツ */}
        <Box sx={{
          p: { xs: 2, md: 3 },
          minHeight: 'auto'
        }}>
          {/* ローディング状態 */}
          {isLoading && (
            <Box sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              py: 4,
              gap: 2
            }}>
              <CircularProgress size={40} />
              <Typography variant="body2" color="text.secondary">
                詳細情報を読み込んでいます...
              </Typography>
            </Box>
          )}

          {/* エラー状態 */}
          {error && !isLoading && (
            <Box sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              py: 4,
              gap: 2
            }}>
              <Typography variant="body1" color="error" textAlign="center" sx={{ fontSize: '0.9rem' }}>
                {error}
              </Typography>
              <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ fontSize: '0.8rem' }}>
                詳細情報の取得に失敗しましたが、基本情報は表示されています。
              </Typography>
            </Box>
          )}

          {/* 正常状態 - コンパクトな表示 */}
          {!isLoading && !error && (
            <Box sx={{ py: 1, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                詳細情報の表示が完了しました
              </Typography>
            </Box>
          )}
        </Box>
      </DialogContent>
    </Dialog>
  );
}