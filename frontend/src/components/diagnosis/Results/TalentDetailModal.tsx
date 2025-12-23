'use client';

// 詳細データ取得を行わないため、React hooksは不要
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
} from '@mui/material';
import {
  Close as CloseIcon,
  Star,
  CalendarMonth,
  Person,
} from '@mui/icons-material';
import { TalentDetailModalProps } from '@/types';

export function TalentDetailModal({ talent, isOpen, onClose, formData, bookingUrl }: TalentDetailModalProps) {
  // CM履歴を表示しないため、状態管理・API呼び出し・関数は不要

  // レスポンシブデザイン用
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  if (!isOpen || !talent) return null;

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      fullScreen={isMobile}
      PaperProps={{
        sx: {
          borderRadius: { xs: 0, md: 3 },
          maxHeight: { xs: '100vh', md: '90vh' },
          margin: { xs: 0, md: 'auto' },
        }
      }}
    >
      <DialogContent sx={{ p: 0 }}>
        {/* ヘッダーセクション */}
        <Box sx={{
          position: 'sticky',
          top: 0,
          zIndex: 10,
          bgcolor: 'white',
          borderBottom: '1px solid #e0e0e0',
          p: { xs: 2, md: 3 },
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
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

          <Box sx={{
            display: 'flex',
            alignItems: 'flex-start',
            flexDirection: { xs: 'column', md: 'row' },
            gap: { xs: 2, md: 3 },
            mr: { xs: 5, md: 6 }
          }}>
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
                flexShrink: 0,
                border: '2px solid #e0e0e0',
                alignSelf: { xs: 'center', md: 'flex-start' }
              }}
            >
              <Person sx={{ fontSize: { xs: 40, md: 48 }, color: '#9ca3af' }} />
            </Box>

            {/* タレント基本情報 */}
            <Box sx={{ flex: 1, minWidth: 0, textAlign: { xs: 'center', md: 'left' } }}>
              <Box sx={{
                display: 'flex',
                flexDirection: { xs: 'column', md: 'row' },
                alignItems: { xs: 'center', md: 'baseline' },
                gap: { xs: 0.5, md: 2 },
                mb: 1
              }}>
                <Typography variant="h4" fontWeight="bold" color="#2c3e50" sx={{
                  fontSize: { xs: '1.5rem', md: '2rem' }
                }}>
                  {talent.name}
                </Typography>
                {talent.kana && (
                  <Typography variant="body2" color="text.secondary">
                    ({talent.kana})
                  </Typography>
                )}
              </Box>

              <Box sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: { xs: 'center', md: 'flex-start' },
                gap: 2,
                mb: 2,
                flexWrap: 'wrap'
              }}>
                <Chip
                  label={talent.category}
                  sx={{ bgcolor: '#e3f2fd', color: '#1976d2' }}
                />
              </Box>
            </Box>

            {/* マッチングスコア表示 */}
            <Box sx={{
              flexShrink: 0,
              alignSelf: { xs: 'center', md: 'flex-start' },
              width: { xs: '100%', md: 'auto' },
              maxWidth: { xs: 180, md: 'none' }
            }}>
              <Box sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: { xs: 1.5, md: 2 },
                bgcolor: 'linear-gradient(135deg, #e3f2fd 0%, #e8f0ff 100%)',
                p: { xs: 1.5, md: 2 },
                borderRadius: 2,
                border: '1px solid #1976d2',
                minWidth: { xs: 'auto', md: 120 }
              }}>
                <Star sx={{ color: '#1976d2', fontSize: { xs: 24, md: 28 } }} />
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" fontWeight="bold" color="#1976d2" sx={{
                    fontSize: { xs: '1.5rem', md: '2rem' },
                    lineHeight: 1
                  }}>
                    {talent.matching_score}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary" fontWeight="medium" sx={{
                    fontSize: { xs: '0.7rem', md: '0.75rem' }
                  }}>
                    マッチング度
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Box>
        </Box>

        {/* メインコンテンツ */}
        <Box sx={{
          p: { xs: 2, md: 3 },
          maxHeight: { xs: 'calc(100vh - 200px)', md: 'calc(90vh - 200px)' },
          overflowY: 'auto',
          pb: { xs: 10, md: 3 } // モバイルでは下部の固定ボタン分のスペースを確保
        }}>
          {/* CM履歴非表示のため、ローディング不要 - CTAボタンのみ表示 */}
          <Box sx={{ minHeight: 200 }}>
            {/* CTAボタンセクション */}
            <Box sx={{
              mt: { xs: 3, md: 4 },
              position: { xs: 'sticky', md: 'static' },
              bottom: { xs: 0, md: 'auto' },
              bgcolor: { xs: 'white', md: 'transparent' },
              p: { xs: 2, md: 0 },
              borderTop: { xs: '1px solid #e0e0e0', md: 'none' },
              mx: { xs: -2, md: 0 },
              zIndex: { xs: 10, md: 'auto' }
            }}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={<CalendarMonth />}
                onClick={() =>
                  window.open(
                    bookingUrl,
                    '_blank'
                  )
                }
                sx={{
                  py: { xs: 2, md: 2.5 },
                  fontSize: { xs: '1rem', md: '1.1rem' },
                  fontWeight: 'bold',
                  background: 'linear-gradient(90deg, #1976d2 0%, #1565c0 100%)',
                  '&:hover': {
                    background: 'linear-gradient(90deg, #1565c0 0%, #0d47a1 100%)',
                  },
                }}
              >
                このタレントについて相談する
              </Button>
            </Box>
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
}