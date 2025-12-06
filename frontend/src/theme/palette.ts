import { PaletteOptions } from '@mui/material/styles';

/**
 * カラーパレット設定
 * 既存mockups-v0のOKLCH色空間定義をMUI用に変換
 */
export const palette: PaletteOptions = {
  mode: 'light',
  primary: {
    main: '#3b72d9', // oklch(0.48 0.18 250) プロフェッショナルブルー
    light: '#6390e8',
    dark: '#2854c8',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#f1f5f9', // oklch(0.94 0.01 240) 薄いブルーグレー
    light: '#f8fafc',
    dark: '#e2e8f0',
    contrastText: '#334155',
  },
  background: {
    default: '#fefefe', // oklch(0.99 0.005 240) ほぼ純白
    paper: '#ffffff',   // oklch(1 0 0) 純白（Card背景）
  },
  text: {
    primary: '#1e293b',   // oklch(0.15 0.02 240) メインテキスト
    secondary: '#64748b', // oklch(0.5 0.02 240) セカンダリテキスト
  },
  error: {
    main: '#ef4444', // oklch(0.577 0.245 27.325) エラーカラー
    light: '#f87171',
    dark: '#dc2626',
    contrastText: '#ffffff',
  },
  warning: {
    main: '#f59e0b',
    light: '#fbbf24',
    dark: '#d97706',
    contrastText: '#ffffff',
  },
  info: {
    main: '#3b82f6',
    light: '#60a5fa',
    dark: '#2563eb',
    contrastText: '#ffffff',
  },
  success: {
    main: '#10b981',
    light: '#34d399',
    dark: '#059669',
    contrastText: '#ffffff',
  },
  grey: {
    50: '#f8fafc',   // background gradient start
    100: '#f1f5f9',
    200: '#e2e8f0',  // border color
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
  },
  action: {
    hover: 'rgba(59, 114, 217, 0.04)',
    selected: 'rgba(59, 114, 217, 0.08)',
    disabled: 'rgba(148, 163, 184, 0.38)',
    disabledBackground: 'rgba(148, 163, 184, 0.12)',
  },
  divider: '#e2e8f0', // oklch(0.9 0.01 240)
};