'use client';

import {
  Box,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormHelperText,
  Link,
  Paper,
  Typography,
} from '@mui/material';
import { Security } from '@mui/icons-material';
import { FormData } from '@/types';

interface FormStep6Props {
  formData: FormData;
  setFormData: (data: FormData) => void;
  errors: Record<string, string>;
}

export function FormStep6({ formData, setFormData, errors }: FormStep6Props) {
  return (
    <Box sx={{ py: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <Security sx={{ mr: 1.5, fontSize: '2rem', color: 'primary.main' }} />
        <Typography variant="h5" fontWeight={700} color="text.primary">
          プライバシー同意
        </Typography>
      </Box>

      <Paper
        variant="outlined"
        sx={{
          p: 3,
          mb: 3,
          maxHeight: 300,
          overflowY: 'auto',
          bgcolor: 'grey.50',
        }}
      >
        <Typography variant="body2" paragraph>
          <strong>個人情報の取り扱いについて</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          株式会社e-Spirit（以下「当社」といいます）は、本サービスにおいてお客様からご提供いただく個人情報について、以下の通り取り扱います。
        </Typography>
        <Typography variant="body2" paragraph>
          <strong>1. 個人情報の利用目的</strong>
        </Typography>
        <Typography variant="body2" component="div" paragraph>
          <ul style={{ paddingLeft: '1.5rem' }}>
            <li>タレントキャスティング診断サービスの提供</li>
            <li>診断結果のご案内およびご提案</li>
            <li>お問い合わせへの対応</li>
            <li>サービス向上のための統計データ作成</li>
          </ul>
        </Typography>
        <Typography variant="body2" paragraph>
          <strong>2. 個人情報の第三者提供</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          当社は、法令に基づく場合を除き、お客様の同意なく個人情報を第三者に提供することはありません。
        </Typography>
        <Typography variant="body2" paragraph>
          <strong>3. お問い合わせ窓口</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          個人情報に関するお問い合わせは、以下までご連絡ください。
          <br />
          株式会社e-Spirit
          <br />
          Email: privacy@e-spirit.co.jp
        </Typography>
      </Paper>

      <FormControl error={!!errors.privacyAgreed} fullWidth>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.privacyAgreed}
              onChange={(e) =>
                setFormData({ ...formData, privacyAgreed: e.target.checked })
              }
            />
          }
          label={
            <Typography variant="body2">
              <Link href="#" underline="hover">
                プライバシーポリシー
              </Link>
              に同意します
            </Typography>
          }
        />
        {errors.privacyAgreed && <FormHelperText>{errors.privacyAgreed}</FormHelperText>}
      </FormControl>
    </Box>
  );
}
