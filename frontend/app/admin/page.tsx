'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Container,
  AppBar,
  Toolbar,
  Fade,
  Slide,
  Tooltip,
  Snackbar,
  useMediaQuery,
  useTheme,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stack,
  Menu,
  MenuItem,
  ListItemIcon,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Download,
  Refresh,
  Logout,
  Analytics,
  TrendingUp,
  People,
  TouchApp,
  Today,
  AdminPanelSettings,
  ExpandMore,
  Phone,
  Email,
  Business,
  Link,
  Edit,
  Save,
  Cancel,
  Settings,
  Star,
  MoreVert,
} from '@mui/icons-material';

// 管理画面用の型定義
interface FormSubmissionData {
  id: number;
  session_id: string;
  industry: string;
  target_segment: string;
  purpose: string;
  budget_range: string;
  company_name: string;
  email: string;
  contact_name: string;
  phone_number: string;
  genre_preference?: string;
  preferred_genres?: string[];
  created_at: string;
  button_clicked?: boolean;
  button_clicked_at?: string;
}

interface ButtonClickData {
  id: number;
  session_id: string;
  button_type: string;
  button_text: string;
  clicked_at: string;
}

interface BookingLinkData {
  id: number;
  industry_name: string;
  booking_url: string;
  created_at: string;
  updated_at: string | null;
}

const ADMIN_PASSWORD = 'talent2025admin';

// 日本時間（JST）でフォーマットする関数
const formatJapanTime = (isoString: string): string => {
  const date = new Date(isoString);
  return date.toLocaleString('ja-JP', {
    timeZone: 'Asia/Tokyo',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

export default function AdminPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isSmallMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const router = useRouter();

  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // データ管理用のstate
  const [formSubmissions, setFormSubmissions] = useState<FormSubmissionData[]>([]);
  const [buttonClicks, setButtonClicks] = useState<ButtonClickData[]>([]);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  // フィルター用のstate
  const [selectedSubmission, setSelectedSubmission] = useState<FormSubmissionData | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);

  // コピー機能用のstate
  const [copySnackbarOpen, setCopySnackbarOpen] = useState(false);
  const [copyMessage, setCopyMessage] = useState('');

  // ★ 診断結果用のstate（新規追加）
  const [diagnosisResults, setDiagnosisResults] = useState<any[]>([]);
  const [diagnosisLoading, setDiagnosisLoading] = useState(false);

  // メニュー用のstate
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const menuOpen = Boolean(anchorEl);

  // 業界別予約リンク管理用のstate
  const [bookingLinks, setBookingLinks] = useState<BookingLinkData[]>([]);
  const [editingLinkId, setEditingLinkId] = useState<number | null>(null);
  const [editingLinkUrl, setEditingLinkUrl] = useState('');

  // コピー機能
  const handleCopyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopyMessage(`${label}をクリップボードにコピーしました`);
      setCopySnackbarOpen(true);
    } catch (err) {
      setCopyMessage('コピーに失敗しました');
      setCopySnackbarOpen(true);
    }
  };

  // メニュー処理
  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleMenuAction = (action: string) => {
    handleMenuClose();
    switch (action) {
      case 'refresh':
        fetchData();
        break;
      case 'export':
        exportToCSV();
        break;
      case 'booking-links':
        router.push('/admin/booking-links');
        break;
      case 'recommended-talents':
        router.push('/admin/recommended-talents');
        break;
      case 'logout':
        handleLogout();
        break;
      default:
        break;
    }
  };

  // ページロード時にログイン状態を復元
  useEffect(() => {
    const savedAuthState = localStorage.getItem('admin_authenticated');
    if (savedAuthState === 'true') {
      setIsAuthenticated(true);
      fetchData();
    }
    setIsInitialized(true);
  }, []);

  // 認証処理
  const handleLogin = () => {
    if (password === ADMIN_PASSWORD) {
      setIsAuthenticated(true);
      localStorage.setItem('admin_authenticated', 'true'); // ログイン状態をlocalStorageに保存
      setError(null);
      setPassword('');
      fetchData();
    } else {
      setError('パスワードが正しくありません');
    }
  };

  // ログアウト処理
  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('admin_authenticated'); // ログイン状態をlocalStorageから削除
    setFormSubmissions([]);
    setButtonClicks([]);
    setLastRefresh(null);
  };

  // データ取得
  const fetchData = async () => {
    setLoading(true);
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8432';

      // フォーム送信データ取得
      const submissionsResponse = await fetch(`${API_BASE_URL}/api/admin/form-submissions`);
      if (!submissionsResponse.ok) throw new Error('フォームデータの取得に失敗しました');
      const submissions = await submissionsResponse.json();

      // ボタンクリックデータ取得
      const clicksResponse = await fetch(`${API_BASE_URL}/api/admin/button-clicks`);
      if (!clicksResponse.ok) throw new Error('ボタンクリックデータの取得に失敗しました');
      const clicks = await clicksResponse.json();

      // データをマージしてbutton_clickedフラグを追加
      const mergedData = submissions.map((submission: FormSubmissionData) => {
        const hasClicked = clicks.some((click: ButtonClickData) =>
          click.session_id === submission.session_id &&
          click.button_type === 'counseling_booking'
        );
        const clickData = clicks.find((click: ButtonClickData) =>
          click.session_id === submission.session_id &&
          click.button_type === 'counseling_booking'
        );

        return {
          ...submission,
          button_clicked: hasClicked,
          button_clicked_at: clickData?.clicked_at || null,
        };
      });

      setFormSubmissions(mergedData);
      setButtonClicks(clicks);
      setLastRefresh(new Date());

      // 業界別予約リンクデータも取得
      await fetchBookingLinks();
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  // CSVエクスポート
  const exportToCSV = () => {
    const headers = [
      'ID', 'セッションID', '業界', 'ターゲット層', '予算', '会社名', 'メール', '担当者名',
      '電話番号', 'ジャンル希望', 'ジャンル詳細', '送信日時', 'ボタンクリック', 'クリック日時'
    ];

    const csvContent = [
      headers.join(','),
      ...formSubmissions.map(row => [
        row.id,
        row.session_id,
        `"${row.industry}"`,
        `"${row.target_segment}"`,
        `"${row.budget_range}"`,
        `"${row.company_name}"`,
        row.email,
        `"${row.contact_name}"`,
        row.phone_number,
        `"${row.genre_preference || ''}"`,
        `"${row.preferred_genres?.join(', ') || ''}"`,
        formatJapanTime(row.created_at),
        row.button_clicked ? 'あり' : 'なし',
        row.button_clicked_at ? formatJapanTime(row.button_clicked_at) : ''
      ].join(','))
    ].join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `talent-casting-form-data-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  // 診断結果CSVエクスポート（リアルタイム分析によるGoogle Sheetsと同じデータ）
  const handleExportDiagnosisCSV = async (submission: FormSubmissionData | null) => {
    if (!submission) {
      setCopyMessage('エクスポート可能な診断結果がありません');
      setCopySnackbarOpen(true);
      return;
    }

    try {
      setCopyMessage('診断結果を取得中...');
      setCopySnackbarOpen(true);

      // リアルタイム分析データを取得（Google Sheetsと同じロジック）
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8432';
      const response = await fetch(
        `${API_BASE_URL}/api/admin/form-submissions/${submission.id}/diagnosis-results-for-csv`
      );

      if (!response.ok) {
        throw new Error(`CSVデータ取得失敗: ${response.status}`);
      }

      const data = await response.json();
      const csvExportData = data.csv_export_data || [];

      if (csvExportData.length === 0) {
        setCopyMessage('エクスポート可能な診断結果がありません');
        setCopySnackbarOpen(true);
        return;
      }

      // Google Sheetsと同じ16項目ヘッダー
      const headers = [
        'タレント名',
        'カテゴリー',
        'VR人気度',
        'TPRスコア',
        '従来スコア',
        'おもしろさ',
        '清潔感',
        '個性的な',
        '信頼できる',
        'かわいい',
        'カッコいい',
        '大人の魅力',
        '従来順位',
        '業種別イメージ',
        '最終スコア',
        '最終順位'
      ];

      // enhanced_matching_debugからのデータを使用（Google Sheetsと同じ）
      const csvData = csvExportData.map((talent: any) => [
        `"${talent['タレント名'] || ''}"`,
        `"${talent['カテゴリー'] || ''}"`,
        talent['VR人気度'] || 0,
        talent['TPRスコア'] || 0,
        talent['従来スコア'] || 0,
        talent['おもしろさ'] || 0,
        talent['清潔感'] || 0,
        talent['個性的な'] || 0,
        talent['信頼できる'] || 0,
        talent['かわいい'] || 0,
        talent['カッコいい'] || 0,
        talent['大人の魅力'] || 0,
        talent['従来順位'] || 0,
        talent['業種別イメージ'] || 0,
        talent['最終スコア'] || 0,
        talent['最終順位'] || 0
      ].join(','));

      // CSVコンテンツ作成
      const csvContent = [
        headers.join(','),
        ...csvData
      ].join('\n');

      // メタデータ追加（空行を挟んで）
      const metadata = [
        '',
        '',
        '■ 実行条件',
        `企業名,"${submission.company_name}"`,
        `担当者,"${submission.contact_name}"`,
        `業種,"${submission.industry}"`,
        `ターゲット層,"${submission.target_segment}"`,
        `予算,"${submission.budget_range}"`,
        `起用目的,${submission.purpose || ''}`,
        `診断実行日時,${new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })}`,
        `タレント数,${csvExportData.length}件`
      ].join('\n');

      const finalCsvContent = csvContent + '\n' + metadata;

      // BOM付きCSVでダウンロード
      const blob = new Blob(['\uFEFF' + finalCsvContent], {
        type: 'text/csv;charset=utf-8;'
      });

      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `診断結果_${submission.company_name}_${submission.session_id}_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();

      setCopyMessage('診断結果CSVをダウンロードしました');
      setCopySnackbarOpen(true);

    } catch (error) {
      console.error('CSV export error:', error);
      setCopyMessage('CSVエクスポートに失敗しました');
      setCopySnackbarOpen(true);
    }
  };

  // 詳細表示（診断結果取得機能追加）
  const handleShowDetail = async (submission: FormSubmissionData) => {
    setSelectedSubmission(submission);
    setDetailDialogOpen(true);

    // ★ 診断結果取得を追加
    setDiagnosisLoading(true);
    setDiagnosisResults([]);

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8432';
      const response = await fetch(
        `${API_BASE_URL}/api/admin/form-submissions/${submission.id}/diagnosis`
      );

      if (response.ok) {
        const data = await response.json();
        setDiagnosisResults(data.diagnosis_results || []);
        console.log('✅ 診断結果取得成功:', data.diagnosis_results?.length || 0, '件');
      } else {
        console.log('ℹ️ 診断結果なし（まだ実行されていない可能性）');
        setDiagnosisResults([]);
      }
    } catch (error) {
      console.error('❌ 診断結果取得エラー:', error);
      setDiagnosisResults([]);
    } finally {
      setDiagnosisLoading(false);
    }
  };

  // 業界別予約リンク取得
  const fetchBookingLinks = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8432';
      const response = await fetch(`${API_BASE_URL}/api/admin/booking-links`);
      if (!response.ok) throw new Error('業界別予約リンクデータの取得に失敗しました');
      const links = await response.json();
      setBookingLinks(links);
    } catch (err) {
      setError(err instanceof Error ? err.message : '業界別予約リンクデータの取得に失敗しました');
    }
  };

  // 業界別予約リンク編集開始
  const handleEditBookingLink = (link: BookingLinkData) => {
    setEditingLinkId(link.id);
    setEditingLinkUrl(link.booking_url);
  };

  // 業界別予約リンク編集キャンセル
  const handleCancelEditBookingLink = () => {
    setEditingLinkId(null);
    setEditingLinkUrl('');
  };

  // 業界別予約リンク保存
  const handleSaveBookingLink = async (linkId: number) => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8432';
      const response = await fetch(`${API_BASE_URL}/api/admin/booking-links/${linkId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ booking_url: editingLinkUrl }),
      });

      if (!response.ok) throw new Error('予約リンクの更新に失敗しました');

      // 更新されたデータを取得して表示に反映
      await fetchBookingLinks();
      setEditingLinkId(null);
      setEditingLinkUrl('');

      setCopyMessage('予約リンクが正常に更新されました');
      setCopySnackbarOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予約リンクの更新に失敗しました');
    }
  };

  // 初期化が完了していない場合は何も表示しない（ちらつき防止）
  if (!isInitialized) {
    return null;
  }

  // 認証されていない場合のログイン画面
  if (!isAuthenticated) {
    return (
      <Box sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 20%, #764ba2 80%)',
        position: 'relative',
        overflow: 'hidden',
        // 小さな円形の図形が動く
        '&::before': {
          content: '""',
          position: 'absolute',
          top: '10%',
          left: '10%',
          width: '60px',
          height: '60px',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '50%',
          animation: 'floatCircle 20s ease-in-out infinite',
          zIndex: 1,
        },
        '@keyframes floatCircle': {
          '0%': {
            transform: 'translate(0, 0)',
          },
          '25%': {
            transform: 'translate(150px, 80px)',
          },
          '50%': {
            transform: 'translate(300px, 40px)',
          },
          '75%': {
            transform: 'translate(100px, 120px)',
          },
          '100%': {
            transform: 'translate(0, 0)',
          }
        },
        // 小さな四角形の図形が動く
        '&::after': {
          content: '""',
          position: 'absolute',
          top: '70%',
          right: '15%',
          width: '40px',
          height: '40px',
          background: 'rgba(255,255,255,0.08)',
          animation: 'floatSquare 25s ease-in-out infinite reverse',
          zIndex: 1,
        },
        '@keyframes floatSquare': {
          '0%': {
            transform: 'translate(0, 0) rotate(0deg)',
          },
          '33%': {
            transform: 'translate(-120px, -60px) rotate(120deg)',
          },
          '66%': {
            transform: 'translate(-80px, -140px) rotate(240deg)',
          },
          '100%': {
            transform: 'translate(0, 0) rotate(360deg)',
          }
        }
      }}>
        {/* 三角形の図形を追加 */}
        <Box sx={{
          position: 'absolute',
          top: '40%',
          left: '80%',
          width: '50px',
          height: '50px',
          zIndex: 1,
          '&::before': {
            content: '""',
            position: 'absolute',
            width: 0,
            height: 0,
            borderLeft: '25px solid transparent',
            borderRight: '25px solid transparent',
            borderBottom: '43px solid rgba(255,255,255,0.06)',
            animation: 'floatTriangle 30s ease-in-out infinite',
          },
          '@keyframes floatTriangle': {
            '0%': {
              transform: 'translate(0, 0) rotate(0deg)',
            },
            '20%': {
              transform: 'translate(-200px, 50px) rotate(72deg)',
            },
            '40%': {
              transform: 'translate(-100px, -80px) rotate(144deg)',
            },
            '60%': {
              transform: 'translate(-300px, 20px) rotate(216deg)',
            },
            '80%': {
              transform: 'translate(-150px, 100px) rotate(288deg)',
            },
            '100%': {
              transform: 'translate(0, 0) rotate(360deg)',
            }
          }
        }} />

        <Box sx={{
          position: 'relative',
          zIndex: 2,
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 2
        }}>
          <Fade in timeout={800}>
            <Container maxWidth="sm">
              <Card sx={{
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(20px)',
                borderRadius: 4,
                boxShadow: '0 32px 64px rgba(0,0,0,0.2)',
                border: '1px solid rgba(255,255,255,0.3)',
              }}>
                <CardContent sx={{ p: isSmallMobile ? 3 : isMobile ? 4 : 6 }}>
                  <Box sx={{ textAlign: 'center', mb: 4 }}>
                    <Box sx={{
                      width: 80,
                      height: 80,
                      mx: 'auto',
                      mb: 3,
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)'
                    }}>
                      <AdminPanelSettings sx={{ fontSize: 40, color: 'white' }} />
                    </Box>
                    <Typography variant="h3" component="h1" fontWeight="700" gutterBottom sx={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      backgroundClip: 'text',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                    }}>
                      管理画面
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ fontSize: '1.1rem' }}>
                      タレントキャスティング診断システム
                    </Typography>
                  </Box>

                  {error && (
                    <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                      {error}
                    </Alert>
                  )}

                  <TextField
                    fullWidth
                    type={showPassword ? 'text' : 'password'}
                    label="パスワード"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                    InputProps={{
                      endAdornment: (
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      ),
                    }}
                    sx={{
                      mb: 4,
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          boxShadow: '0 4px 20px rgba(102, 126, 234, 0.15)',
                        },
                        '&.Mui-focused': {
                          boxShadow: '0 4px 20px rgba(102, 126, 234, 0.25)',
                        }
                      }
                    }}
                  />

                  {/* テスト用自動パスワード入力ボタン（開発環境のみ） */}
                  {process.env.NODE_ENV === 'development' && (
                    <Button
                      variant="text"
                      size="small"
                      onClick={() => setPassword('talent2025admin')}
                      sx={{
                        mb: 2,
                        color: '#6b7280',
                        fontSize: '0.8rem',
                        textTransform: 'none',
                        '&:hover': {
                          backgroundColor: 'rgba(0,0,0,0.04)',
                          color: '#374151'
                        }
                      }}
                    >
                      🔑 テスト用パスワード自動入力
                    </Button>
                  )}

                  <Button
                    fullWidth
                    variant="contained"
                    size="large"
                    onClick={handleLogin}
                    sx={{
                      py: 2.5,
                      mb: 4, // Added more margin below the login button
                      fontSize: '1.2rem',
                      fontWeight: 600,
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      borderRadius: 2,
                      boxShadow: '0 8px 32px rgba(102, 126, 234, 0.4)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                        boxShadow: '0 12px 40px rgba(102, 126, 234, 0.6)',
                        transform: 'translateY(-2px)',
                      },
                    }}
                  >
                    ログイン
                  </Button>
                </CardContent>
              </Card>
            </Container>
          </Fade>
        </Box>
      </Box>
    );
  }

  // 認証後の管理画面
  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* モダンなヘッダーバー */}
      <AppBar
        position="static"
        elevation={0}
        sx={{
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(0,0,0,0.08)',
          color: '#1f2937'
        }}
      >
        <Toolbar sx={{
          py: isMobile ? 1 : 2,
          flexDirection: isMobile ? 'column' : 'row',
          gap: isMobile ? 2 : 0,
          alignItems: isMobile ? 'flex-start' : 'center'
        }}>
          {/* ヘッダーの第1行：アイコンとタイトル */}
          <Box sx={{
            display: 'flex',
            alignItems: 'center',
            width: isMobile ? '100%' : 'auto',
            justifyContent: isMobile ? 'space-between' : 'flex-start'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box sx={{
                width: isMobile ? 36 : 44,
                height: isMobile ? 36 : 44,
                mr: isMobile ? 2 : 3,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
              }}>
                <Analytics sx={{ color: 'white', fontSize: isMobile ? 20 : 24 }} />
              </Box>
              <Typography
                variant="h4"
                component="div"
                sx={{
                  fontWeight: 700,
                  letterSpacing: '-0.5px',
                  background: 'linear-gradient(135deg, #1f2937 0%, #4b5563 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontSize: isMobile ? '1.1rem' : '1.5rem'
                }}
              >
                タレントキャスティング診断
              </Typography>
            </Box>

            {/* モバイルではLogoutボタンを右端に配置 */}
            {isMobile && (
              <Button
                startIcon={<Logout />}
                onClick={handleLogout}
                variant="outlined"
                size="small"
                sx={{
                  minWidth: 'auto',
                  px: 2,
                  py: 1,
                  borderRadius: 2,
                  borderColor: '#fca5a5',
                  color: '#dc2626',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  textTransform: 'none',
                  '&:hover': {
                    backgroundColor: '#fef2f2',
                    borderColor: '#f87171',
                  }
                }}
              >
                Logout
              </Button>
            )}
          </Box>

          {/* ヘッダーの第2行：更新時刻とボタン */}
          <Box sx={{
            display: 'flex',
            alignItems: isMobile ? 'flex-start' : 'center',
            gap: isMobile ? 1 : 2,
            width: isMobile ? '100%' : 'auto',
            flexDirection: isMobile ? 'column' : 'row',
            marginLeft: isMobile ? 0 : 'auto' // デスクトップで右寄せ
          }}>
            {lastRefresh && (
              <Typography variant="body2" sx={{
                color: '#6b7280',
                fontSize: isMobile ? '0.8rem' : '0.85rem',
                fontWeight: 500,
                mb: isMobile ? 0.5 : 0,
                mr: isMobile ? 0 : 2 // デスクトップでボタンとの間隔調整
              }}>
                更新: {lastRefresh.toLocaleString('ja-JP', {
                  timeZone: 'Asia/Tokyo',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </Typography>
            )}

            <Tooltip title="メニューを開く" arrow>
              <IconButton
                sx={{
                  color: '#1f2937',
                  '&:hover': {
                    backgroundColor: 'rgba(31, 41, 55, 0.08)'
                  }
                }}
                onClick={handleMenuOpen}
              >
                <MoreVert />
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      {/* ナビゲーションメニュー */}
      <Menu
        anchorEl={anchorEl}
        open={menuOpen}
        onClose={handleMenuClose}
        PaperProps={{
          elevation: 8,
          sx: {
            mt: 1,
            borderRadius: 2,
            minWidth: 200,
            border: '1px solid rgba(0,0,0,0.08)',
            '& .MuiMenuItem-root': {
              py: 1.5,
              px: 2,
              borderRadius: 1,
              mx: 0.5,
              '&:hover': {
                backgroundColor: '#f8fafc',
              },
            },
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem
          onClick={() => handleMenuAction('refresh')}
          disabled={loading}
        >
          <ListItemIcon>
            <Refresh fontSize="small" sx={{ color: '#6b7280' }} />
          </ListItemIcon>
          <ListItemText>データを更新</ListItemText>
        </MenuItem>

        <MenuItem
          onClick={() => handleMenuAction('export')}
          disabled={formSubmissions.length === 0}
        >
          <ListItemIcon>
            <Download fontSize="small" sx={{ color: '#6b7280' }} />
          </ListItemIcon>
          <ListItemText>CSVエクスポート</ListItemText>
        </MenuItem>

        <Divider sx={{ my: 1 }} />

        <MenuItem onClick={() => handleMenuAction('booking-links')}>
          <ListItemIcon>
            <Settings fontSize="small" sx={{ color: '#7c3aed' }} />
          </ListItemIcon>
          <ListItemText>予約リンク管理</ListItemText>
        </MenuItem>

        <MenuItem onClick={() => handleMenuAction('recommended-talents')}>
          <ListItemIcon>
            <Star fontSize="small" sx={{ color: '#d97706' }} />
          </ListItemIcon>
          <ListItemText>おすすめタレント設定</ListItemText>
        </MenuItem>

        <Divider sx={{ my: 1 }} />

        <MenuItem onClick={() => handleMenuAction('logout')}>
          <ListItemIcon>
            <Logout fontSize="small" sx={{ color: '#dc2626' }} />
          </ListItemIcon>
          <ListItemText sx={{ color: '#dc2626' }}>ログアウト</ListItemText>
        </MenuItem>
      </Menu>

      <Container maxWidth="xl" sx={{ py: isMobile ? 2 : 4, px: isMobile ? 2 : 3 }}>
        {/* シンプルで洗練された統計カード */}
        <Grid container spacing={isMobile ? 1 : 2} sx={{ mb: isMobile ? 3 : 4 }}>
          <Grid size={{ xs: 3, sm: 6, md: 3 }}>
            <Card sx={{
              background: 'rgba(255, 255, 255, 0.8)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(0,0,0,0.06)',
              borderRadius: 2,
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
              transition: 'all 0.2s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 4px 16px rgba(0,0,0,0.08)'
              }
            }}>
              <CardContent sx={{ p: isMobile ? 1.5 : 2.5 }}>
                <Box sx={{
                  display: 'flex',
                  flexDirection: isMobile ? 'column' : 'row',
                  alignItems: isMobile ? 'center' : 'center',
                  justifyContent: isMobile ? 'center' : 'space-between',
                  textAlign: isMobile ? 'center' : 'left'
                }}>
                  <div>
                    <Typography variant="body2" sx={{
                      color: '#6b7280',
                      mb: 0.5,
                      fontSize: isMobile ? '0.6rem' : '0.75rem',
                      fontWeight: 600
                    }}>
                      SUBMISSIONS
                    </Typography>
                    <Typography variant="h5" fontWeight="800" sx={{
                      color: '#111827',
                      fontSize: isMobile ? '1.2rem' : '1.75rem'
                    }}>
                      {formSubmissions.length}
                    </Typography>
                  </div>
                  {!isMobile && (
                    <Box sx={{
                      width: 32,
                      height: 32,
                      background: '#f3f4f6',
                      borderRadius: 1.5,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <People sx={{ fontSize: 16, color: '#6b7280' }} />
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 3, sm: 6, md: 3 }}>
            <Card sx={{
              background: 'rgba(255, 255, 255, 0.8)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(0,0,0,0.06)',
              borderRadius: 2,
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
              transition: 'all 0.2s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 4px 16px rgba(0,0,0,0.08)'
              }
            }}>
              <CardContent sx={{ p: isMobile ? 1.5 : 2.5 }}>
                <Box sx={{
                  display: 'flex',
                  flexDirection: isMobile ? 'column' : 'row',
                  alignItems: isMobile ? 'center' : 'center',
                  justifyContent: isMobile ? 'center' : 'space-between',
                  textAlign: isMobile ? 'center' : 'left'
                }}>
                  <div>
                    <Typography variant="body2" sx={{
                      color: '#6b7280',
                      mb: 0.5,
                      fontSize: isMobile ? '0.6rem' : '0.75rem',
                      fontWeight: 600
                    }}>
                      BOOKINGS
                    </Typography>
                    <Typography variant="h5" fontWeight="800" sx={{
                      color: '#111827',
                      fontSize: isMobile ? '1.2rem' : '1.75rem'
                    }}>
                      {formSubmissions.filter(s => s.button_clicked).length}
                    </Typography>
                  </div>
                  {!isMobile && (
                    <Box sx={{
                      width: 32,
                      height: 32,
                      background: '#f3f4f6',
                      borderRadius: 1.5,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <TrendingUp sx={{ fontSize: 16, color: '#6b7280' }} />
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 3, sm: 6, md: 3 }}>
            <Card sx={{
              background: 'rgba(255, 255, 255, 0.8)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(0,0,0,0.06)',
              borderRadius: 2,
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
              transition: 'all 0.2s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 4px 16px rgba(0,0,0,0.08)'
              }
            }}>
              <CardContent sx={{ p: isMobile ? 1.5 : 2.5 }}>
                <Box sx={{
                  display: 'flex',
                  flexDirection: isMobile ? 'column' : 'row',
                  alignItems: isMobile ? 'center' : 'center',
                  justifyContent: isMobile ? 'center' : 'space-between',
                  textAlign: isMobile ? 'center' : 'left'
                }}>
                  <div>
                    <Typography variant="body2" sx={{
                      color: '#6b7280',
                      mb: 0.5,
                      fontSize: isMobile ? '0.6rem' : '0.75rem',
                      fontWeight: 600
                    }}>
                      CONVERSION
                    </Typography>
                    <Typography variant="h5" fontWeight="800" sx={{
                      color: '#111827',
                      fontSize: isMobile ? '1.2rem' : '1.75rem'
                    }}>
                      {formSubmissions.length > 0
                        ? `${((formSubmissions.filter(s => s.button_clicked).length / formSubmissions.length) * 100).toFixed(1)}%`
                        : '0%'
                      }
                    </Typography>
                  </div>
                  {!isMobile && (
                    <Box sx={{
                      width: 32,
                      height: 32,
                      background: '#f3f4f6',
                      borderRadius: 1.5,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <TouchApp sx={{ fontSize: 16, color: '#6b7280' }} />
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 3, sm: 6, md: 3 }}>
            <Card sx={{
              background: 'rgba(255, 255, 255, 0.8)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(0,0,0,0.06)',
              borderRadius: 2,
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
              transition: 'all 0.2s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 4px 16px rgba(0,0,0,0.08)'
              }
            }}>
              <CardContent sx={{ p: isMobile ? 1.5 : 2.5 }}>
                <Box sx={{
                  display: 'flex',
                  flexDirection: isMobile ? 'column' : 'row',
                  alignItems: isMobile ? 'center' : 'center',
                  justifyContent: isMobile ? 'center' : 'space-between',
                  textAlign: isMobile ? 'center' : 'left'
                }}>
                  <div>
                    <Typography variant="body2" sx={{
                      color: '#6b7280',
                      mb: 0.5,
                      fontSize: isMobile ? '0.6rem' : '0.75rem',
                      fontWeight: 600
                    }}>
                      TODAY
                    </Typography>
                    <Typography variant="h5" fontWeight="800" sx={{
                      color: '#111827',
                      fontSize: isMobile ? '1.2rem' : '1.75rem'
                    }}>
                      {formSubmissions.filter(s => {
                        const submissionDate = new Date(s.created_at);
                        const today = new Date();
                        const submissionJST = submissionDate.toLocaleDateString('ja-JP', { timeZone: 'Asia/Tokyo' });
                        const todayJST = today.toLocaleDateString('ja-JP', { timeZone: 'Asia/Tokyo' });
                        return submissionJST === todayJST;
                      }).length}
                    </Typography>
                  </div>
                  {!isMobile && (
                    <Box sx={{
                      width: 32,
                      height: 32,
                      background: '#f3f4f6',
                      borderRadius: 1.5,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <Today sx={{ fontSize: 16, color: '#6b7280' }} />
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* モダンなデータテーブル */}
        <Fade in timeout={800}>
          <Card sx={{
            borderRadius: 3,
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid rgba(0,0,0,0.05)',
            overflow: 'hidden'
          }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" gutterBottom fontWeight="600" sx={{ mb: 3, color: '#1f2937' }}>
                📊 フォーム送信履歴
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                  {error}
                </Alert>
              )}

              {loading ? (
                <Box sx={{ textAlign: 'center', py: 6 }}>
                  <Typography color="text.secondary">データを読み込み中...</Typography>
                </Box>
              ) : formSubmissions.length === 0 ? (
                <Box sx={{
                  textAlign: 'center',
                  py: 8,
                  background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                  borderRadius: 2,
                  border: '1px solid #e2e8f0'
                }}>
                  <Analytics sx={{ fontSize: 64, color: '#cbd5e1', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    まだフォーム送信がありません
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    診断フォームが送信されるとここに表示されます
                  </Typography>
                </Box>
              ) : isMobile ? (
                // モバイル版: アコーディオン形式のリスト表示
                <Box>
                  {formSubmissions.map((submission, index) => (
                    <Card key={submission.id} sx={{
                      mb: 2,
                      borderRadius: 2,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      '&:hover': {
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                        transform: 'translateY(-2px)',
                        transition: 'all 0.2s ease'
                      }
                    }}>
                      <Accordion>
                        <AccordionSummary
                          expandIcon={<ExpandMore />}
                          sx={{
                            backgroundColor: '#f8fafc',
                            borderBottom: '1px solid #e2e8f0',
                            '& .MuiAccordionSummary-content': {
                              flexDirection: 'column',
                              alignItems: 'flex-start'
                            }
                          }}
                        >
                          <Typography variant="h6" sx={{ fontWeight: 600, color: '#374151', mb: 0.5 }}>
                            {submission.company_name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Today sx={{ fontSize: 14 }} />
                            {formatJapanTime(submission.created_at)}
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails sx={{ pt: 2 }}>
                          <Stack spacing={2}>
                            {/* 基本情報 */}
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Business sx={{ fontSize: 18, color: '#6b7280' }} />
                              <Box>
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                  担当者
                                </Typography>
                                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                  {submission.contact_name}
                                </Typography>
                              </Box>
                            </Box>

                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Email sx={{ fontSize: 18, color: '#6b7280' }} />
                              <Box>
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                  メールアドレス
                                </Typography>
                                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                  {submission.email}
                                </Typography>
                              </Box>
                            </Box>

                            {submission.phone_number && (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Phone sx={{ fontSize: 18, color: '#6b7280' }} />
                                <Box>
                                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                    電話番号
                                  </Typography>
                                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                    {submission.phone_number}
                                  </Typography>
                                </Box>
                              </Box>
                            )}

                            {/* 業界・ターゲット */}
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                              <Chip
                                label={submission.industry}
                                size="small"
                                sx={{ backgroundColor: '#e0f2fe', color: '#0277bd' }}
                              />
                              <Chip
                                label={submission.target_segment}
                                size="small"
                                sx={{ backgroundColor: '#f3e5f5', color: '#7b1fa2' }}
                              />
                              <Chip
                                label={submission.budget_range}
                                size="small"
                                sx={{ backgroundColor: '#e8f5e8', color: '#2e7d32' }}
                              />
                            </Box>

                            {/* ボタンクリック状況 */}
                            <Box sx={{
                              p: 2,
                              backgroundColor: submission.button_clicked ? '#e8f5e8' : '#fff3e0',
                              borderRadius: 1,
                              border: `1px solid ${submission.button_clicked ? '#c8e6c9' : '#ffcc02'}`
                            }}>
                              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                予約ボタン
                              </Typography>
                              <Typography variant="body2" sx={{
                                fontWeight: 600,
                                color: submission.button_clicked ? '#2e7d32' : '#ef6c00'
                              }}>
                                {submission.button_clicked ? 'クリック済み' : 'クリック未'}
                              </Typography>
                              {submission.button_clicked && submission.button_clicked_at && (
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                                  {formatJapanTime(submission.button_clicked_at)}
                                </Typography>
                              )}
                            </Box>

                            {/* 操作ボタン */}
                            <Button
                              variant="outlined"
                              size="small"
                              onClick={() => handleShowDetail(submission)}
                              fullWidth
                              sx={{
                                mt: 2,
                                borderColor: '#3b82f6',
                                color: '#3b82f6',
                                '&:hover': {
                                  backgroundColor: '#3b82f6',
                                  color: 'white'
                                }
                              }}
                            >
                              詳細を表示
                            </Button>
                          </Stack>
                        </AccordionDetails>
                      </Accordion>
                    </Card>
                  ))}
                </Box>
              ) : (
                // デスクトップ版: テーブル表示
                <TableContainer component={Paper} sx={{
                  maxHeight: 600,
                  borderRadius: 2,
                  boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.1)'
                }}>
                  <Table stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{
                          fontWeight: 600,
                          backgroundColor: '#f8fafc',
                          borderBottom: '2px solid #e2e8f0',
                          color: '#374151'
                        }}>
                          送信日時
                        </TableCell>
                        <TableCell sx={{
                          fontWeight: 600,
                          backgroundColor: '#f8fafc',
                          borderBottom: '2px solid #e2e8f0',
                          color: '#374151'
                        }}>
                          会社名
                        </TableCell>
                        <TableCell sx={{
                          fontWeight: 600,
                          backgroundColor: '#f8fafc',
                          borderBottom: '2px solid #e2e8f0',
                          color: '#374151'
                        }}>
                          担当者
                        </TableCell>
                        <TableCell sx={{
                          fontWeight: 600,
                          backgroundColor: '#f8fafc',
                          borderBottom: '2px solid #e2e8f0',
                          color: '#374151'
                        }}>
                          業界
                        </TableCell>
                        <TableCell sx={{
                          fontWeight: 600,
                          backgroundColor: '#f8fafc',
                          borderBottom: '2px solid #e2e8f0',
                          color: '#374151'
                        }}>
                          ターゲット
                        </TableCell>
                        <TableCell sx={{
                          fontWeight: 600,
                          backgroundColor: '#f8fafc',
                          borderBottom: '2px solid #e2e8f0',
                          color: '#374151'
                        }}>
                          予算
                        </TableCell>
                        <TableCell sx={{
                          fontWeight: 600,
                          backgroundColor: '#f8fafc',
                          borderBottom: '2px solid #e2e8f0',
                          color: '#374151'
                        }}>
                          予約ボタン
                        </TableCell>
                        <TableCell sx={{
                          fontWeight: 600,
                          backgroundColor: '#f8fafc',
                          borderBottom: '2px solid #e2e8f0',
                          color: '#374151'
                        }}>
                          操作
                        </TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {formSubmissions.map((submission, index) => (
                        <TableRow
                          key={submission.id}
                          sx={{
                            '&:nth-of-type(odd)': { backgroundColor: '#fafbfc' },
                            '&:hover': {
                              backgroundColor: '#f1f5f9',
                              transition: 'background-color 0.2s ease'
                            },
                            borderBottom: '1px solid #e2e8f0'
                          }}
                        >
                          <TableCell sx={{ fontSize: '0.9rem' }}>
                            {formatJapanTime(submission.created_at)}
                          </TableCell>
                          <TableCell sx={{ fontWeight: 500, color: '#374151' }}>
                            {submission.company_name}
                          </TableCell>
                          <TableCell sx={{ color: '#6b7280' }}>
                            {submission.contact_name}
                          </TableCell>
                          <TableCell sx={{ color: '#6b7280' }}>
                            {submission.industry}
                          </TableCell>
                          <TableCell sx={{ color: '#6b7280' }}>
                            {submission.target_segment}
                          </TableCell>
                          <TableCell sx={{ color: '#6b7280' }}>
                            {submission.budget_range}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={submission.button_clicked ? '✓ クリック済み' : '○ クリックなし'}
                              color={submission.button_clicked ? 'success' : 'default'}
                              size="small"
                              sx={{
                                fontWeight: 500,
                                borderRadius: 2,
                                ...(submission.button_clicked ? {
                                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                                  color: 'white'
                                } : {
                                  background: '#f3f4f6',
                                  color: '#6b7280'
                                })
                              }}
                            />
                            {submission.button_clicked_at && (
                              <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 0.5, fontSize: '0.75rem' }}>
                                {formatJapanTime(submission.button_clicked_at)}
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => handleShowDetail(submission)}
                              sx={{
                                borderRadius: 2,
                                borderColor: '#d1d5db',
                                color: '#6b7280',
                                fontWeight: 500,
                                '&:hover': {
                                  borderColor: '#667eea',
                                  color: '#667eea',
                                  backgroundColor: 'rgba(102, 126, 234, 0.04)'
                                }
                              }}
                            >
                              詳細
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Fade>

      </Container>

      {/* モダンな詳細ダイアログ */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
        fullScreen={isMobile}
        PaperProps={{
          sx: {
            borderRadius: isMobile ? 0 : 3,
            boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
            ...(isMobile && {
              margin: 0,
              maxHeight: '100vh',
              height: '100vh',
            }),
          }
        }}
      >
        <DialogTitle sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          fontWeight: 600,
          py: 3
        }}>
          📋 フォーム送信詳細
        </DialogTitle>
        <DialogContent sx={{ mt: 3, p: 4 }}>
          {selectedSubmission && (
            <Grid container spacing={3}>
              <Grid size={{ xs: 12 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                  送信日時
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {formatJapanTime(selectedSubmission.created_at)}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                  会社名
                </Typography>
                <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>
                  {selectedSubmission.company_name}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                  担当者名
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {selectedSubmission.contact_name}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                  メールアドレス
                </Typography>
                <Tooltip title="クリックしてコピー" arrow>
                  <Typography
                    variant="body1"
                    onClick={() => handleCopyToClipboard(selectedSubmission.email, 'メールアドレス')}
                    sx={{
                      mb: 2,
                      fontFamily: 'monospace',
                      backgroundColor: '#f8fafc',
                      p: 1.5,
                      borderRadius: 2,
                      border: '1px solid #e2e8f0',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: '#e2e8f0',
                        transform: 'translateY(-1px)',
                        boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                      },
                      '&:active': {
                        transform: 'translateY(0)',
                      }
                    }}
                  >
                    {selectedSubmission.email}
                  </Typography>
                </Tooltip>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                  電話番号
                </Typography>
                <Tooltip title="クリックして発信" arrow>
                  <Typography
                    variant="body1"
                    component="a"
                    href={`tel:${selectedSubmission.phone_number}`}
                    sx={{
                      mb: 2,
                      fontFamily: 'monospace',
                      textDecoration: 'none',
                      color: 'inherit',
                      display: 'inline-block',
                      backgroundColor: '#f0f9ff',
                      p: 1.5,
                      borderRadius: 2,
                      border: '1px solid #0ea5e9',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: '#0ea5e9',
                        color: 'white',
                        transform: 'translateY(-1px)',
                        boxShadow: '0 4px 8px rgba(14,165,233,0.3)',
                      },
                      '&:active': {
                        transform: 'translateY(0)',
                      }
                    }}
                  >
                    📞 {selectedSubmission.phone_number}
                  </Typography>
                </Tooltip>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                  業界
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {selectedSubmission.industry}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                  ターゲット層
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {selectedSubmission.target_segment}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                  起用目的
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {selectedSubmission.purpose || '未入力'}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                  予算
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {selectedSubmission.budget_range}
                </Typography>
              </Grid>
              {selectedSubmission.genre_preference && (
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                    ジャンル希望
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {selectedSubmission.genre_preference}
                  </Typography>
                </Grid>
              )}
              {selectedSubmission.preferred_genres && selectedSubmission.preferred_genres.length > 0 && (
                <Grid size={{ xs: 12 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                    起用したいタレントのジャンル
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {selectedSubmission.preferred_genres.join(', ')}
                  </Typography>
                </Grid>
              )}
              <Grid size={{ xs: 12 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                  予約ボタンクリック
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip
                    label={selectedSubmission.button_clicked ? '✓ クリック済み' : '○ クリックなし'}
                    color={selectedSubmission.button_clicked ? 'success' : 'default'}
                    sx={{
                      fontWeight: 500,
                      borderRadius: 2,
                      ...(selectedSubmission.button_clicked ? {
                        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                        color: 'white'
                      } : {})
                    }}
                  />
                  {selectedSubmission.button_clicked_at && (
                    <Typography variant="body2" color="text.secondary">
                      {formatJapanTime(selectedSubmission.button_clicked_at)}
                    </Typography>
                  )}
                </Box>
              </Grid>

              {/* ★ 新規追加: 診断結果セクション */}
              <Grid size={{ xs: 12 }}>
                <Divider sx={{ my: 3 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: '#374151' }}>
                    🎯 診断結果タレント (30名)
                  </Typography>

                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<Download />}
                    onClick={() => handleExportDiagnosisCSV(selectedSubmission)}
                    disabled={diagnosisResults.length === 0 || diagnosisLoading}
                    sx={{
                      borderColor: '#10b981',
                      color: '#10b981',
                      fontWeight: 500,
                      '&:hover': {
                        backgroundColor: '#ecfdf5',
                        borderColor: '#059669',
                        color: '#059669'
                      },
                      '&:disabled': {
                        borderColor: '#d1d5db',
                        color: '#9ca3af'
                      }
                    }}
                  >
                    {diagnosisResults.length > 0
                      ? `診断結果CSV (${diagnosisResults.length}件)`
                      : '診断結果CSV'
                    }
                  </Button>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  診断結果を詳細分析用16項目CSVでダウンロード
                </Typography>

                {diagnosisLoading ? (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 3 }}>
                    <CircularProgress size={20} />
                    <Typography variant="body2" color="text.secondary">
                      診断結果を読み込んでいます...
                    </Typography>
                  </Box>
                ) : diagnosisResults.length > 0 ? (
                  <TableContainer sx={{
                    maxHeight: 400,
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 2,
                    backgroundColor: '#fafafa'
                  }}>
                    <Table size="small" stickyHeader>
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600, backgroundColor: '#f5f5f5' }}>順位</TableCell>
                          <TableCell sx={{ fontWeight: 600, backgroundColor: '#f5f5f5' }}>タレント名</TableCell>
                          <TableCell sx={{ fontWeight: 600, backgroundColor: '#f5f5f5' }}>カテゴリ</TableCell>
                          <TableCell sx={{ fontWeight: 600, backgroundColor: '#f5f5f5' }}>スコア</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {diagnosisResults.map((talent) => (
                          <TableRow
                            key={talent.talent_account_id}
                            sx={{
                              '&:nth-of-type(odd)': { backgroundColor: '#fafbfc' },
                              '&:hover': { backgroundColor: '#f1f5f9' }
                            }}
                          >
                            <TableCell sx={{ fontWeight: 500 }}>
                              {talent.ranking}位
                            </TableCell>
                            <TableCell sx={{ fontWeight: 500, color: '#374151' }}>
                              {talent.talent_name}
                            </TableCell>
                            <TableCell sx={{ color: '#6b7280' }}>
                              {talent.talent_category || '-'}
                            </TableCell>
                            <TableCell sx={{
                              color: '#374151',
                              fontFamily: 'monospace',
                              fontWeight: 500
                            }}>
                              {talent.matching_score.toFixed(1)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Alert
                    severity="info"
                    sx={{
                      mt: 2,
                      borderRadius: 2,
                      backgroundColor: '#e3f2fd',
                      color: '#1565c0'
                    }}
                  >
                    この送信に対する診断結果がまだ記録されていません
                  </Alert>
                )}
              </Grid>

            </Grid>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button
            onClick={() => setDetailDialogOpen(false)}
            variant="contained"
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: 2,
              px: 4,
              py: 1.5,
              fontWeight: 600,
              '&:hover': {
                background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
              }
            }}
          >
            閉じる
          </Button>
        </DialogActions>
      </Dialog>

      {/* コピー通知用のSnackbar */}
      <Snackbar
        open={copySnackbarOpen}
        autoHideDuration={3000}
        onClose={() => setCopySnackbarOpen(false)}
        message={copyMessage}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        sx={{
          '& .MuiSnackbarContent-root': {
            backgroundColor: '#10b981',
            color: 'white',
            borderRadius: 2,
            fontWeight: 500,
          }
        }}
      />
    </Box>
  );
}