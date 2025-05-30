import React, { useState, useEffect } from 'react';
import {
  Box,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  Wifi as OnlineIcon,
  WifiOff as OfflineIcon,
  Circle as StatusIcon,
} from '@mui/icons-material';
import { useAPI } from '../contexts/APIContext';

interface ConnectionStatusProps {
  isOnline: boolean;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ isOnline }) => {
  const { apiClient } = useAPI();
  const [apiStatus, setApiStatus] = useState<'connected' | 'error' | 'checking'>('checking');

  useEffect(() => {
    if (isOnline) {
      checkAPIHealth();
    } else {
      setApiStatus('error');
    }
  }, [isOnline, apiClient]);

  const checkAPIHealth = async () => {
    try {
      setApiStatus('checking');
      await apiClient.get('/health', { timeout: 5000 });
      setApiStatus('connected');
    } catch (error) {
      console.error('API health check failed:', error);
      setApiStatus('error');
    }
  };

  const getStatusColor = () => {
    if (!isOnline) return 'error';
    switch (apiStatus) {
      case 'connected': return 'success';
      case 'error': return 'error';
      case 'checking': return 'warning';
      default: return 'default';
    }
  };

  const getStatusText = () => {
    if (!isOnline) return 'Offline';
    switch (apiStatus) {
      case 'connected': return 'Connected';
      case 'error': return 'API Error';
      case 'checking': return 'Connecting...';
      default: return 'Unknown';
    }
  };

  const getTooltipText = () => {
    if (!isOnline) return 'No internet connection';
    switch (apiStatus) {
      case 'connected': return 'API server is reachable';
      case 'error': return 'Cannot reach API server';
      case 'checking': return 'Checking API connection';
      default: return 'Connection status unknown';
    }
  };

  return (
    <Tooltip title={getTooltipText()}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Chip
          icon={isOnline ? <OnlineIcon /> : <OfflineIcon />}
          label={getStatusText()}
          color={getStatusColor()}
          size="small"
          variant="outlined"
          sx={{
            // Enhanced green styling for connected state
            ...(apiStatus === 'connected' && isOnline && {
              backgroundColor: '#e8f5e8',
              borderColor: '#4caf50',
              color: '#2e7d32',
              '& .MuiChip-icon': {
                color: '#4caf50',
              },
              '&:hover': {
                backgroundColor: '#d4f4d4',
                borderColor: '#45a049',
              }
            })
          }}
        />
        <StatusIcon
          sx={{
            fontSize: 12,
            color: getStatusColor() === 'success' ? '#4caf50' : 
                   getStatusColor() === 'error' ? 'error.main' : 'warning.main',
            // Enhanced green glow effect for connected state
            ...(apiStatus === 'connected' && isOnline && {
              color: '#4caf50',
              filter: 'drop-shadow(0 0 2px rgba(76, 175, 80, 0.4))',
              animation: 'pulse 2s infinite'
            })
          }}
        />
      </Box>
    </Tooltip>
  );
};

export default ConnectionStatus;
