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
import { CalendarMonth, Refresh, Error as ErrorIcon, AccountCircle, TipsAndUpdates, Download, Person, BarChart, EmojiEvents } from '@mui/icons-material';
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

  // CSVダウンロード状態管理
  const [csvDownloading, setCsvDownloading] = useState(false);

  // PDFダウンロード状態管理
  const [pdfDownloading, setPdfDownloading] = useState(false);


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

  // CSVダウンロードハンドラー関数
  const handleCsvDownload = async () => {
    if (!sessionId) {
      alert('セッション情報が見つかりません。ページを再読み込みしてお試しください。');
      return;
    }

    setCsvDownloading(true);

    try {
      // CSVダウンロードボタンクリックを記録
      await trackButtonClick('csv_download', 'CSVダウンロード');

      // バックエンドからCSVをダウンロード
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8432';
      const response = await fetch(`${API_BASE_URL}/api/csv-download/${sessionId}`, {
        method: 'GET',
        headers: {
          'Accept': 'text/csv',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          alert('診断結果が見つかりません。時間をおいて再度お試しください。');
        } else {
          alert('CSVダウンロード中にエラーが発生しました。しばらく時間をおいて再度お試しください。');
        }
        return;
      }

      // ファイルダウンロード処理
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      // ファイル名を取得（レスポンスヘッダーから）
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'タレント診断結果.csv';
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match) {
          filename = match[1];
        }
      }

      link.download = filename;
      document.body.appendChild(link);
      link.click();

      // クリーンアップ
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      if (process.env.NODE_ENV !== 'production') {
        console.log('✅ CSVダウンロード完了:', filename);
      }

    } catch (error) {
      console.error('❌ CSVダウンロードエラー:', error);
      alert('CSVダウンロード中にエラーが発生しました。ネットワーク接続を確認して再度お試しください。');
    } finally {
      setCsvDownloading(false);
    }
  };

  // PDFダウンロードハンドラー関数
  const handlePdfDownload = async () => {
    if (!sessionId) {
      alert('セッション情報が見つかりません。ページを再読み込みしてお試しください。');
      return;
    }

    setPdfDownloading(true);

    try {
      // PDFダウンロードボタンクリックを記録
      await trackButtonClick('pdf_download', 'PDFダウンロード');

      // バックエンドからPDFをダウンロード
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8432';
      const response = await fetch(`${API_BASE_URL}/api/pdf-download/${sessionId}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/pdf',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          alert('診断結果が見つかりません。時間をおいて再度お試しください。');
        } else {
          alert('PDFダウンロード中にエラーが発生しました。しばらく時間をおいて再度お試しください。');
        }
        return;
      }

      // ファイルダウンロード処理
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      // ファイル名を取得（レスポンスヘッダーから）
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'タレント診断結果.pdf';
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match) {
          filename = match[1];
        }
      }

      link.download = filename;
      document.body.appendChild(link);
      link.click();

      // クリーンアップ
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      if (process.env.NODE_ENV !== 'production') {
        console.log('✅ PDFダウンロード完了:', filename);
      }

    } catch (error) {
      console.error('❌ PDFダウンロードエラー:', error);
      alert('PDFダウンロード中にエラーが発生しました。ネットワーク接続を確認して再度お試しください。');
    } finally {
      setPdfDownloading(false);
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
                {/* 1〜3位 */}
                <Typography
                  variant="h5"
                  fontWeight="bold"
                  gutterBottom
                  sx={{ mt: 2.5, mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}
                >
                  <EmojiEvents sx={{ color: '#ffd700', fontSize: '1.5rem' }} />
                  1〜3位
                </Typography>
                <Box
                  sx={{
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' },
                    gap: 3,
                    mb: 0,
                  }}
                >
                  {talents.slice(0, 3).map((talent, index) => {
                    const isRecommended = true; // 1〜3位は常にオススメ
                    const isCompetitorUsed = talent.is_currently_in_cm || false;
                    const rankPosition = talent.ranking || (index + 1);

                    return (
                      <Card
                        key={talent.account_id}
                        elevation={3}
                        sx={{
                          borderRadius: 3,
                          backgroundColor: 'white',
                          border: isCompetitorUsed ? '2px solid #f44336' : '2px solid #1976d2',
                          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                          overflow: 'hidden',
                          opacity: isCompetitorUsed ? 0.7 : 1,
                          position: 'relative',
                          '&:hover': {
                            transform: 'translateY(-4px)',
                            boxShadow: '0 8px 24px rgba(25,118,210,0.2)',
                          },
                        }}
                      >
                        <CardContent sx={{ p: 0 }}>
                          {/* ランキング表示 */}
                          <Box
                            sx={{
                              position: 'absolute',
                              top: -5,
                              left: 15,
                              zIndex: 2,
                              bgcolor: rankPosition === 1 ? '#ffd700' : rankPosition === 2 ? '#c0c0c0' : '#cd7f32',
                              color: '#333',
                              borderRadius: '50%',
                              width: 40,
                              height: 40,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontWeight: 'bold',
                              fontSize: '1.1rem',
                              boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                            }}
                          >
                            {rankPosition}
                          </Box>
                          {/* ステータスラベル */}
                          {(isRecommended || isCompetitorUsed) && (
                            <Box
                              sx={{
                                position: 'absolute',
                                top: 12,
                                right: 12,
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
                              height: { xs: '120px', md: '140px' },
                              background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              position: 'relative',
                            }}
                          >
                            <Box
                              sx={{
                                width: { xs: '80px', md: '100px' },
                                height: { xs: '80px', md: '100px' },
                                backgroundColor: 'white',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                              }}
                            >
                              <Person
                                sx={{
                                  fontSize: { xs: '3rem', md: '4rem' },
                                  color: '#1976d2',
                                }}
                              />
                            </Box>
                          </Box>

                          {/* タレント情報 */}
                          <Box sx={{ p: 2.5, pb: 1.25 }}>
                            <Typography
                              variant="h6"
                              fontWeight="bold"
                              textAlign="center"
                              sx={{ mb: 1, fontSize: { xs: '1.1rem', md: '1.25rem' } }}
                            >
                              {talent.name}
                            </Typography>

                            {talent.company_name && (
                              <Typography
                                variant="body2"
                                color="text.secondary"
                                textAlign="center"
                                sx={{ mb: 1.5, fontSize: '0.9rem' }}
                              >
                                {talent.company_name}
                              </Typography>
                            )}

                            {/* マッチングスコア */}
                            <Box
                              sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                                bgcolor: '#f8f9fa',
                                borderRadius: 2,
                                p: 1.5,
                                mb: 1.5,
                              }}
                            >
                              <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5 }}>
                                マッチングスコア
                              </Typography>
                              <Typography
                                variant="h5"
                                fontWeight="bold"
                                color="#1976d2"
                              >
                                {talent.matching_score}%
                              </Typography>
                            </Box>

                            <Button
                              variant="contained"
                              fullWidth
                              size="large"
                              sx={{
                                bgcolor: '#1976d2',
                                color: 'white',
                                fontWeight: 'bold',
                                py: 1.5,
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
                        </CardContent>
                      </Card>
                    );
                  })}
                </Box>

              {/* 4〜30位 */}
              <Typography
                variant="h5"
                fontWeight="bold"
                gutterBottom
                sx={{ mt: 2.5, mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}
              >
                <BarChart sx={{ color: '#1976d2', fontSize: '1.5rem' }} />
                4〜30位
              </Typography>
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
                  gap: 2,
                  mb: 3,
                }}
              >
                {talents.slice(3).map((talent, index) => {
                  const isCompetitorUsed = talent.is_currently_in_cm || false;
                  const rankPosition = talent.ranking || (index + 4);

                  return (
                    <Card
                      key={talent.account_id}
                      elevation={1}
                      sx={{
                        borderRadius: 2,
                        backgroundColor: isCompetitorUsed ? '#fef3f3' : 'white',
                        border: isCompetitorUsed ? '1px solid #f44336' : '1px solid #e0e0e0',
                        opacity: isCompetitorUsed ? 0.7 : 1,
                        position: 'relative',
                      }}
                    >
                      {/* 順位表示 */}
                      <Box
                        sx={{
                          position: 'absolute',
                          top: 8,
                          left: 8,
                          zIndex: 2,
                          bgcolor: '#666666',
                          color: 'white',
                          borderRadius: '4px',
                          minWidth: 24,
                          height: 18,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '0.7rem',
                          fontWeight: 'bold',
                          px: 0.5,
                        }}
                      >
                        {rankPosition}
                      </Box>

                      {/* 競合契約中ラベル */}
                      {isCompetitorUsed && (
                        <Chip
                          label="競合契約中"
                          size="small"
                          sx={{
                            position: 'absolute',
                            top: 8,
                            right: 8,
                            zIndex: 2,
                            bgcolor: '#f44336',
                            color: 'white',
                            fontSize: '0.6rem',
                            fontWeight: 'bold',
                            height: 20,
                            borderRadius: '10px',
                            '& .MuiChip-label': {
                              px: 1,
                              py: 0,
                            },
                          }}
                        />
                      )}

                      <CardContent sx={{ p: 2, pt: 3 }}>
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: 2,
                          }}
                        >
                          {/* 左側：プロフィールアイコン */}
                          <Box
                            sx={{
                              width: 50,
                              height: 50,
                              borderRadius: '50%',
                              backgroundColor: '#f5f5f5',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              flexShrink: 0,
                            }}
                          >
                            <Person
                              sx={{
                                fontSize: '1.5rem',
                                color: '#9e9e9e',
                              }}
                            />
                          </Box>

                          {/* 右側：情報 */}
                          <Box sx={{ flex: 1, minWidth: 0 }}>
                            {/* タレント名 */}
                            <Typography
                              variant="body1"
                              fontWeight="bold"
                              sx={{ mb: 0.5, lineHeight: 1.2 }}
                            >
                              {talent.name}
                            </Typography>

                            {/* 事務所名 */}
                            {talent.company_name && (
                              <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 0.5, fontSize: '0.85rem', lineHeight: 1.2 }}
                              >
                                {talent.company_name}
                              </Typography>
                            )}

                            {/* マッチングスコア */}
                            <Typography
                              variant="body2"
                              color="primary"
                              fontWeight="bold"
                              sx={{ mb: 0.5 }}
                            >
                              マッチングスコア {talent.matching_score}%
                            </Typography>
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

                {/* 白いカード形式のコンテナ - 左右2カラムレイアウト */}
                <Box
                  sx={{
                    bgcolor: 'white',
                    borderRadius: 3,
                    p: { xs: 2, sm: 3, md: 4 },
                    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                  }}
                >
                  {/* 左右2カラム配置 */}
                  <Box sx={{
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
                    gap: { xs: 4, md: 6 }
                  }}>
                    {/* 左側：ダウンロード機能セクション */}
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: { xs: 2, md: 3 } }}>
                        <Box
                          sx={{
                            width: { xs: 48, md: 56 },
                            height: { xs: 48, md: 56 },
                            borderRadius: '50%',
                            bgcolor: '#e3f2fd',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0
                          }}
                        >
                          <Download sx={{ fontSize: { xs: 24, md: 28 }, color: 'primary.main' }} />
                        </Box>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, color: '#2c3e50', lineHeight: 1.3 }}>
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
                    </Box>

                    {/* 右側：専任アドバイザーセクション */}
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: { xs: 2, md: 3 } }}>
                        <Box
                          sx={{
                            width: { xs: 48, md: 56 },
                            height: { xs: 48, md: 56 },
                            borderRadius: '50%',
                            bgcolor: '#e3f2fd',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0
                          }}
                        >
                          <CalendarMonth sx={{ fontSize: { xs: 24, md: 28 }, color: 'primary.main' }} />
                        </Box>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, color: '#2c3e50', lineHeight: 1.3 }}>
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
