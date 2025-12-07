import React from 'react';
import { Box, Container, Typography, AppBar, Toolbar } from '@mui/material';

/**
 * PublicLayout - 公開アクセス専用レイアウト
 * 認証なしのシンプルな構成（requirements.md準拠）
 */
interface PublicLayoutProps {
  children: React.ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  showHeader?: boolean;
}

export function PublicLayout({
  children,
  maxWidth = 'md',
  showHeader = true
}: PublicLayoutProps) {
  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {showHeader && (
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <Typography
              variant="h6"
              component="div"
              sx={{
                flexGrow: 1,
                color: 'primary.main',
                fontWeight: 600
              }}
            >
              タレントキャスティング診断
            </Typography>
          </Toolbar>
        </AppBar>
      )}

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: showHeader ? 2 : 1,
          px: { xs: 0.5, sm: 2 },
        }}
      >
        <Container maxWidth={maxWidth}>
          {children}
        </Container>
      </Box>
    </Box>
  );
}