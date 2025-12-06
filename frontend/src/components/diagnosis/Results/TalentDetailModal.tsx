'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  Box,
  Typography,
  Button,
  IconButton,
  Card,
  CardContent,
  Chip,
  Divider,
  CircularProgress,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Close as CloseIcon,
  Star,
  CalendarMonth,
  Person,
  ChevronLeft,
  ChevronRight,
  Business,
  Movie,
  AccountCircle,
} from '@mui/icons-material';
import { TalentDetailModalProps, CMHistoryDetail, TalentDetailInfo } from '@/types';
import { fetchTalentDetails } from '@/lib/api';
import { getCategoryName, getCategoryColor, getAllCategoryNames } from '@/utils/categoryMapping';

export function TalentDetailModal({ talent, isOpen, onClose, formData, bookingUrl }: TalentDetailModalProps) {
  const [detailData, setDetailData] = useState<TalentDetailInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const timelineRef = useRef<HTMLDivElement>(null);

  // レスポンシブデザイン用
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // モーダル開閉時のデータ取得
  useEffect(() => {
    if (isOpen && talent) {
      fetchTalentDetail();
    }
  }, [isOpen, talent]);

  const fetchTalentDetail = async () => {
    setLoading(true);
    try {
      // ターゲットセグメントIDを取得（フォームデータから）
      // target_segments値から対応するIDにマッピング
      const targetSegmentMapping: { [key: string]: number } = {
        '男性12-19': 9,
        '女性12-19': 10,
        '男性20-34': 11,
        '女性20-34': 12,
        '男性35-49': 13,
        '女性35-49': 14,
        '男性50-69': 15,
        '女性50-69': 16
      };

      const targetSegmentId = targetSegmentMapping[formData.q3];

      console.log('🔍 Fetching talent detail:', {
        accountId: talent.account_id,
        targetSegmentId,
        formDataTargetSegments: formData.q3
      });

      // 実際のAPIを呼び出し
      const detailData = await fetchTalentDetails(talent.account_id, targetSegmentId);

      // 既存のマッチング結果からスコアと順位を設定
      const completeDetailData: TalentDetailInfo = {
        ...detailData,
        matching_score: talent.matching_score, // 結果ページから継承
        ranking: talent.ranking,               // 結果ページから継承
      };

      setDetailData(completeDetailData);

    } catch (error) {
      console.error('❌ タレント詳細データの取得に失敗:', error);

      // エラー時はフォールバック（基本情報のみ表示）
      const fallbackData: TalentDetailInfo = {
        account_id: talent.account_id,
        name: talent.name,
        kana: talent.kana,
        category: talent.category,
        matching_score: talent.matching_score,
        ranking: talent.ranking,
        cm_history: [],
        introduction: 'データの取得に失敗しました。しばらく時間をおいて再度お試しください。',
      };
      setDetailData(fallbackData);
    } finally {
      setLoading(false);
    }
  };

  const scrollTimeline = (direction: 'left' | 'right') => {
    if (timelineRef.current) {
      const scrollAmount = 344; // 1カード分の幅
      const newScrollLeft = timelineRef.current.scrollLeft + (direction === 'right' ? scrollAmount : -scrollAmount);
      timelineRef.current.scrollTo({
        left: newScrollLeft,
        behavior: 'smooth',
      });
    }
  };

  const formatPeriod = (startDate: string, endDate?: string) => {
    const start = new Date(startDate).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
    });
    if (endDate) {
      const end = new Date(endDate).toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: 'short',
      });
      return `${start}〜${end}`;
    }
    return `${start}〜`;
  };

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
                {detailData?.kana && (
                  <Typography variant="body2" color="text.secondary">
                    ({detailData.kana})
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
                {detailData?.category && (
                  <Chip
                    label={detailData.category}
                    sx={{ bgcolor: '#e3f2fd', color: '#1976d2' }}
                  />
                )}
                {detailData?.age && (
                  <Typography variant="body2" color="text.secondary">
                    {detailData.age}歳
                  </Typography>
                )}
              </Box>

              {detailData?.introduction && (
                <Typography variant="body2" color="text.secondary" sx={{
                  lineHeight: 1.6,
                  textAlign: { xs: 'center', md: 'left' }
                }}>
                  {detailData.introduction}
                </Typography>
              )}
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
          {loading ? (
            <Box sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              p: 4,
              minHeight: 200
            }}>
              <CircularProgress sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                詳細情報を読み込み中...
              </Typography>
            </Box>
          ) : (
            <Box sx={{ minHeight: 200 }}>
              {/* CM出演履歴タイムライン */}
              {detailData?.cm_history && detailData.cm_history.length > 0 && (
                <Box sx={{ mb: { xs: 3, md: 4 } }}>
                  <Box sx={{
                    display: 'flex',
                    alignItems: { xs: 'flex-start', md: 'center' },
                    justifyContent: 'space-between',
                    mb: { xs: 2, md: 3 },
                    flexDirection: { xs: 'column', sm: 'row' },
                    gap: { xs: 2, sm: 0 }
                  }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1.5, md: 2 } }}>
                      <Box sx={{
                        p: { xs: 1, md: 1.5 },
                        bgcolor: '#e8f5e8',
                        borderRadius: 2,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <Movie sx={{ fontSize: { xs: 20, md: 24 }, color: '#2e7d32' }} />
                      </Box>
                      <Typography variant={isMobile ? "h6" : "h5"} fontWeight="bold" color="#2c3e50">
                        CM出演履歴
                      </Typography>
                    </Box>

                    {/* デスクトップでのみスクロールボタンを表示 */}
                    {!isMobile && (
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <IconButton
                          onClick={() => scrollTimeline('left')}
                          sx={{
                            width: 32,
                            height: 32,
                            border: '1px solid #e0e0e0',
                            '&:hover': { bgcolor: '#f5f5f5' }
                          }}
                        >
                          <ChevronLeft sx={{ fontSize: 20 }} />
                        </IconButton>
                        <IconButton
                          onClick={() => scrollTimeline('right')}
                          sx={{
                            width: 32,
                            height: 32,
                            border: '1px solid #e0e0e0',
                            '&:hover': { bgcolor: '#f5f5f5' }
                          }}
                        >
                          <ChevronRight sx={{ fontSize: 20 }} />
                        </IconButton>
                      </Box>
                    )}
                  </Box>

                  <Box
                    ref={timelineRef}
                    sx={{
                      display: 'flex',
                      flexDirection: { xs: 'column', md: 'row' },
                      gap: { xs: 2, md: 3 },
                      overflowX: { xs: 'visible', md: 'auto' },
                      overflowY: { xs: 'visible', md: 'hidden' },
                      pb: 2,
                      maxHeight: { xs: 'none', md: 'auto' },
                      '&::-webkit-scrollbar': {
                        height: 6,
                      },
                      '&::-webkit-scrollbar-track': {
                        bgcolor: '#f1f1f1',
                        borderRadius: 3,
                      },
                      '&::-webkit-scrollbar-thumb': {
                        bgcolor: '#c1c1c1',
                        borderRadius: 3,
                        '&:hover': { bgcolor: '#a8a8a8' },
                      },
                    }}
                  >
                    {detailData.cm_history.map((cm, index) => (
                      <Card
                        key={index}
                        sx={{
                          minWidth: { xs: '100%', md: 320 },
                          maxWidth: { xs: '100%', md: 320 },
                          flexShrink: 0,
                          borderRadius: 3,
                          border: '1px solid #e0e0e0',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            transform: { xs: 'none', md: 'translateY(-2px)' },
                            boxShadow: { xs: 'none', md: '0 8px 24px rgba(0,0,0,0.1)' },
                          },
                        }}
                      >
                        <CardContent sx={{ p: { xs: 2, md: 3 } }}>
                          {/* カード ヘッダー */}
                          <Box sx={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'flex-start',
                            mb: 2,
                            flexDirection: { xs: 'column', md: 'row' },
                            gap: { xs: 1, md: 0 }
                          }}>
                            <Box sx={{ flex: 1, minWidth: 0, width: { xs: '100%', md: 'auto' } }}>
                              <Typography variant="h6" fontWeight="bold" sx={{
                                fontSize: { xs: '1rem', md: '1.1rem' },
                                lineHeight: 1.3,
                                mb: 0.5,
                                overflow: { xs: 'visible', md: 'hidden' },
                                textOverflow: { xs: 'unset', md: 'ellipsis' },
                                whiteSpace: { xs: 'normal', md: 'nowrap' }
                              }}>
                                {cm.product_name}
                              </Typography>
                              <Typography variant="body2" color="text.secondary" sx={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 1,
                                mb: 1
                              }}>
                                <Business sx={{ fontSize: { xs: 14, md: 16 } }} />
                                {cm.client_name}
                              </Typography>
                            </Box>
                            <Box sx={{
                              display: 'flex',
                              flexDirection: 'column',
                              gap: 0.5,
                              alignItems: { xs: 'flex-start', md: 'flex-end' },
                              width: { xs: '100%', md: 'auto' }
                            }}>
                              {/* 従来のカテゴリ表示を非表示にする（ほとんどが「その他」になるため） */}
                              {/* {cm.category && (
                                <Chip
                                  label={cm.category}
                                  size="small"
                                  sx={{
                                    bgcolor: '#f3e5f5',
                                    color: '#7b1fa2',
                                    fontSize: '0.75rem'
                                  }}
                                />
                              )} */}

                              {/* 新しいカテゴリラベル（Category Code based） */}
                              {(() => {
                                const categoryNames = getAllCategoryNames(
                                  cm.rival_category_type_cd1,
                                  cm.rival_category_type_cd2,
                                  cm.rival_category_type_cd3,
                                  cm.rival_category_type_cd4
                                );

                                if (categoryNames.length === 0) {
                                  return null; // カテゴリがない場合は何も表示しない
                                }

                                const categoryIds = [
                                  cm.rival_category_type_cd1,
                                  cm.rival_category_type_cd2,
                                  cm.rival_category_type_cd3,
                                  cm.rival_category_type_cd4
                                ].filter((id): id is number => id !== null && id !== undefined && id !== 0);

                                return (
                                  <Box sx={{
                                    display: 'flex',
                                    flexWrap: 'wrap',
                                    gap: 0.5,
                                    justifyContent: { xs: 'flex-start', md: 'flex-end' },
                                    maxWidth: { xs: '100%', md: 'none' }
                                  }}>
                                    {categoryNames.map((categoryName, idx) => (
                                      <Chip
                                        key={idx}
                                        label={categoryName}
                                        size="small"
                                        color={getCategoryColor(categoryIds[idx])}
                                        variant="outlined"
                                        sx={{
                                          fontSize: { xs: '0.65rem', md: '0.7rem' },
                                          height: { xs: '18px', md: '20px' },
                                          fontWeight: 500
                                        }}
                                      />
                                    ))}
                                  </Box>
                                );
                              })()}
                            </Box>
                          </Box>

                          <Divider sx={{ mb: 2 }} />

                          {/* 期間 */}
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                            <CalendarMonth sx={{ fontSize: 16, color: '#666' }} />
                            <Typography variant="body2" color="text.secondary">
                              {formatPeriod(cm.use_period_start, cm.use_period_end)}
                            </Typography>
                          </Box>

                          {/* 詳細情報 */}
                          <Box sx={{ space: 1 }}>
                            {cm.agency_name && (
                              <Typography variant="caption" display="block" color="text.secondary">
                                代理店: {cm.agency_name}
                              </Typography>
                            )}
                            {cm.production_name && (
                              <Typography variant="caption" display="block" color="text.secondary">
                                制作: {cm.production_name}
                              </Typography>
                            )}
                            {cm.director && (
                              <Typography variant="caption" display="block" color="text.secondary">
                                監督: {cm.director}
                              </Typography>
                            )}
                          </Box>

                          {cm.note && (
                            <Box sx={{ mt: 2, p: 1.5, bgcolor: '#fafafa', borderRadius: 1 }}>
                              <Typography variant="caption" color="text.secondary">
                                {cm.note}
                              </Typography>
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </Box>
                </Box>
              )}

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
          )}
        </Box>
      </DialogContent>
    </Dialog>
  );
}