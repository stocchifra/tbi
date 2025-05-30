import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  InputAdornment,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Settings as SettingsIcon,
  ExpandMore,
  ExpandLess,
  Key as KeyIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useAPI } from '../contexts/APIContext';
import { useSession } from '../contexts/SessionContext';

const SettingsPanel: React.FC = () => {
  const { isAPIKeySet, setAPIKey, clearAPIKey } = useAPI();
  const { sessionId, resetSession } = useSession();
  const [apiKey, setApiKeyValue] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  const handleSetApiKey = async () => {
    if (!apiKey.trim()) {
      setError('Please enter your OpenAI API key');
      return;
    }

    if (!apiKey.startsWith('sk-')) {
      setError('OpenAI API keys start with "sk-"');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const success = await setAPIKey(apiKey.trim());
      if (success) {
        setSuccess('API key set successfully!');
        setApiKeyValue(''); // Clear the input
      } else {
        setError('Invalid API key. Please check and try again.');
      }
    } catch (error) {
      setError('Failed to set API key. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearApiKey = () => {
    clearAPIKey();
    setApiKeyValue('');
    setSuccess('API key cleared successfully!');
    setError(null);
  };

  const handleResetSession = () => {
    resetSession();
    setSuccess('Session reset successfully!');
    setError(null);
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <SettingsIcon sx={{ mr: 1 }} />
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Settings
        </Typography>
        <IconButton
          onClick={() => setExpanded(!expanded)}
          sx={{ p: 0.5 }}
        >
          {expanded ? <ExpandLess /> : <ExpandMore />}
        </IconButton>
      </Box>

      {/* API Key Status */}
      <Box sx={{ mb: 2 }}>
        {isAPIKeySet ? (
          <Alert
            severity="success"
            action={
              <Button color="inherit" size="small" onClick={handleClearApiKey}>
                Clear
              </Button>
            }
          >
            OpenAI API key is configured
          </Alert>
        ) : (
          <Alert severity="warning">
            OpenAI API key required to use the application
          </Alert>
        )}
      </Box>

      <Collapse in={expanded}>
        <Box>
          {/* API Key Input */}
          {!isAPIKeySet && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                OpenAI API Key
              </Typography>
              <TextField
                fullWidth
                type={showApiKey ? 'text' : 'password'}
                placeholder="sk-..."
                value={apiKey}
                onChange={(e) => setApiKeyValue(e.target.value)}
                disabled={isLoading}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <KeyIcon color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowApiKey(!showApiKey)}
                        edge="end"
                      >
                        {showApiKey ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 1 }}
              />
              <Button
                fullWidth
                variant="contained"
                onClick={handleSetApiKey}
                disabled={isLoading || !apiKey.trim()}
              >
                {isLoading ? 'Setting...' : 'Set API Key'}
              </Button>
              
              <Alert severity="info" sx={{ mt: 2 }} icon={<InfoIcon />}>
                <Typography variant="body2">
                  Your API key is stored securely and only used for this session.
                  Get your key from{' '}
                  <a
                    href="https://platform.openai.com/api-keys"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    OpenAI Platform
                  </a>
                </Typography>
              </Alert>
            </Box>
          )}

          {/* Session Info */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Session Information
            </Typography>
            <List dense>
              <ListItem sx={{ px: 0 }}>
                <ListItemText
                  primary="Session ID"
                  secondary={sessionId.slice(0, 8) + '...'}
                />
                <Chip label="Active" color="success" size="small" />
              </ListItem>
            </List>
            <Button
              variant="outlined"
              color="warning"
              onClick={handleResetSession}
              size="small"
              fullWidth
            >
              Reset Session
            </Button>
          </Box>

          {/* Performance Info */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Performance Target
            </Typography>
            <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
              <Typography variant="body2">
                • Target response time: &lt;3 seconds<br />
                • Cost per query: &lt;$0.01<br />
                • Model: GPT-4o-mini
              </Typography>
            </Alert>
          </Box>
        </Box>
      </Collapse>

      {/* Status Messages */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mt: 2 }}>
          {success}
        </Alert>
      )}
    </Paper>
  );
};

export default SettingsPanel;
