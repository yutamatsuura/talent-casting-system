import { Components, Theme } from '@mui/material/styles';

/**
 * MUIコンポーネント設定
 * 既存mockups-v0のCard中心デザインを再現
 */
export const components: Components<Omit<Theme, 'components'>> = {
  MuiCssBaseline: {
    styleOverrides: {
      body: {
        background: 'linear-gradient(135deg, #f8fafc 0%, #ffffff 50%, #f3e8ff 100%)',
        minHeight: '100vh',
      },
    },
  },

  MuiCard: {
    styleOverrides: {
      root: {
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        borderRadius: '0.5rem',
        border: 'none',
      },
    },
  },

  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: '0.5rem',
        textTransform: 'none',
        fontWeight: 500,
        padding: '0.75rem 1.5rem',
      },
      contained: {
        background: 'linear-gradient(135deg, #3b72d9 0%, #6390e8 100%)',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        '&:hover': {
          background: 'linear-gradient(135deg, #2854c8 0%, #3b72d9 100%)',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        },
      },
      outlined: {
        borderColor: '#e2e8f0',
        color: '#3b72d9',
        '&:hover': {
          backgroundColor: 'rgba(59, 114, 217, 0.04)',
          borderColor: '#3b72d9',
        },
      },
    },
  },

  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: '0.5rem',
          backgroundColor: '#ffffff',
          '& fieldset': {
            borderColor: '#e2e8f0',
          },
          '&:hover fieldset': {
            borderColor: '#cbd5e1',
          },
          '&.Mui-focused fieldset': {
            borderColor: '#3b72d9',
          },
        },
      },
    },
  },

  MuiFormControlLabel: {
    styleOverrides: {
      root: {
        '&:hover': {
          backgroundColor: 'rgba(59, 114, 217, 0.04)',
          borderRadius: '0.5rem',
        },
      },
    },
  },

  MuiRadio: {
    styleOverrides: {
      root: {
        color: '#cbd5e1',
        '&.Mui-checked': {
          color: '#3b72d9',
        },
      },
    },
  },

  MuiCheckbox: {
    styleOverrides: {
      root: {
        color: '#cbd5e1',
        '&.Mui-checked': {
          color: '#3b72d9',
        },
      },
    },
  },

  MuiLinearProgress: {
    styleOverrides: {
      root: {
        height: 8,
        borderRadius: 4,
        backgroundColor: '#f1f5f9',
      },
      bar: {
        borderRadius: 4,
        background: 'linear-gradient(90deg, #3b72d9 0%, #8b5cf6 100%)',
      },
    },
  },

  MuiPaper: {
    styleOverrides: {
      root: {
        borderRadius: '0.5rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
      },
    },
  },

  MuiAppBar: {
    styleOverrides: {
      root: {
        backgroundColor: '#ffffff',
        color: '#1e293b',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        borderBottom: '1px solid #e2e8f0',
      },
    },
  },

  MuiDrawer: {
    styleOverrides: {
      paper: {
        borderRight: '1px solid #e2e8f0',
        backgroundColor: '#fefefe',
      },
    },
  },

  MuiListItemButton: {
    styleOverrides: {
      root: {
        borderRadius: '0.5rem',
        margin: '0 0.5rem',
        '&:hover': {
          backgroundColor: 'rgba(59, 114, 217, 0.04)',
        },
        '&.Mui-selected': {
          backgroundColor: 'rgba(59, 114, 217, 0.08)',
          '&:hover': {
            backgroundColor: 'rgba(59, 114, 217, 0.12)',
          },
        },
      },
    },
  },
};