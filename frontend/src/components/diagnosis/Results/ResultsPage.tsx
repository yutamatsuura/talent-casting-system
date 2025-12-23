'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Container,
  Typography,
  Alert,
  Chip,
} from '@mui/material';
import { CalendarMonth, Refresh, Error as ErrorIcon, AccountCircle, TipsAndUpdates, Download, Person } from '@mui/icons-material';
import { FormData, TalentResult, API_ENDPOINTS, ButtonClickData, ButtonClickResponse } from '@/types';
// パーソナライズメッセージは固定の共通メッセージに変更済み
import { TalentDetailModal } from './TalentDetailModal';

interface ResultsPageProps {
  formData: FormData;
  onReset: () => void;
  apiResults: TalentResult[];
  apiError: string | null;
  sessionId?: string;
}

export function ResultsPage({ formData, onReset, apiResults, apiError, sessionId }: ResultsPageProps) {
  // API結果を使用（エラー時の対応含む）
  const talents = apiResults;

  // タレント詳細モーダル状態管理
  const [selectedTalent, setSelectedTalent] = useState<TalentResult | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 業界別予約リンク状態管理
  const [bookingUrl, setBookingUrl] = useState<string>('https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm');

  // 旧マッピング関数は固定メッセージ導入により削除

  const generatePersonalizedMessage = (): string => {
    // URLパラメータデコード後のフィールド名と従来のフィールド名の両方をサポート
    const formDataAny = formData as any;
    const companyName = formData.q4 || formDataAny.company_name || '貴社';
    const contactName = formData.q5 || formDataAny.contact_name || '';

    // 社名と担当者名の組み合わせを生成
    let greeting = '';
    if (contactName) {
      greeting = `${companyName} ${contactName}様`;
    } else {
      greeting = `${companyName}様`;
    }

    // 固定の共通メッセージを返却
    const commonMessage = `${greeting}、無料タレントキャスティング診断をご利用いただきありがとうございます。
入力いただいた条件をもとに、貴社に最適なタレント 30名を選定いたしました。今なら期間限定で、専任アドバイザーによる無料カウンセリングを実施中です。ご希望の場合はページ下部のボタンよりご予約ください。
貴社に最適な戦略とより詳細なデータをご用意してお待ちしております。

※本診断内容は参考情報であり、特定のタレントの出演、起用、契約の成立を保証するものではありません。`;

    // デバッグログ
    if (process.env.NODE_ENV !== 'production') {
      console.log('📝 共通メッセージ生成:', {
        companyName,
        contactName,
        greeting,
        message: commonMessage
      });
    }

    return commonMessage;
  };

  // ボタンクリック追跡関数
  const trackButtonClick = async (buttonType: string, buttonText: string) => {
    if (!sessionId) {
      if (process.env.NODE_ENV !== 'production') {
        console.warn('Session ID not available for button tracking');
      }
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}${API_ENDPOINTS.TRACK_BUTTON_CLICK}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          button_type: buttonType,
          button_text: buttonText
        } as ButtonClickData),
      });

      if (!response.ok) {
        if (process.env.NODE_ENV !== 'production') {
          console.error('Failed to track button click:', response.statusText);
        }
      }
    } catch (error) {
      if (process.env.NODE_ENV !== 'production') {
        console.error('Error tracking button click:', error);
      }
    }
  };

  // 業界別予約リンク取得関数
  const fetchBookingUrl = async () => {
    try {
      if (process.env.NODE_ENV !== 'production') {
        console.log('🔍 fetchBookingUrl実行:', {
          formData,
          q2: formData?.q2,
          hasFormData: !!formData,
          formDataKeys: formData ? Object.keys(formData) : null
        });
      }

      const industryName = formData?.q2; // q2が業界選択
      if (!industryName) {
        if (process.env.NODE_ENV !== 'production') {
          console.warn('業界が選択されていません。デフォルトURLを使用します。');
        }
        return;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/booking-link/${encodeURIComponent(industryName)}`);
      if (response.ok) {
        const data = await response.json();
        setBookingUrl(data.booking_url);
      } else {
        if (process.env.NODE_ENV !== 'production') {
          console.warn('業界別予約リンクの取得に失敗しました。デフォルトURLを使用します。');
        }
      }
    } catch (error) {
      if (process.env.NODE_ENV !== 'production') {
        console.error('業界別予約リンク取得エラー:', error);
      }
      // エラー時はデフォルトURLをそのまま使用
    }
  };

  // コンポーネント初期化時に予約URLを取得（formDataが完全に設定された後のみ）
  useEffect(() => {
    if (formData && formData.q2) {
      if (process.env.NODE_ENV !== 'production') {
        console.log('🎯 有効なformDataでfetchBookingUrlを実行');
      }
      fetchBookingUrl();
    } else {
      if (process.env.NODE_ENV !== 'production') {
        console.log('⏳ formDataまたはq2が未設定のため、fetchBookingUrlをスキップ');
      }
    }
  }, [formData?.q2]);

  return (
    <Container maxWidth="lg" sx={{ pt: 1, pb: 2, px: { xs: 0.5, sm: 2, md: 6 } }}>
      <Card elevation={3}>
        <CardHeader
          title="診断結果"
          titleTypographyProps={{
            variant: 'h2',
            fontWeight: 600,
            textAlign: 'center',
            sx: {
              color: '#2c3e50',
              letterSpacing: '0.08em',
              fontSize: { xs: '1.6rem', md: '1.9rem' },
              position: 'relative',
              fontFamily: '"Yu Gothic", "Hiragino Kaku Gothic ProN", "Hiragino Sans", sans-serif',
              '&::after': {
                content: '""',
                position: 'absolute',
                bottom: '-12px',
                left: '50%',
                transform: 'translateX(-50%)',
                width: '60px',
                height: '2px',
                background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
              }
            }
          }}
          sx={{ py: 3, px: { xs: 3, sm: 4, md: 6 } }}
        />
        <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 4, pt: 2, px: { xs: 3, sm: 4, md: 6 } }}>
          {apiError ? (
            // APIエラー時の表示
            <Alert severity="error" icon={<ErrorIcon />}>
              <Typography variant="body1" fontWeight="bold">
                マッチング処理中にエラーが発生しました
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                {apiError}
              </Typography>
              <Button
                variant="outlined"
                size="small"
                startIcon={<Refresh />}
                onClick={onReset}
                sx={{ mt: 2 }}
              >
                最初からやり直す
              </Button>
            </Alert>
          ) : (
            <>
              <Alert
                severity="info"
                icon={<TipsAndUpdates />}
                sx={{
                  background: 'linear-gradient(135deg, #e3f2fd 0%, #c5cae9 100%)',
                  borderLeft: 4,
                  borderColor: 'primary.main',
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    lineHeight: 1.6
                  }}
                >
                  {generatePersonalizedMessage()}
                </Typography>
              </Alert>

              <Box data-talents-section>
                <Typography variant="h4" fontWeight="bold" gutterBottom>
                  おすすめタレント
                </Typography>
                <Box
                  sx={{
                    display: { xs: 'block', sm: 'flex' },
                    justifyContent: { sm: 'space-between' },
                    alignItems: { sm: 'center' },
                    mb: 2,
                    gap: { xs: 1, sm: 0 }
                  }}
                >
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      mb: { xs: 1, sm: 0 },
                      fontSize: { xs: '0.75rem', sm: '0.875rem' }
                    }}
                  >
                    合計60,000名中、上位30名から厳選してご提案
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      fontSize: { xs: '0.75rem', sm: '0.875rem' },
                      textAlign: { xs: 'left', sm: 'right' }
                    }}
                  >
                    全{talents.length}名を表示
                  </Typography>
                </Box>

                {/* タレントリスト（API結果） */}
                <Box
                  sx={{
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
                    gap: 3,
                    mt: 2,
                  }}
                >
                  {talents.map((talent, index) => {
                    const isRecommended = talent.is_recommended || false;
                    const isCompetitorUsed = talent.is_currently_in_cm || false;

                    // デバッグログ：競合利用中状況を確認（本番環境では無効化）
                    if (process.env.NODE_ENV !== 'production') {
                      console.log(`タレント ${talent.name}: is_currently_in_cm=${talent.is_currently_in_cm}, isCompetitorUsed=${isCompetitorUsed}`);
                    }

                    return (
                      <Card
                        key={talent.account_id}
                        elevation={0}
                        sx={{
                          borderRadius: 3,
                          backgroundColor: 'white',
                          border: isCompetitorUsed
                            ? '2px solid #f44336'
                            : '1px solid #e9ecef',
                          transition: 'transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease',
                          overflow: 'hidden',
                          opacity: isCompetitorUsed ? 0.7 : 1,
                          filter: isCompetitorUsed ? 'grayscale(30%)' : 'none',
                          position: 'relative',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: isCompetitorUsed
                              ? '0 4px 12px rgba(244,67,54,0.3)'
                              : '0 4px 12px rgba(0,0,0,0.1)',
                            opacity: isCompetitorUsed ? 0.85 : 1,
                          },
                        }}
                      >
                        <CardContent sx={{ p: 0, pb: 1.875, position: 'relative', display: 'flex', flexDirection: 'column', height: '100%' }}>
                          {/* ステータスラベル */}
                          {(isRecommended || isCompetitorUsed) && (
                            <Box
                              sx={{
                                position: 'absolute',
                                top: 12,
                                left: 12,
                                zIndex: 1,
                                display: 'flex',
                                flexDirection: 'column',
                                gap: 0.5,
                              }}
                            >
                              {isRecommended && (
                                <Chip
                                  label="⭐ オススメ"
                                  sx={{
                                    bgcolor: '#ff9800',
                                    color: 'white',
                                    fontWeight: 'bold',
                                    fontSize: '0.75rem',
                                    height: '24px',
                                  }}
                                />
                              )}
                              {isCompetitorUsed && (
                                <Chip
                                  label="競合契約中"
                                  sx={{
                                    bgcolor: '#f44336',
                                    color: 'white',
                                    fontWeight: 'bold',
                                    fontSize: '0.75rem',
                                    height: '24px',
                                  }}
                                />
                              )}
                            </Box>
                          )}

                          {/* 競合利用中マスクオーバーレイ */}
                          {isCompetitorUsed && (
                            <Box
                              sx={{
                                position: 'absolute',
                                top: 0,
                                left: 0,
                                right: 0,
                                bottom: 0,
                                background: 'rgba(244, 67, 54, 0.15)',
                                zIndex: 2,
                                pointerEvents: 'none',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                              }}
                            >
                              {/* 斜め線パターン */}
                              <Box
                                sx={{
                                  position: 'absolute',
                                  top: 0,
                                  left: 0,
                                  right: 0,
                                  bottom: 0,
                                  background: `
                                    repeating-linear-gradient(
                                      45deg,
                                      transparent,
                                      transparent 3px,
                                      rgba(244, 67, 54, 0.08) 3px,
                                      rgba(244, 67, 54, 0.08) 6px
                                    )
                                  `,
                                  pointerEvents: 'none',
                                }}
                              />
                            </Box>
                          )}

                          {/* タレント画像エリア */}
                          <Box
                            sx={{
                              width: '100%',
                              height: { xs: '80px', sm: '100px', lg: '120px' },
                              background: 'linear-gradient(to bottom right, #f3f4f6, #e5e7eb)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              position: 'relative',
                            }}
                          >
                            <Box
                              sx={{
                                width: { xs: '64px', sm: '80px', lg: '80px' },
                                height: { xs: '64px', sm: '80px', lg: '80px' },
                                backgroundColor: 'white',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                boxShadow: 'inset 0 1px 3px rgba(0, 0, 0, 0.1)',
                              }}
                            >
                              <Person
                                sx={{
                                  fontSize: { xs: '2.5rem', sm: '3rem', lg: '3rem' },
                                  color: '#9ca3af',
                                }}
                              />
                            </Box>
                          </Box>

                          {/* コンテンツエリア */}
                          <Box sx={{ px: 1.5, py: 1, display: 'flex', flexDirection: 'column', flex: 1 }}>
                            <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                              <Typography
                                variant="body2"
                                fontWeight="bold"
                                textAlign="center"
                                sx={{ fontSize: '1rem' }}
                              >
                                {talent.name}
                              </Typography>
                            </Box>

                            <Box sx={{ pt: 0.5 }}>
                              <Button
                                variant="contained"
                                fullWidth
                                size="medium"
                                sx={{
                                  bgcolor: '#1976d2',
                                  color: 'white',
                                  fontWeight: 'bold',
                                  fontSize: '0.875rem',
                                  py: 1,
                                  textTransform: 'none',
                                  '&:hover': {
                                    bgcolor: '#1565c0',
                                  },
                                }}
                                onClick={() => {
                                  setSelectedTalent(talent);
                                  setIsModalOpen(true);
                                }}
                              >
                                詳細を見る
                              </Button>
                            </Box>
                          </Box>
                        </CardContent>
                      </Card>
                    );
                  })}
                </Box>

              </Box>

              {/* 特別特典セクション */}
              <Box
                sx={{
                  p: { xs: 2, sm: 3, md: 4 },
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #e3f2fd 0%, #e8f0ff 100%)',
                  mt: { xs: 3, md: 5 },
                  mb: 2
                }}
              >
                <Typography
                  variant="h5"
                  fontWeight={600}
                  textAlign="center"
                  sx={{
                    mb: 4,
                    color: '#2c3e50',
                    letterSpacing: '0.08em',
                    fontSize: { xs: '1.3rem', md: '1.5rem' },
                    position: 'relative',
                    fontFamily: '"Yu Gothic", "Hiragino Kaku Gothic ProN", "Hiragino Sans", sans-serif',
                    '&::after': {
                      content: '""',
                      position: 'absolute',
                      bottom: '-12px',
                      left: '50%',
                      transform: 'translateX(-50%)',
                      width: '40px',
                      height: '1px',
                      background: '#d4af37',
                    }
                  }}
                >
                  特別特典のご案内
                </Typography>

                {/* 白いカード形式のコンテナ */}
                <Box
                  sx={{
                    bgcolor: 'white',
                    borderRadius: 3,
                    p: { xs: 2, sm: 3, md: 4 },
                    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                  }}
                >
                  <Box
                    sx={{
                      display: 'grid',
                      gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
                      gap: { xs: 2, md: 4 },
                    }}
                  >
                    {/* 左側：簡易版タレントリストダウンロード */}
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: { xs: 2, md: 3 } }}>
                      <Box
                        sx={{
                          width: { xs: 48, md: 64 },
                          height: { xs: 48, md: 64 },
                          borderRadius: '50%',
                          bgcolor: '#e3f2fd',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0
                        }}
                      >
                        <Download sx={{ fontSize: { xs: 24, md: 32 }, color: 'primary.main' }} />
                      </Box>
                      <Box>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 1.5, lineHeight: 1.4 }}>
                          簡易版タレントリストダウンロード
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6, mb: 1 }}>
                          ご入力いただいたメールアドレス宛にダウンロード用リンクをお送りいたしました。
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                          診断結果をまとめたリストをダウンロードしていただけます。
                        </Typography>
                      </Box>
                    </Box>

                    {/* 右側：専任アドバイザーによる無料カウンセリング */}
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: { xs: 2, md: 3 } }}>
                      <Box
                        sx={{
                          width: { xs: 48, md: 64 },
                          height: { xs: 48, md: 64 },
                          borderRadius: '50%',
                          bgcolor: '#e3f2fd',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0
                        }}
                      >
                        <CalendarMonth sx={{ fontSize: { xs: 24, md: 32 }, color: 'primary.main' }} />
                      </Box>
                      <Box>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 1.5, lineHeight: 1.4 }}>
                          専任アドバイザーによる無料カウンセリング(60分)
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6, mb: 1 }}>
                          経験豊富なアドバイザーに無料でご相談いただけます。
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6, mb: 1 }}>
                          より詳細な情報のご提供も可能です。
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                          ご希望の場合は以下のボタンよりご予約ください。
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Box>
              </Box>
            </>
          )}

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Button
              variant="contained"
              size="large"
              fullWidth
              startIcon={<CalendarMonth />}
              onClick={async () => {
                // ボタンクリックを追跡
                await trackButtonClick('counseling_booking', '今すぐ無料カウンセリングを予約する');

                // 業界に応じた外部リンクを開く
                window.open(
                  bookingUrl,
                  '_blank'
                );
              }}
              sx={{
                py: 2.5,
                fontSize: '1.1rem',
                background: 'linear-gradient(90deg, #1976d2 0%, #1565c0 100%)',
                '&:hover': {
                  background: 'linear-gradient(90deg, #1565c0 0%, #0d47a1 100%)',
                },
              }}
            >
              今すぐ無料カウンセリングを予約する
            </Button>


            <Button
              variant="text"
              startIcon={<Refresh />}
              onClick={onReset}
              sx={{ alignSelf: 'center' }}
            >
              最初からやり直す
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* タレント詳細モーダル */}
      {selectedTalent && (
        <TalentDetailModal
          talent={selectedTalent}
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedTalent(null);
          }}
          formData={formData}
          bookingUrl={bookingUrl}
        />
      )}
    </Container>
  );
}
