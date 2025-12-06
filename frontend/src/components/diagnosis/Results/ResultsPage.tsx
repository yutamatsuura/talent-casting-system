'use client';

import { useState, useRef, useEffect } from 'react';
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
  Pagination,
} from '@mui/material';
import { CalendarMonth, Refresh, Error as ErrorIcon, AccountCircle, TipsAndUpdates, Download, Person } from '@mui/icons-material';
import { FormData, TalentResult, API_ENDPOINTS, ButtonClickData, ButtonClickResponse } from '@/types';
import { generateDetailedPersonalizedMessage, generateSimplePersonalizedMessage } from '@/lib/personalized-messages';
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

  // ページネーション状態管理
  const [currentPage, setCurrentPage] = useState(1);
  const talentsPerPage = 9;
  const totalPages = Math.ceil(talents.length / talentsPerPage);

  // タレントセクションのref
  const talentsSectionRef = useRef<HTMLDivElement>(null);

  // タレント詳細モーダル状態管理
  const [selectedTalent, setSelectedTalent] = useState<TalentResult | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 業界別予約リンク状態管理
  const [bookingUrl, setBookingUrl] = useState<string>('https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm');

  // 現在のページに表示するタレントを計算
  const startIndex = (currentPage - 1) * talentsPerPage;
  const endIndex = startIndex + talentsPerPage;
  const currentTalents = talents.slice(startIndex, endIndex);

  // ページ変更ハンドラ（ページネーション時のスクロール処理も含む）
  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setCurrentPage(value);

    // ページネーション時のみスクロール
    if (talentsSectionRef.current) {
      talentsSectionRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  };

  // フォーム選択値をメッセージテンプレートキーに変換するマッピング関数
  const mapIndustryToTemplateKey = (formIndustry: string): string => {
    const industryMapping: Record<string, string> = {
      // 美容・化粧品関連
      '化粧品・ヘアケア・オーラルケア': '美容・化粧品',
      'トイレタリー': '美容・化粧品',

      // 食品・飲料関連
      '食品': '食品・飲料',
      '菓子・氷菓': '食品・飲料',
      '乳製品': '食品・飲料',
      '清涼飲料水': '食品・飲料',
      'アルコール飲料': '食品・飲料',
      'フードサービス': '食品・飲料',

      // 医療・ヘルスケア関連
      '医薬品・医療・健康食品': '医療・ヘルスケア',

      // 自動車・モビリティー関連
      '自動車関連': '自動車・モビリティー',

      // IT・テクノロジー関連
      '通信・IT': 'IT・テクノロジー',
      'ゲーム・エンターテイメント・アプリ': 'IT・テクノロジー',
      '家電': 'IT・テクノロジー',

      // ファッション・アパレル関連
      'ファッション': 'ファッション・アパレル',
      '貴金属': 'ファッション・アパレル',

      // 金融・不動産関連
      '金融・不動産': '金融・保険',

      // 流通・サービス関連
      '流通・通販': 'その他',
      'エネルギー・輸送・交通': 'その他',

      // 教育関連
      '教育・出版・公共団体': '教育',

      // 旅行・レジャー関連
      '観光': '旅行・レジャー'
    };

    return industryMapping[formIndustry] || 'その他';
  };

  const generatePersonalizedMessage = (): string => {
    const companyName = formData.q4 || '貴社';
    const originalIndustry = formData.q2;
    const purpose = formData.q3_2;

    // フォーム選択値をテンプレートキーに変換
    const mappedIndustry = mapIndustryToTemplateKey(originalIndustry || '');

    // デバッグログ: パーソナライゼーションデータの確認（本番環境では無効化）
    if (process.env.NODE_ENV !== 'production') {
      console.log('🎭 パーソナライゼーションデータ確認:', {
        q4_companyName: formData.q4,
        q2_industry_original: originalIndustry,
        q2_industry_mapped: mappedIndustry,
        q3_2_purpose: formData.q3_2,
        formDataFull: formData
      });
    }

    // 業界と目的が両方選択されている場合は詳細なメッセージを生成
    if (originalIndustry && purpose) {
      try {
        const result = generateDetailedPersonalizedMessage({
          companyName,
          industry: mappedIndustry,
          purpose
        });

        // 成功ログを出力
        if (process.env.NODE_ENV !== 'production') {
          console.log('✅ 詳細パーソナライズメッセージ生成成功');
        }

        return result;
      } catch (error) {
        if (process.env.NODE_ENV !== 'production') {
          console.warn('詳細メッセージ生成に失敗、フォールバックを使用:', error);
        }
      }
    }

    // フォールバック用のシンプルメッセージ
    return generateSimplePersonalizedMessage({
      companyName,
      industry: mappedIndustry || '業界',
      purpose: purpose || 'ブランド価値向上'
    });
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
    <Container maxWidth="lg" sx={{ pt: 1, pb: 2, px: { xs: 3, sm: 4, md: 6 } }}>
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

              <Box ref={talentsSectionRef} data-talents-section>
                <Typography variant="h4" fontWeight="bold" gutterBottom>
                  おすすめタレント
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    合計11,000名中、上位30名から厳選してご提案
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {currentPage}ページ目 ({startIndex + 1}〜{Math.min(endIndex, talents.length)}件目 / {talents.length}件)
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
                  {currentTalents.map((talent, index) => {
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
                                  label="競合使用中"
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

                {/* ページネーション */}
                {totalPages > 1 && (
                  <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                    <Pagination
                      count={totalPages}
                      page={currentPage}
                      onChange={handlePageChange}
                      color="primary"
                      size="large"
                      sx={{
                        '& .MuiPagination-ul': {
                          justifyContent: 'center',
                        }
                      }}
                    />
                  </Box>
                )}
              </Box>

              {/* 特別特典セクション */}
              <Box
                sx={{
                  p: 4,
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #e3f2fd 0%, #e8f0ff 100%)',
                  mt: 5,
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
                    p: 4,
                    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                  }}
                >
                  <Box
                    sx={{
                      display: 'grid',
                      gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
                      gap: 4,
                    }}
                  >
                    {/* 左側：無料カウンセリング */}
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 3 }}>
                      <Box
                        sx={{
                          width: 64,
                          height: 64,
                          borderRadius: '50%',
                          bgcolor: '#e3f2fd',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0
                        }}
                      >
                        <CalendarMonth sx={{ fontSize: 32, color: 'primary.main' }} />
                      </Box>
                      <Box>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 1.5, lineHeight: 1.4 }}>
                          専任コンサルタントによる<br />無料カウンセリング相談(60分)
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                          業界経験豊富なコンサルタントが、貴社の課題に合わせた最適な戦略をご提案します
                        </Typography>
                      </Box>
                    </Box>

                    {/* 右側：タレント詳細情報 */}
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 3 }}>
                      <Box
                        sx={{
                          width: 64,
                          height: 64,
                          borderRadius: '50%',
                          bgcolor: '#e3f2fd',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0
                        }}
                      >
                        <Download sx={{ fontSize: 32, color: 'primary.main' }} />
                      </Box>
                      <Box>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 1.5, lineHeight: 1.4 }}>
                          貴社に最適な<br />タレント詳細情報提供
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                          11,000名のデータベースから、貴社の目的・予算に最適なタレント情報を詳しくご提供
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
