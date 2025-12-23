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
import { Gavel } from '@mui/icons-material';
import { FormData } from '@/types';

interface FormStepTermsProps {
  formData: FormData;
  setFormData: (data: FormData) => void;
  errors: Record<string, string>;
}

export function FormStepTerms({ formData, setFormData, errors }: FormStepTermsProps) {
  return (
    <Box sx={{ py: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <Gavel sx={{ mr: 1.5, fontSize: '2rem', color: 'primary.main' }} />
        <Typography variant="h5" fontWeight={700} color="text.primary">
          注意事項・利用規約
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
          <strong>■注意事項</strong>
        </Typography>
        <Typography variant="body2" component="div" paragraph>
          <ul style={{ paddingLeft: '0', listStyle: 'none' }}>
            <li style={{ marginBottom: '8px' }}>
              ・本診断は、入力された情報に基づき、当社独自の基準およびアルゴリズムにより分析した参考情報を提供するものであり、特定のタレントの出演、起用、契約の成立を保証するものではありません。
            </li>
            <li style={{ marginBottom: '8px' }}>
              ・本サービス上に表示されるタレント情報は、当社が当該タレントの出演交渉権、独占的使用権、出演確約等を有することを意味するものではありません。
            </li>
            <li style={{ marginBottom: '8px' }}>
              ・出演可否、出演条件、出演料等は、タレント本人または所属事務所等の意向により変更される場合があります。
            </li>
            <li style={{ marginBottom: '8px' }}>
              ・本診断結果は、当社独自のロジックに基づくものであり、その正確性、完全性、有用性、最新性を保証するものではありません。
            </li>
            <li style={{ marginBottom: '8px' }}>
              ・本サービスの利用により成立した取引実績として、当社は、利用者の企業名およびロゴを当社サービスサイト、営業資料等に掲載する場合があります。
            </li>
            <li style={{ marginBottom: '8px' }}>
              ・本診断結果の利用により生じた損害について、当社は一切の責任を負いません。
            </li>
            <li style={{ marginBottom: '8px' }}>
              ・詳細については、利用規約をご確認ください。
            </li>
          </ul>
        </Typography>
      </Paper>

      <FormControl error={!!errors.termsAgreed} fullWidth>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.termsAgreed || false}
              onChange={(e) =>
                setFormData({ ...formData, termsAgreed: e.target.checked })
              }
            />
          }
          label={
            <Typography variant="body2">
              上記の
              <Link href="#" underline="hover">
                注意事項・利用規約
              </Link>
              に同意します
            </Typography>
          }
        />
        {errors.termsAgreed && <FormHelperText>{errors.termsAgreed}</FormHelperText>}
      </FormControl>
    </Box>
  );
}