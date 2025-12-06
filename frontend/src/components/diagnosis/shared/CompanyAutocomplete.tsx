'use client';

import { useState, useRef, useEffect } from 'react';
import {
  TextField,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  IconButton,
  InputAdornment,
} from '@mui/material';
import { Business, LocationOn, Edit, ArrowBack } from '@mui/icons-material';
import { companies, type Company } from '@/lib/company-data';

type CompanyAutocompleteProps = {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  label?: string;
  error?: boolean;
  helperText?: string;
};

export function CompanyAutocomplete({
  value,
  onChange,
  placeholder,
  label,
  error,
  helperText,
}: CompanyAutocompleteProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [filteredCompanies, setFilteredCompanies] = useState<Company[]>([]);
  const [isFreeTextMode, setIsFreeTextMode] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (inputValue: string) => {
    onChange(inputValue);

    if (isFreeTextMode) {
      // Free text mode - no autocomplete
      setIsOpen(false);
      return;
    }

    if (inputValue.trim().length > 0) {
      const filtered = companies.filter((company) =>
        company.name.toLowerCase().includes(inputValue.toLowerCase())
      );
      setFilteredCompanies(filtered);

      // Always show dropdown with filtered companies + "その他" option
      setIsOpen(true);
    } else {
      setFilteredCompanies([]);
      setIsOpen(false);
    }
  };

  const handleSelectCompany = (company: Company) => {
    onChange(company.name);
    setIsOpen(false);
    setIsFreeTextMode(false);
  };

  const handleSelectFreeText = () => {
    setIsFreeTextMode(true);
    setIsOpen(false);
    // Keep current value but switch to free text mode
  };

  const handleBackToAutocomplete = () => {
    setIsFreeTextMode(false);
    setIsOpen(false);
    // Trigger autocomplete if there's a value
    if (value.trim().length > 0) {
      const filtered = companies.filter((company) =>
        company.name.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredCompanies(filtered);
      setIsOpen(filtered.length > 0);
    }
  };

  return (
    <Box ref={wrapperRef} sx={{ position: 'relative' }}>
      <TextField
        fullWidth
        label={label}
        value={value}
        onChange={(e) => handleInputChange(e.target.value)}
        onFocus={() => {
          if (!isFreeTextMode && value.trim().length > 0) {
            const filtered = companies.filter((company) =>
              company.name.toLowerCase().includes(value.toLowerCase())
            );
            setFilteredCompanies(filtered);
            setIsOpen(true);
          }
        }}
        placeholder={isFreeTextMode ? "会社名を自由に入力してください" : placeholder}
        error={error}
        helperText={isFreeTextMode ? "手入力モード（制限なし）• オートコンプリートに戻る →" : helperText}
        autoComplete="off"
        InputProps={
          isFreeTextMode
            ? {
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={handleBackToAutocomplete}
                      edge="end"
                      size="small"
                      color="primary"
                      title="オートコンプリートに戻る"
                    >
                      <ArrowBack />
                    </IconButton>
                  </InputAdornment>
                ),
              }
            : undefined
        }
      />

      {isOpen && !isFreeTextMode && (
        <Paper
          elevation={3}
          sx={{
            position: 'absolute',
            zIndex: 50,
            width: '100%',
            mt: 1,
            maxHeight: 300,
            overflowY: 'auto',
          }}
        >
          <List disablePadding>
            {filteredCompanies.map((company) => (
              <ListItem key={company.id} disablePadding divider>
                <ListItemButton onClick={() => handleSelectCompany(company)}>
                  <ListItemIcon>
                    <Business color="action" />
                  </ListItemIcon>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body1" component="div">
                      {company.name}
                    </Typography>
                    <Box component="span" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <LocationOn sx={{ fontSize: 14, color: 'text.secondary' }} />
                      <Typography variant="caption" component="span" color="text.secondary">
                        {company.prefecture} {company.city}
                      </Typography>
                    </Box>
                  </Box>
                </ListItemButton>
              </ListItem>
            ))}

            {/* Add "その他（手入力）" option */}
            <ListItem disablePadding>
              <ListItemButton
                onClick={handleSelectFreeText}
                sx={{
                  backgroundColor: 'action.hover',
                  borderTop: 1,
                  borderColor: 'divider'
                }}
              >
                <ListItemIcon>
                  <Edit color="primary" />
                </ListItemIcon>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body1" component="div" color="primary">
                    その他（手入力）
                  </Typography>
                  <Typography variant="caption" component="span" color="text.secondary">
                    任意の会社名を入力できます
                  </Typography>
                </Box>
              </ListItemButton>
            </ListItem>
          </List>
        </Paper>
      )}
    </Box>
  );
}
