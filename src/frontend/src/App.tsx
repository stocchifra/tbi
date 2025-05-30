import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Alert,
} from '@mui/material';
import ChatInterface from './components/ChatInterface';
import DocumentUploader from './components/DocumentUploader';
import SettingsPanel from './components/SettingsPanel';
import ConnectionStatus from './components/ConnectionStatus';
import { SessionProvider } from './contexts/SessionContext';
import { APIProvider } from './contexts/APIContext';
import { DocumentProvider } from './contexts/DocumentContext';
import './App.css';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SessionProvider>
        <APIProvider>
          <DocumentProvider>
          <div className="App">
            <AppBar position="static" elevation={1}>
              <Toolbar>
                <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                  AI Document Analysis
                </Typography>
                <ConnectionStatus isOnline={isOnline} />
              </Toolbar>
            </AppBar>

            <Container maxWidth="xl" sx={{ py: 2 }}>
              {!isOnline && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  No internet connection. Please check your connection and try again.
                </Alert>
              )}

              <Box sx={{ display: 'flex', gap: 2, height: 'calc(100vh - 120px)' }}>
                {/* Left Panel - Document Upload & Settings */}
                <Box sx={{ width: 350, display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <DocumentUploader />
                  <SettingsPanel />
                </Box>

                {/* Right Panel - Chat Interface */}
                <Box sx={{ flex: 1 }}>
                  <ChatInterface />
                </Box>
              </Box>
            </Container>
          </div>
          </DocumentProvider>
        </APIProvider>
      </SessionProvider>
    </ThemeProvider>
  );
}

export default App;
