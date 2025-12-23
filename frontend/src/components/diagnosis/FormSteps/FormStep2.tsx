'use client';

import {
  Box,
  FormControl,
  FormControlLabel,
  FormHelperText,
  FormLabel,
  Radio,
  RadioGroup,
  Typography,
  Paper,
} from '@mui/material';
import { Business } from '@mui/icons-material';
import { FormData } from '@/types';

interface FormStep2Props {
  formData: FormData;
  setFormData: (data: FormData) => void;
  errors: Record<string, string>;
}

const industries = [
  '食品',
  '菓子・氷菓',
  '乳製品',
  '清涼飲料水',
  'アルコール飲料',
  'フードサービス',
  '医薬品・医療・健康食品',
  '化粧品・ヘアケア・オーラルケア',
  'トイレタリー',
  '自動車関連',
  '家電',
  '通信・IT',
  'ゲーム・エンターテイメント・アプリ',
  '流通・通販',
  'ファッション',
  '貴金属',
  '金融・不動産',
  'エネルギー・輸送・交通',
  '教育・出版・公共団体',
  '観光',
];

export function FormStep2({ formData, setFormData, errors }: FormStep2Props) {
  return (
    <Box sx={{ py: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <Business sx={{ mr: 1.5, fontSize: '2rem', color: 'primary.main' }} />
        <Typography variant="h5" fontWeight={700} color="text.primary">
          業界選択
        </Typography>
      </Box>
      <FormControl error={!!errors.q2} fullWidth>
        <FormLabel sx={{ mb: 0.5, fontSize: '1.1rem', fontWeight: 600 }}>
          貴社の業界は次のうちどれにあてはまりますか？
        </FormLabel>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
          ※業界に最適なタレントをご提案するために使用します
        </Typography>
        <Paper
          variant="outlined"
          sx={{
            maxHeight: 400,
            overflowY: 'auto',
            p: 2,
            bgcolor: 'background.paper',
          }}
        >
          <RadioGroup
            value={formData.q2}
            onChange={(e) => setFormData({ ...formData, q2: e.target.value })}
          >
            {industries.map((industry) => (
              <FormControlLabel
                key={industry}
                value={industry}
                control={<Radio />}
                label={industry}
                sx={{ mb: 0.5 }}
              />
            ))}
          </RadioGroup>
        </Paper>
        {errors.q2 && <FormHelperText>{errors.q2}</FormHelperText>}
      </FormControl>
    </Box>
  );
}
