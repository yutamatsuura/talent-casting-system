'use client';

import {
  Box,
  FormControl,
  FormControlLabel,
  FormHelperText,
  FormLabel,
  Radio,
  RadioGroup,
  TextField,
  Typography,
} from '@mui/material';
import { Lightbulb } from '@mui/icons-material';
import { FormData } from '@/types';

interface FormStep3Props {
  formData: FormData;
  setFormData: (data: FormData) => void;
  errors: Record<string, string>;
}

const reasons = [
  '商品サービスの知名度アップ',
  '商品サービスの売上拡大',
  '商品サービスの特長訴求のため',
  '企業知名度アップ',
  '企業好感度アップ',
  '採用効果アップ',
  'その他',
];

export function FormStep3({ formData, setFormData, errors }: FormStep3Props) {
  const isOtherSelected = formData.q3_2 === 'その他' || (formData.q3_2 && !reasons.slice(0, -1).includes(formData.q3_2));
  const isPresetReason = reasons.slice(0, -1).includes(formData.q3_2);

  const handleRadioChange = (value: string) => {
    setFormData({ ...formData, q3_2: value });
  };

  const handleCustomTextChange = (text: string) => {
    setFormData({ ...formData, q3_2: text || 'その他' });
  };

  return (
    <Box sx={{ py: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <Lightbulb sx={{ mr: 1.5, fontSize: '2rem', color: 'primary.main' }} />
        <Typography variant="h5" fontWeight={700} color="text.primary">
          起用目的
        </Typography>
      </Box>
      <FormControl error={!!errors.q3_2} fullWidth>
        <FormLabel sx={{ mb: 1.5, fontSize: '1.1rem', fontWeight: 600 }}>
          タレント起用を検討する一番の理由はなんですか？
        </FormLabel>
        <RadioGroup
          value={formData.q3_2 || ''}
          onChange={(e) => handleRadioChange(e.target.value)}
        >
          {reasons.map((reason) => (
            <FormControlLabel
              key={reason}
              value={reason}
              control={<Radio />}
              label={reason}
              sx={{
                p: 1,
                borderRadius: 2,
                '&:hover': { bgcolor: 'action.hover' },
                transition: 'background-color 0.2s',
              }}
            />
          ))}
        </RadioGroup>
        {isOtherSelected && (
          <TextField
            fullWidth
            placeholder="具体的な理由をお聞かせください"
            value={isPresetReason ? '' : formData.q3_2.replace('その他', '').trim()}
            onChange={(e) => handleCustomTextChange(e.target.value)}
            sx={{ mt: 2 }}
            variant="outlined"
            multiline
            rows={3}
          />
        )}
        {errors.q3_2 && <FormHelperText>{errors.q3_2}</FormHelperText>}
      </FormControl>
    </Box>
  );
}
