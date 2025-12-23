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

interface FormStep7Props {
  formData: FormData;
  setFormData: (data: FormData) => void;
  errors: Record<string, string>;
}

export function FormStep7({ formData, setFormData, errors }: FormStep7Props) {
  return (
    <Box sx={{ py: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <Security sx={{ mr: 1.5, fontSize: '2rem', color: 'primary.main' }} />
        <Typography variant="h5" fontWeight={700} color="text.primary">
          プライバシーポリシー
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
          <strong>プライバシーポリシー</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          株式会社e-Spirit（以下「当社」といいます）は、本サービスにおいてお客様からご提供いただく個人情報について、以下の通り取り扱います。
        </Typography>

        <Typography variant="body2" paragraph>
          <strong>第1条（個人情報の定義）</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          「個人情報」とは、個人情報保護法にいう「個人情報」を指すものとし、生存する個人に関する情報であって、当該情報に含まれる氏名、生年月日、住所、電話番号、連絡先その他の記述等により特定の個人を識別できる情報を指します。
        </Typography>

        <Typography variant="body2" paragraph>
          <strong>第2条（個人情報の収集方法）</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          当社は、お客様が利用登録をする際に氏名、メールアドレス、電話番号等の個人情報をお尋ねすることがあります。
        </Typography>

        <Typography variant="body2" paragraph>
          <strong>第3条（個人情報を収集・利用する目的）</strong>
        </Typography>
        <Typography variant="body2" component="div" paragraph>
          当社が個人情報を収集・利用する目的は、以下のとおりです。
          <ul style={{ paddingLeft: '1.5rem' }}>
            <li>タレントキャスティング診断サービスの提供のため</li>
            <li>診断結果のご案内およびご提案のため</li>
            <li>お客様からのお問い合わせに回答するため</li>
            <li>当社のサービスに関するご案内をするため</li>
            <li>サービス向上のための統計データ作成のため</li>
            <li>メンテナンス、重要なお知らせなど必要に応じたご連絡のため</li>
          </ul>
        </Typography>

        <Typography variant="body2" paragraph>
          <strong>第4条（利用目的の変更）</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          当社は、利用目的が変更前と関連性を有すると合理的に認められる場合に限り、個人情報の利用目的を変更するものとします。
        </Typography>

        <Typography variant="body2" paragraph>
          <strong>第5条（個人情報の第三者提供）</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          当社は、次に掲げる場合を除いて、あらかじめお客様の同意を得ることなく、第三者に個人情報を提供することはありません。
        </Typography>

        <Typography variant="body2" paragraph>
          <strong>第6条（個人情報の開示）</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          当社は、お客様ご本人から個人情報の開示を求められたときは、遅滞なく開示いたします。
        </Typography>

        <Typography variant="body2" paragraph>
          <strong>第7条（個人情報の訂正および削除）</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          お客様は、当社の保有する自己の個人情報が誤った情報である場合には、当社が定める手続きにより、当社に対して個人情報の訂正、追加または削除を請求することができます。
        </Typography>

        <Typography variant="body2" paragraph>
          <strong>第8条（個人情報の利用停止等）</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          当社は、お客様本人から、個人情報が、利用目的の範囲を超えて取り扱われているという理由、または不正の手段により取得されたものであるという理由により、その利用の停止または消去を求められた場合には、遅滞なく必要な調査を行います。
        </Typography>

        <Typography variant="body2" paragraph>
          <strong>第9条（プライバシーポリシーの変更）</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          本ポリシーの内容は、法令その他本ポリシーに別段の定めのある事項を除いて、お客様に通知することなく、変更することができるものとします。
        </Typography>

        <Typography variant="body2" paragraph>
          <strong>第10条（お問い合わせ窓口）</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          本ポリシーに関するお問い合わせは、以下の窓口までお願いいたします。
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
