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
} from '@mui/material';
import { AttachMoney } from '@mui/icons-material';
import { FormData } from '@/types';

interface FormStep5Props {
  formData: FormData;
  setFormData: (data: FormData) => void;
  errors: Record<string, string>;
}

const budgetRanges = [
  '500万円以下',
  '500万円〜1,000万円',
  '1,000万円〜3,000万円',
  '3,000万円〜5,000万円',
  '5,000万円〜1億円',
  '1億円以上',
];

export function FormStep5({ formData, setFormData, errors }: FormStep5Props) {
  return (
    <Box sx={{ py: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <AttachMoney sx={{ mr: 1.5, fontSize: '2rem', color: 'primary.main' }} />
        <Typography variant="h5" fontWeight={700} color="text.primary">
          予算設定
        </Typography>
      </Box>
      <FormControl error={!!errors.q3_3} fullWidth>
        <FormLabel sx={{ mb: 1.5, fontSize: '1.1rem', fontWeight: 600 }}>
          今回の施策のタレント予算はどの程度ですか？
        </FormLabel>
        <RadioGroup
          value={formData.q3_3}
          onChange={(e) => setFormData({ ...formData, q3_3: e.target.value })}
        >
          {budgetRanges.map((budget) => (
            <FormControlLabel
              key={budget}
              value={budget}
              control={<Radio />}
              label={budget}
              sx={{
                p: 1,
                borderRadius: 2,
                '&:hover': { bgcolor: 'action.hover' },
                transition: 'background-color 0.2s',
              }}
            />
          ))}
        </RadioGroup>
        {errors.q3_3 && <FormHelperText>{errors.q3_3}</FormHelperText>}
      </FormControl>
    </Box>
  );
}