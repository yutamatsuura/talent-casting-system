import { createTheme } from '@mui/material/styles';
import { palette } from './palette';
import { typography } from './typography';
import { components } from './components';

/**
 * タレントキャスティングシステム MUIテーマ
 * 既存mockups-v0のプロフェッショナルブルー配色を基に構築
 */
export const theme = createTheme({
  palette,
  typography,
  components,
  shape: {
    borderRadius: 8, // 0.5rem相当
  },
  spacing: 8,
});

export default theme;