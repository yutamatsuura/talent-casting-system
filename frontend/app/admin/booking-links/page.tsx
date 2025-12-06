'use client';

import { useState, useEffect } from 'react';
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
  Container,
  AppBar,
  Toolbar,
  IconButton,
  Tooltip,
  Snackbar,
  useMediaQuery,
  useTheme,
  List,
  ListItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stack,
  Fade,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  ArrowBack,
  Link as LinkIcon,
  Edit,
  Save,
  Cancel,
  Refresh,
  ExpandMore,
  MoreVert,
  Star,
  Settings,
  Download,
  Logout,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';

// 業界別予約リンクデータの型定義
interface BookingLinkData {
  id: number;
  industry_name: string;
  booking_url: string;
  created_at: string;
  updated_at: string | null;
}

export default function BookingLinksPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const router = useRouter();

  // 認証状態管理
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 業界別予約リンク管理用のstate
  const [bookingLinks, setBookingLinks] = useState<BookingLinkData[]>([]);
  const [editingLinkId, setEditingLinkId] = useState<number | null>(null);
  const [editingLinkUrl, setEditingLinkUrl] = useState('');

  // 通知用のstate
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  // メニュー用のstate
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const menuOpen = Boolean(anchorEl);

  // 認証チェック
  useEffect(() => {
    const savedAuthState = localStorage.getItem('admin_authenticated');
    if (savedAuthState !== 'true') {
      router.push('/admin');
      return;
    }
    setIsAuthenticated(true);
    fetchBookingLinks();
  }, [router]);

  // 業界別予約リンク取得
  const fetchBookingLinks = async () => {
    setLoading(true);
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8432';
      const response = await fetch(`${API_BASE_URL}/api/admin/booking-links`);
      if (!response.ok) throw new Error('業界別予約リンクデータの取得に失敗しました');
      const links = await response.json();
      setBookingLinks(links);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '業界別予約リンクデータの取得に失敗しました');
    } finally {
      setLoading(false);
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

      setSnackbarMessage('予約リンクが正常に更新されました');
      setSnackbarOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予約リンクの更新に失敗しました');
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
        fetchBookingLinks();
        break;
      case 'main-admin':
        router.push('/admin');
        break;
      case 'recommended-talents':
        router.push('/admin/recommended-talents');
        break;
      case 'logout':
        localStorage.removeItem('admin_authenticated');
        router.push('/admin');
        break;
    }
  };

  // 認証されていない場合は何も表示しない
  if (!isAuthenticated) {
    return null;
  }

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
              <Tooltip title="メイン管理画面に戻る" arrow>
                <IconButton
                  edge="start"
                  sx={{
                    mr: 2,
                    color: '#1f2937',
                    '&:hover': {
                      backgroundColor: 'rgba(31, 41, 55, 0.08)'
                    }
                  }}
                  onClick={() => router.push('/admin')}
                >
                  <ArrowBack />
                </IconButton>
              </Tooltip>

              <Box sx={{
                width: isMobile ? 36 : 44,
                height: isMobile ? 36 : 44,
                mr: isMobile ? 2 : 3,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <LinkIcon sx={{
                  color: 'white',
                  fontSize: isMobile ? '1.2rem' : '1.5rem'
                }} />
              </Box>

              <Typography variant="h6" sx={{
                fontWeight: 700,
                letterSpacing: '-0.5px',
                background: 'linear-gradient(135deg, #1f2937 0%, #4b5563 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontSize: isMobile ? '1.1rem' : '1.5rem'
              }}>
                業界別予約リンク管理
              </Typography>
            </Box>

            {/* モバイルではメニューボタンを右端に配置 */}
            {isMobile && (
              <Tooltip title="メニュー" arrow>
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
            )}
          </Box>

          {/* デスクトップではメニューボタンを右側に */}
          {!isMobile && (
            <Box sx={{ display: 'flex', gap: 2, ml: 'auto' }}>
              <Tooltip title="メニュー" arrow>
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
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ pt: 4, pb: 6 }}>
        <Fade in timeout={800}>
          <Card sx={{
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            borderRadius: 3,
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid rgba(0,0,0,0.05)',
            overflow: 'hidden'
          }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h4" gutterBottom fontWeight="600" sx={{ mb: 3, color: '#1f2937' }}>
                🔗 業界別予約リンク管理
              </Typography>

              <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                各業界の診断結果ページで表示される予約ボタンのリンク先を管理できます。
                編集したい業界の「編集」ボタンをクリックして、URLを変更してください。
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                  {error}
                </Alert>
              )}

              {loading ? (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <Typography color="text.secondary" variant="h6">
                    データを読み込み中...
                  </Typography>
                </Box>
              ) : bookingLinks.length === 0 ? (
                <Box sx={{
                  textAlign: 'center',
                  py: 8,
                  background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                  borderRadius: 2,
                  border: '1px solid #e2e8f0'
                }}>
                  <LinkIcon sx={{ fontSize: 64, color: '#cbd5e1', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    業界別予約リンクデータがありません
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    データベースから予約リンク情報を取得できませんでした
                  </Typography>
                </Box>
              ) : isMobile ? (
                // モバイル版: アコーディオン形式
                <Box>
                  {bookingLinks.map((link) => (
                    <Card key={link.id} sx={{
                      mb: 2,
                      borderRadius: 2,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    }}>
                      <Accordion>
                        <AccordionSummary
                          expandIcon={<ExpandMore />}
                          sx={{
                            backgroundColor: '#f8fafc',
                            borderBottom: '1px solid #e2e8f0',
                          }}
                        >
                          <Typography variant="h6" sx={{ fontWeight: 600, color: '#374151' }}>
                            {link.industry_name}
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails sx={{ pt: 2 }}>
                          <Stack spacing={2}>
                            {editingLinkId === link.id ? (
                              <>
                                <TextField
                                  fullWidth
                                  label="予約リンクURL"
                                  value={editingLinkUrl}
                                  onChange={(e) => setEditingLinkUrl(e.target.value)}
                                  multiline
                                  rows={3}
                                  sx={{ mt: 1 }}
                                />
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                  <Button
                                    variant="contained"
                                    color="success"
                                    startIcon={<Save />}
                                    onClick={() => handleSaveBookingLink(link.id)}
                                    size="small"
                                  >
                                    保存
                                  </Button>
                                  <Button
                                    variant="outlined"
                                    startIcon={<Cancel />}
                                    onClick={handleCancelEditBookingLink}
                                    size="small"
                                  >
                                    キャンセル
                                  </Button>
                                </Box>
                              </>
                            ) : (
                              <>
                                <Box>
                                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                    現在の予約リンク
                                  </Typography>
                                  <Typography variant="body2" sx={{
                                    wordBreak: 'break-all',
                                    p: 1,
                                    backgroundColor: '#f3f4f6',
                                    borderRadius: 1,
                                    fontSize: '0.8rem'
                                  }}>
                                    {link.booking_url}
                                  </Typography>
                                </Box>
                                <Button
                                  variant="outlined"
                                  startIcon={<Edit />}
                                  onClick={() => handleEditBookingLink(link)}
                                  size="small"
                                  fullWidth
                                >
                                  編集
                                </Button>
                              </>
                            )}
                          </Stack>
                        </AccordionDetails>
                      </Accordion>
                    </Card>
                  ))}
                </Box>
              ) : (
                // デスクトップ版: テーブル表示
                <TableContainer component={Paper} sx={{
                  borderRadius: 2,
                  boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                  border: '1px solid #e2e8f0'
                }}>
                  <Table stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{
                          fontWeight: 600,
                          backgroundColor: '#f8fafc',
                          color: '#374151',
                          borderBottom: '2px solid #e2e8f0',
                          width: '200px'
                        }}>
                          業界名
                        </TableCell>
                        <TableCell sx={{
                          fontWeight: 600,
                          backgroundColor: '#f8fafc',
                          color: '#374151',
                          borderBottom: '2px solid #e2e8f0'
                        }}>
                          予約リンクURL
                        </TableCell>
                        <TableCell sx={{
                          fontWeight: 600,
                          backgroundColor: '#f8fafc',
                          color: '#374151',
                          borderBottom: '2px solid #e2e8f0',
                          width: '140px'
                        }}>
                          操作
                        </TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {bookingLinks.map((link) => (
                        <TableRow
                          key={link.id}
                          sx={{
                            '&:hover': {
                              backgroundColor: '#f8fafc',
                            },
                            '&:nth-of-type(odd)': {
                              backgroundColor: '#fafbfc',
                            },
                          }}
                        >
                          <TableCell sx={{ fontWeight: 500, color: '#374151', verticalAlign: 'top' }}>
                            {link.industry_name}
                          </TableCell>
                          <TableCell sx={{ verticalAlign: 'top' }}>
                            {editingLinkId === link.id ? (
                              <TextField
                                fullWidth
                                value={editingLinkUrl}
                                onChange={(e) => setEditingLinkUrl(e.target.value)}
                                multiline
                                rows={2}
                                size="small"
                                sx={{ mt: 0.5 }}
                              />
                            ) : (
                              <Typography variant="body2" sx={{
                                wordBreak: 'break-all',
                                color: '#6b7280',
                                fontSize: '0.85rem',
                                lineHeight: 1.4
                              }}>
                                {link.booking_url}
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell sx={{ verticalAlign: 'top' }}>
                            {editingLinkId === link.id ? (
                              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                <Button
                                  variant="contained"
                                  color="success"
                                  startIcon={<Save />}
                                  onClick={() => handleSaveBookingLink(link.id)}
                                  size="small"
                                  fullWidth
                                >
                                  保存
                                </Button>
                                <Button
                                  variant="outlined"
                                  startIcon={<Cancel />}
                                  onClick={handleCancelEditBookingLink}
                                  size="small"
                                  fullWidth
                                >
                                  キャンセル
                                </Button>
                              </Box>
                            ) : (
                              <Button
                                variant="outlined"
                                startIcon={<Edit />}
                                onClick={() => handleEditBookingLink(link)}
                                size="small"
                                fullWidth
                              >
                                編集
                              </Button>
                            )}
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

      {/* 通知用のSnackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
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

      {/* メニューコンポーネント */}
      <Menu
        anchorEl={anchorEl}
        open={menuOpen}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        sx={{
          '& .MuiPaper-root': {
            borderRadius: 2,
            minWidth: 200,
            boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
            border: '1px solid rgba(0,0,0,0.08)',
            mt: 1
          }
        }}
      >
        <MenuItem onClick={() => handleMenuAction('refresh')}>
          <ListItemIcon>
            <Refresh fontSize="small" sx={{ color: '#059669' }} />
          </ListItemIcon>
          <ListItemText>データ更新</ListItemText>
        </MenuItem>

        <Divider sx={{ my: 1 }} />

        <MenuItem onClick={() => handleMenuAction('main-admin')}>
          <ListItemIcon>
            <Settings fontSize="small" sx={{ color: '#7c3aed' }} />
          </ListItemIcon>
          <ListItemText>メイン管理画面</ListItemText>
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
    </Box>
  );
}