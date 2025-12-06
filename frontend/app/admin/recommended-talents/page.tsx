'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Chip,
  IconButton,
  AppBar,
  Toolbar,
  Container,
  Tooltip,
  Fade,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Grid,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Save as SaveIcon,
  Delete as DeleteIcon,
  ArrowBack as ArrowBackIcon,
  Star as StarIcon,
  MoreVert,
  Refresh,
  Settings as SettingsIcon,
  Logout,
} from '@mui/icons-material';

// 型定義
interface RecommendedTalent {
  id: number;
  industry_name: string;
  talent_id_1: number | null;
  talent_id_2: number | null;
  talent_id_3: number | null;
  talent_1_name: string | null;
  talent_2_name: string | null;
  talent_3_name: string | null;
  created_at: string;
  updated_at: string;
}

interface Industry {
  id: number;
  name: string;
}

export default function RecommendedTalentsPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const router = useRouter();

  // 認証状態
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // データ状態
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [recommendedTalents, setRecommendedTalents] = useState<RecommendedTalent[]>([]);

  // UI状態
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // 一括設定用の状態
  const [bulkSettings, setBulkSettings] = useState({
    talent_id_1: '',
    talent_id_2: '',
    talent_id_3: ''
  });
  const [bulkSaving, setBulkSaving] = useState(false);

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
    initializeData();
  }, [router]);

  const initializeData = async () => {
    try {
      setLoading(true);

      // 必要なデータのみ取得（軽量化）
      const [industriesRes, recommendedRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/industries`),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/recommended-talents`),
      ]);

      if (industriesRes.ok) {
        const industriesData = await industriesRes.json();
        console.log('Industries API response:', industriesData);
        // APIレスポンスの構造を確認して正しく設定
        if (industriesData.industries && Array.isArray(industriesData.industries)) {
          setIndustries(industriesData.industries);
        } else if (Array.isArray(industriesData)) {
          setIndustries(industriesData);
        } else {
          console.error('Industries data is not an array:', industriesData);
          setIndustries([]);
        }
      }

      if (recommendedRes.ok) {
        const recommendedData = await recommendedRes.json();
        console.log('Recommended talents API response:', recommendedData);
        if (Array.isArray(recommendedData)) {
          setRecommendedTalents(recommendedData);
        } else {
          console.error('Recommended talents data is not an array:', recommendedData);
          setRecommendedTalents([]);
        }
      }

    } catch (error) {
      console.error('データ取得エラー:', error);
      // エラーが発生した場合は空配列で初期化
      setIndustries([]);
      setRecommendedTalents([]);
      setMessage({
        type: 'error',
        text: 'データの読み込みに失敗しました'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTalentChange = (industryName: string, position: 1 | 2 | 3, talentId: number | '') => {
    // 既存設定を探す
    const existingIndex = recommendedTalents.findIndex(rt => rt.industry_name === industryName);

    if (existingIndex >= 0) {
      // 更新
      const updated = [...recommendedTalents];
      updated[existingIndex] = {
        ...updated[existingIndex],
        [`talent_id_${position}`]: talentId === '' ? null : talentId,
        [`talent_${position}_name`]: null, // ID入力方式では名前は取得しない
      };
      setRecommendedTalents(updated);
    } else {
      // 新規作成
      const newRecommended: RecommendedTalent = {
        id: 0, // 新規の場合
        industry_name: industryName,
        talent_id_1: position === 1 ? (talentId === '' ? null : talentId) : null,
        talent_id_2: position === 2 ? (talentId === '' ? null : talentId) : null,
        talent_id_3: position === 3 ? (talentId === '' ? null : talentId) : null,
        talent_1_name: null, // ID入力方式では名前は取得しない
        talent_2_name: null, // ID入力方式では名前は取得しない
        talent_3_name: null, // ID入力方式では名前は取得しない
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setRecommendedTalents([...recommendedTalents, newRecommended]);
    }
  };

  const handleSave = async (industryName: string) => {
    try {
      setSaving(industryName);

      const recommended = recommendedTalents.find(rt => rt.industry_name === industryName);
      if (!recommended) return;

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/recommended-talents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          industry_name: industryName,
          talent_id_1: recommended.talent_id_1,
          talent_id_2: recommended.talent_id_2,
          talent_id_3: recommended.talent_id_3,
        }),
      });

      if (response.ok) {
        const updatedData = await response.json();

        // 状態を更新
        const updatedIndex = recommendedTalents.findIndex(rt => rt.industry_name === industryName);
        if (updatedIndex >= 0) {
          const updated = [...recommendedTalents];
          updated[updatedIndex] = updatedData;
          setRecommendedTalents(updated);
        }

        setMessage({
          type: 'success',
          text: `${industryName}のおすすめタレント設定を保存しました`
        });
      } else {
        throw new Error('保存に失敗しました');
      }

    } catch (error) {
      console.error('保存エラー:', error);
      setMessage({
        type: 'error',
        text: '保存に失敗しました'
      });
    } finally {
      setSaving(null);
    }
  };

  const handleDelete = async (industryName: string) => {
    if (!confirm(`${industryName}のおすすめタレント設定を削除しますか？`)) return;

    try {
      setSaving(industryName);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/recommended-talents/${encodeURIComponent(industryName)}`,
        {
          method: 'DELETE',
        }
      );

      if (response.ok) {
        // 状態から削除
        setRecommendedTalents(recommendedTalents.filter(rt => rt.industry_name !== industryName));

        setMessage({
          type: 'success',
          text: `${industryName}のおすすめタレント設定を削除しました`
        });
      } else {
        throw new Error('削除に失敗しました');
      }

    } catch (error) {
      console.error('削除エラー:', error);
      setMessage({
        type: 'error',
        text: '削除に失敗しました'
      });
    } finally {
      setSaving(null);
    }
  };

  const getRecommendedForIndustry = (industryName: string): RecommendedTalent | null => {
    return recommendedTalents.find(rt => rt.industry_name === industryName) || null;
  };

  // 一括設定のハンドラー
  const handleBulkApply = async () => {
    if (!bulkSettings.talent_id_1 && !bulkSettings.talent_id_2 && !bulkSettings.talent_id_3) {
      setMessage({
        type: 'error',
        text: '最低1つのタレントIDを入力してください'
      });
      return;
    }

    if (!confirm('全業界に一括で設定しますか？既存の設定は上書きされます。')) {
      return;
    }

    setBulkSaving(true);
    let successCount = 0;
    let errorCount = 0;

    try {
      for (const industry of industries) {
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/recommended-talents`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              industry_name: industry.name,
              talent_id_1: bulkSettings.talent_id_1 ? parseInt(bulkSettings.talent_id_1, 10) : null,
              talent_id_2: bulkSettings.talent_id_2 ? parseInt(bulkSettings.talent_id_2, 10) : null,
              talent_id_3: bulkSettings.talent_id_3 ? parseInt(bulkSettings.talent_id_3, 10) : null,
            }),
          });

          if (response.ok) {
            const updatedData = await response.json();

            // 状態を更新
            const existingIndex = recommendedTalents.findIndex(rt => rt.industry_name === industry.name);
            if (existingIndex >= 0) {
              const updated = [...recommendedTalents];
              updated[existingIndex] = updatedData;
              setRecommendedTalents(updated);
            } else {
              setRecommendedTalents([...recommendedTalents, updatedData]);
            }
            successCount++;
          } else {
            errorCount++;
          }
        } catch (error) {
          console.error(`業界 ${industry.name} の保存エラー:`, error);
          errorCount++;
        }
      }

      if (errorCount === 0) {
        setMessage({
          type: 'success',
          text: `全${successCount}業界に一括設定を完了しました`
        });
        // 一括設定フィールドをクリア
        setBulkSettings({
          talent_id_1: '',
          talent_id_2: '',
          talent_id_3: ''
        });
      } else {
        setMessage({
          type: 'error',
          text: `${successCount}業界成功、${errorCount}業界失敗しました`
        });
      }

    } finally {
      setBulkSaving(false);
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
        initializeData();
        break;
      case 'main-admin':
        router.push('/admin');
        break;
      case 'booking-links':
        router.push('/admin/booking-links');
        break;
      case 'logout':
        localStorage.removeItem('admin_authenticated');
        router.push('/admin');
        break;
    }
  };

  const renderTalentSelector = (
    industryName: string,
    position: 1 | 2 | 3,
    currentTalentId: number | null
  ) => {
    const recommended = getRecommendedForIndustry(industryName);
    const talentName = recommended ? recommended[`talent_${position}_name` as keyof RecommendedTalent] as string | null : null;

    return (
      <Box sx={{ mb: 1 }}>
        <TextField
          fullWidth
          size="small"
          label={`${position}位おすすめタレント`}
          value={currentTalentId || ''}
          onChange={(e) => {
            const value = e.target.value;
            const numericValue = value === '' ? '' : parseInt(value, 10);
            if (value === '' || (typeof numericValue === 'number' && !isNaN(numericValue) && numericValue > 0)) {
              handleTalentChange(industryName, position, numericValue);
            }
          }}
          placeholder="例: 12345（タレントID）"
          type="number"
          inputProps={{ min: 1, step: 1 }}
          helperText={
            <Box component="span" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: '#6b7280', fontSize: '0.75rem' }}>
              <Box component="span">🆔</Box>
              <Box component="span">タレントのアカウントIDを入力してください</Box>
            </Box>
          }
        />
        {currentTalentId && talentName && (
          <Typography
            variant="body2"
            sx={{
              mt: 0.5,
              px: 1,
              py: 0.5,
              backgroundColor: '#f0f9ff',
              color: '#0369a1',
              borderRadius: 1,
              fontSize: '0.75rem',
              fontWeight: 500,
              border: '1px solid #bae6fd'
            }}
          >
            📍 {talentName}
          </Typography>
        )}
        {currentTalentId && !talentName && (
          <Typography
            variant="body2"
            sx={{
              mt: 0.5,
              px: 1,
              py: 0.5,
              backgroundColor: '#fef3c7',
              color: '#d97706',
              borderRadius: 1,
              fontSize: '0.75rem',
              fontStyle: 'italic',
              border: '1px solid #fcd34d'
            }}
          >
            ⚠️ 保存してタレント名を取得
          </Typography>
        )}
      </Box>
    );
  };

  if (!isAuthenticated || loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
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
                  <ArrowBackIcon />
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
                <StarIcon sx={{
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
                おすすめタレント設定
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
        {/* アラート */}
        {message && (
          <Alert
            severity={message.type}
            onClose={() => setMessage(null)}
            sx={{ mb: 3 }}
          >
            {message.text}
          </Alert>
        )}

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
                ⭐ おすすめタレント設定
              </Typography>

              <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                業界別に最大3名のおすすめタレントを設定できます。
                診断結果では、設定したタレントが上位に「オススメ」ラベル付きで表示されます。
              </Typography>

              <Alert severity="info" sx={{ mb: 4, borderRadius: 2 }}>
                <Typography variant="body2">
                  <strong>自動補完機能:</strong><br />
                  • 1-2名のみ設定した場合、残りは通常マッチング結果の上位から自動補完されます<br />
                  • 未設定の場合は、通常マッチング結果の上位3名が「オススメ」表示されます
                </Typography>
              </Alert>

              {/* 一括設定セクション */}
              <Card sx={{
                mb: 4,
                background: 'linear-gradient(135deg, #fef7cd 0%, #fef3c7 100%)',
                borderRadius: 2,
                border: '2px solid #fbbf24',
                boxShadow: '0 4px 12px rgba(251, 191, 36, 0.15)'
              }}>
                <CardContent sx={{ p: 3 }}>
                  <Box display="flex" alignItems="center" mb={3}>
                    <Box sx={{
                      width: 40,
                      height: 40,
                      mr: 2,
                      background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                      borderRadius: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <Typography sx={{ fontSize: '1.2rem' }}>⚡</Typography>
                    </Box>
                    <Typography variant="h6" sx={{
                      fontWeight: 600,
                      color: '#92400e',
                      fontSize: '1.1rem'
                    }}>
                      全業界一括設定
                    </Typography>
                  </Box>

                  <Typography variant="body2" color="#92400e" sx={{ mb: 3, fontWeight: 500 }}>
                    全業界に同じタレントを一括で設定できます。空欄の場合はその順位は変更されません。
                  </Typography>

                  <Box sx={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 2,
                    mb: 3,
                    '& > *': {
                      flex: '1 1 200px',
                      minWidth: '200px'
                    }
                  }}>
                    <TextField
                      size="small"
                      label="全業界 1位タレント"
                      value={bulkSettings.talent_id_1}
                      onChange={(e) => {
                        const value = e.target.value;
                        if (value === '' || (!isNaN(parseInt(value, 10)) && parseInt(value, 10) > 0)) {
                          setBulkSettings(prev => ({ ...prev, talent_id_1: value }));
                        }
                      }}
                      placeholder="例: 12345"
                      type="number"
                      inputProps={{ min: 1, step: 1 }}
                      helperText="1位に設定するタレントID"
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          backgroundColor: 'rgba(255, 255, 255, 0.8)'
                        }
                      }}
                    />
                    <TextField
                      size="small"
                      label="全業界 2位タレント"
                      value={bulkSettings.talent_id_2}
                      onChange={(e) => {
                        const value = e.target.value;
                        if (value === '' || (!isNaN(parseInt(value, 10)) && parseInt(value, 10) > 0)) {
                          setBulkSettings(prev => ({ ...prev, talent_id_2: value }));
                        }
                      }}
                      placeholder="例: 23456"
                      type="number"
                      inputProps={{ min: 1, step: 1 }}
                      helperText="2位に設定するタレントID"
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          backgroundColor: 'rgba(255, 255, 255, 0.8)'
                        }
                      }}
                    />
                    <TextField
                      size="small"
                      label="全業界 3位タレント"
                      value={bulkSettings.talent_id_3}
                      onChange={(e) => {
                        const value = e.target.value;
                        if (value === '' || (!isNaN(parseInt(value, 10)) && parseInt(value, 10) > 0)) {
                          setBulkSettings(prev => ({ ...prev, talent_id_3: value }));
                        }
                      }}
                      placeholder="例: 34567"
                      type="number"
                      inputProps={{ min: 1, step: 1 }}
                      helperText="3位に設定するタレントID"
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          backgroundColor: 'rgba(255, 255, 255, 0.8)'
                        }
                      }}
                    />
                  </Box>

                  <Box display="flex" justifyContent="center">
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={bulkSaving ? <CircularProgress size={20} color="inherit" /> : <Typography sx={{ fontSize: '1.1rem' }}>⚡</Typography>}
                      onClick={handleBulkApply}
                      disabled={bulkSaving || (!bulkSettings.talent_id_1 && !bulkSettings.talent_id_2 && !bulkSettings.talent_id_3)}
                      sx={{
                        background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                        color: 'white',
                        fontWeight: 600,
                        px: 4,
                        py: 1.5,
                        borderRadius: 2,
                        textTransform: 'none',
                        fontSize: '1rem',
                        boxShadow: '0 4px 12px rgba(245, 158, 11, 0.3)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #d97706 0%, #b45309 100%)',
                          boxShadow: '0 6px 16px rgba(245, 158, 11, 0.4)',
                        }
                      }}
                    >
                      {bulkSaving ? '設定中...' : `全${industries.length}業界に一括適用`}
                    </Button>
                  </Box>
                </CardContent>
              </Card>

              {/* 業界別設定 - Flexbox レイアウト */}
              <Box sx={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 3,
                '& > *': {
                  flex: '1 1 300px',
                  minWidth: '300px',
                  maxWidth: {
                    xs: '100%',
                    sm: 'calc(50% - 12px)',
                    md: 'calc(33.333% - 16px)'
                  }
                }
              }}>
                {industries.map((industry) => {
                  const recommended = getRecommendedForIndustry(industry.name);
                  const isSaving = saving === industry.name;

                  return (
                    <Card
                      key={industry.id}
                      sx={{
                        borderRadius: 2,
                        boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                        border: '1px solid #e2e8f0',
                        '&:hover': {
                          boxShadow: '0 4px 20px rgba(0,0,0,0.12)',
                        }
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                          <Typography variant="subtitle1" component="h2" sx={{
                            fontWeight: 600,
                            color: '#374151',
                            fontSize: '1rem'
                          }}>
                            {industry.name}
                          </Typography>
                          {recommended && (
                            <Chip
                              label={`${[recommended.talent_id_1, recommended.talent_id_2, recommended.talent_id_3]
                                .filter(id => id !== null).length}名設定済み`}
                              size="small"
                              color="primary"
                              sx={{ borderRadius: 1, fontSize: '0.75rem' }}
                            />
                          )}
                        </Box>

                        <Box sx={{ mb: 3 }}>
                          {renderTalentSelector(industry.name, 1, recommended?.talent_id_1 || null)}
                          {renderTalentSelector(industry.name, 2, recommended?.talent_id_2 || null)}
                          {renderTalentSelector(industry.name, 3, recommended?.talent_id_3 || null)}
                        </Box>

                        <Box display="flex" gap={1} justifyContent="flex-end">
                          <Button
                            variant="contained"
                            startIcon={isSaving ? <CircularProgress size={16} /> : <SaveIcon />}
                            onClick={() => handleSave(industry.name)}
                            disabled={isSaving}
                            size="small"
                            sx={{
                              borderRadius: 2,
                              textTransform: 'none',
                              fontWeight: 600,
                            }}
                          >
                            保存
                          </Button>
                          {recommended && (
                            <Button
                              variant="outlined"
                              color="error"
                              startIcon={<DeleteIcon />}
                              onClick={() => handleDelete(industry.name)}
                              disabled={isSaving}
                              size="small"
                              sx={{
                                borderRadius: 2,
                                textTransform: 'none',
                                fontWeight: 500,
                              }}
                            >
                              削除
                            </Button>
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  );
                })}
              </Box>

              {industries.length === 0 && (
                <Box sx={{
                  textAlign: 'center',
                  py: 8,
                  background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                  borderRadius: 2,
                  border: '1px solid #e2e8f0'
                }}>
                  <StarIcon sx={{ fontSize: 64, color: '#cbd5e1', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    業界データが見つかりませんでした
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    データベースから業界情報を取得できませんでした
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Fade>
      </Container>

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
            <SettingsIcon fontSize="small" sx={{ color: '#7c3aed' }} />
          </ListItemIcon>
          <ListItemText>メイン管理画面</ListItemText>
        </MenuItem>

        <MenuItem onClick={() => handleMenuAction('booking-links')}>
          <ListItemIcon>
            <StarIcon fontSize="small" sx={{ color: '#0ea5e9' }} />
          </ListItemIcon>
          <ListItemText>業界別予約リンク管理</ListItemText>
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