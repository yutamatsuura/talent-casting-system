'use client';

import {
  Box,
  Radio,
  FormControl,
  FormControlLabel,
  RadioGroup,
  FormHelperText,
  FormLabel,
  Typography,
} from '@mui/material';
import { People } from '@mui/icons-material';
import { FormData } from '@/types';

interface FormStep2Props {
  formData: FormData;
  setFormData: (data: FormData) => void;
  errors: Record<string, string>;
}

const targetOptions = [
  '男性12-19歳',
  '女性12-19歳',
  '男性20-34歳',
  '女性20-34歳',
  '男性35-49歳',
  '女性35-49歳',
  '男性50-69歳',
  '女性50-69歳',
];

export function FormStep2({ formData, setFormData, errors }: FormStep2Props) {
  const handleTargetChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, q3: event.target.value });
  };

  return (
    <Box sx={{ py: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <People sx={{ mr: 1.5, fontSize: '2rem', color: 'primary.main' }} />
        <Typography variant="h5" fontWeight={700} color="text.primary">
          訴求対象
        </Typography>
      </Box>
      <FormControl error={!!errors.q3} fullWidth>
        <FormLabel sx={{ mb: 0.5, fontSize: '1.1rem', fontWeight: 600 }}>
          貴社の商品サービスの主要なターゲットはどの層ですか？
        </FormLabel>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
          ※1つのターゲット層を選択してください
        </Typography>
        <RadioGroup value={formData.q3} onChange={handleTargetChange}>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
              gap: 1,
            }}
          >
            {targetOptions.map((option) => (
              <FormControlLabel
                key={option}
                value={option}
                control={<Radio />}
                label={option}
                sx={{
                  p: 1,
                  borderRadius: 2,
                  '&:hover': { bgcolor: 'action.hover' },
                }}
              />
            ))}
          </Box>
        </RadioGroup>
        {errors.q3 && <FormHelperText>{errors.q3}</FormHelperText>}
      </FormControl>
    </Box>
  );
}
