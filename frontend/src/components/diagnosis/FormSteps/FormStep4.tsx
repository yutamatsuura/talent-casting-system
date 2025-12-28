'use client';

import {
  Box,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormHelperText,
  FormLabel,
  FormGroup,
  Typography,
} from '@mui/material';
import { Psychology } from '@mui/icons-material';
import { FormData } from '@/types';

interface FormStep4Props {
  formData: FormData;
  setFormData: (data: FormData) => void;
  errors: Record<string, string>;
}

const purposeOptions = [
  '認知度向上',
  'ブランディング',
  '商品・サービスの魅力訴求',
  '購入・利用促進',
  '企業イメージの向上',
  '信頼性・安心感の演出',
  'その他',
];

export function FormStep4({ formData, setFormData, errors }: FormStep4Props) {
  return (
    <Box sx={{ py: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <Psychology sx={{ mr: 1.5, fontSize: '2rem', color: 'primary.main' }} />
        <Typography variant="h5" fontWeight={700} color="text.primary">
          起用目的
        </Typography>
      </Box>
      <FormControl error={!!errors.q3_2} fullWidth>
        <FormLabel sx={{ mb: 1.5, fontSize: '1.1rem', fontWeight: 600 }}>
          今回のタレント起用の目的は何ですか？（複数選択可）
        </FormLabel>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
          ※該当する目的をすべて選択してください
        </Typography>
        <FormGroup>
          {purposeOptions.map((purpose) => (
            <FormControlLabel
              key={purpose}
              control={
                <Checkbox
                  checked={formData.q3_2.includes(purpose)}
                  onChange={(e) => {
                    const updatedPurposes = e.target.checked
                      ? [...formData.q3_2, purpose]
                      : formData.q3_2.filter((p) => p !== purpose);
                    setFormData({ ...formData, q3_2: updatedPurposes });
                  }}
                />
              }
              label={purpose}
              sx={{
                p: 1,
                borderRadius: 2,
                '&:hover': { bgcolor: 'action.hover' },
                transition: 'background-color 0.2s',
              }}
            />
          ))}
        </FormGroup>
        {errors.q3_2 && <FormHelperText>{errors.q3_2}</FormHelperText>}
      </FormControl>
    </Box>
  );
}
