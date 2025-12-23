'use client';

import {
  Box,
  TextField,
  Typography,
  FormLabel,
  Button,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  FormControl
} from '@mui/material';
import { Domain, Science } from '@mui/icons-material';
import { FormData } from '@/types';

// 企業情報のテストデータ
const testCompanyData = {
  q4: '株式会社テストクライアント',
  q5: 'テスト太郎',
  q6: 'test@talent-casting-dev.local',
  q7: '090-1234-5678',
  q7_2: '希望ジャンルあり',
  q7_2_genres: ['俳優', 'アーティスト'],
};

interface FormStep6Props {
  formData: FormData;
  setFormData: (data: FormData) => void;
  errors: Record<string, string>;
}

export function FormStep6({ formData, setFormData, errors }: FormStep6Props) {
  // 企業情報のテストデータ自動入力
  const handleFillTestCompanyData = () => {
    setFormData({
      ...formData,
      ...testCompanyData,
    });
  };

  return (
    <Box sx={{ py: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <Domain sx={{ mr: 1.5, fontSize: '2rem', color: 'primary.main' }} />
        <Typography variant="h5" fontWeight={700} color="text.primary">
          企業情報入力
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
        <FormLabel sx={{ fontSize: '1.1rem', fontWeight: 600 }}>
          貴社の情報を教えてください
        </FormLabel>

        {/* 開発テスト用ボタン */}
        {process.env.NODE_ENV === 'development' && (
          <Button
            variant="outlined"
            size="small"
            startIcon={<Science />}
            onClick={handleFillTestCompanyData}
            sx={{
              borderColor: '#ff9800',
              color: '#ff9800',
              fontSize: '0.75rem',
              fontWeight: 'bold',
              '&:hover': {
                borderColor: '#f57c00',
                backgroundColor: 'rgba(255, 152, 0, 0.04)',
              },
            }}
          >
            🧪 テストデータ入力
          </Button>
        )}
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 3 }}>
        <TextField
          fullWidth
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              会社名
              <Typography component="span" sx={{ color: 'error.main', fontSize: '0.875rem' }}>
                ※
              </Typography>
            </Box>
          }
          value={formData.q4}
          onChange={(e) => setFormData({ ...formData, q4: e.target.value })}
          placeholder="例：株式会社〇〇"
          error={!!errors.q4}
          helperText={errors.q4}
        />

        <TextField
          fullWidth
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              担当者名
              <Typography component="span" sx={{ color: 'error.main', fontSize: '0.875rem' }}>
                ※
              </Typography>
            </Box>
          }
          placeholder="山田 太郎"
          value={formData.q5}
          onChange={(e) => setFormData({ ...formData, q5: e.target.value })}
          error={!!errors.q5}
          helperText={errors.q5}
        />

        <TextField
          fullWidth
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              メールアドレス
              <Typography component="span" sx={{ color: 'error.main', fontSize: '0.875rem' }}>
                ※
              </Typography>
            </Box>
          }
          type="email"
          placeholder="example@company.com"
          value={formData.q6}
          onChange={(e) => setFormData({ ...formData, q6: e.target.value })}
          error={!!errors.q6}
          helperText={errors.q6 || "※タレントリストをお送りしますので、正確にご記入ください。"}
        />

        <TextField
          fullWidth
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              携帯電話番号
              <Typography component="span" sx={{ color: 'error.main', fontSize: '0.875rem' }}>
                ※
              </Typography>
            </Box>
          }
          type="tel"
          placeholder="例：090-1234-5678"
          value={formData.q7}
          onChange={(e) => setFormData({ ...formData, q7: e.target.value })}
          error={!!errors.q7}
          helperText={errors.q7}
        />

        {/* ジャンル希望選択 */}
        <Box sx={{ mt: 2 }}>
          <Box sx={{ mb: 1 }}>
            <FormLabel sx={{ fontSize: '1rem', fontWeight: 600, display: 'block' }}>
              起用したいタレントのジャンル（俳優・アーティスト等）はありますか？
            </FormLabel>
            <Typography component="span" sx={{ color: 'error.main', fontSize: '0.875rem', ml: 0.5 }}>
              ※
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            ※AIの診断結果には影響しません
          </Typography>

          <FormControl component="fieldset" error={!!errors.q7_2}>
            <RadioGroup
              value={formData.q7_2}
              onChange={(e) => {
                const value = e.target.value;
                setFormData({
                  ...formData,
                  q7_2: value,
                  q7_2_genres: value === '希望ジャンルなし' ? [] : formData.q7_2_genres,
                });
              }}
            >
              <FormControlLabel
                value="希望ジャンルなし"
                control={<Radio />}
                label="希望ジャンルなし"
                sx={{ '& .MuiFormControlLabel-label': { fontWeight: 'normal' } }}
              />
              <FormControlLabel
                value="希望ジャンルあり"
                control={<Radio />}
                label="希望ジャンルあり"
                sx={{ '& .MuiFormControlLabel-label': { fontWeight: 'normal' } }}
              />
            </RadioGroup>
            {/* ジャンル選択のエラー表示 */}
            {errors.q7_2 && (
              <Typography variant="body2" color="error" sx={{ mt: 1, ml: 2, fontSize: '0.75rem' }}>
                {errors.q7_2}
              </Typography>
            )}
          </FormControl>

          {/* 具体的ジャンル選択（希望ジャンルありの場合のみ表示） */}
          {formData.q7_2 === '希望ジャンルあり' && (
            <Box sx={{ ml: 6, mt: 2 }}>
              {[
                '俳優',
                'モデル',
                'アーティスト',
                '声優・ナレーター',
                'アイドル',
                'お笑い芸人',
                'アスリート',
              ].map((genre) => (
                <FormControlLabel
                  key={genre}
                  control={
                    <Checkbox
                      checked={Array.isArray(formData.q7_2_genres) && formData.q7_2_genres.includes(genre)}
                      onChange={(e) => {
                        const currentGenres = Array.isArray(formData.q7_2_genres) ? formData.q7_2_genres : [];
                        if (e.target.checked) {
                          setFormData({ ...formData, q7_2_genres: [...currentGenres, genre] });
                        } else {
                          setFormData({ ...formData, q7_2_genres: currentGenres.filter((g) => g !== genre) });
                        }
                      }}
                    />
                  }
                  label={genre}
                  sx={{
                    display: 'flex',
                    mb: 1,
                    '& .MuiFormControlLabel-label': { fontWeight: 'normal' },
                  }}
                />
              ))}
              {/* ジャンル選択のエラー表示 */}
              {errors.q7_2_genres && (
                <Typography variant="body2" color="error" sx={{ mt: 1, fontSize: '0.75rem' }}>
                  {errors.q7_2_genres}
                </Typography>
              )}
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
}
