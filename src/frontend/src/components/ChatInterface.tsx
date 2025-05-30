import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  CircularProgress,
  Alert,
  List,
  ListItem,
  Chip,
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
} from '@mui/icons-material';
import { useAPI } from '../contexts/APIContext';
import { useSession } from '../contexts/SessionContext';
import { useDocument } from '../contexts/DocumentContext';

interface ChatMessage {
  id: number;
  message_type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tokens_used?: number;
  processing_time?: number;
}

const ChatInterface: React.FC = () => {
  const { apiClient, isAPIKeySet } = useAPI();
  const { sessionId } = useSession();
  const { selectedDocumentId } = useDocument();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streamingResponse, setStreamingResponse] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingResponse]);

  useEffect(() => {
    // Load chat history when component mounts
    if (sessionId && isAPIKeySet) {
      loadChatHistory();
    }
  }, [sessionId, isAPIKeySet]);

  const loadChatHistory = async () => {
    if (!sessionId || !isAPIKeySet) return;

    try {
      const response = await apiClient.get(`/chat/history/${sessionId}`);
      setMessages(response.data);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !isAPIKeySet || isLoading) return;

    const userMessage = currentMessage.trim();
    setCurrentMessage('');
    setError(null);
    setIsLoading(true);
    setStreamingResponse('');

    // Add user message to UI immediately
    const tempUserMessage: ChatMessage = {
      id: Date.now(),
      message_type: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempUserMessage]);

    try {
      // Send query and handle streaming response
      const response = await fetch(`${apiClient.defaults.baseURL}/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage,
          session_id: sessionId,
          document_id: selectedDocumentId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body reader available');
      }

      let assistantResponse = '';
      let buffer = '';
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode the chunk and add to buffer
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;

        // Split by double newlines to separate SSE messages
        const messages = buffer.split('\n\n');
        buffer = messages.pop() || ''; // Keep incomplete message in buffer

        for (const message of messages) {
          const lines = message.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6); // Remove 'data: ' prefix but DON'T trim to preserve spaces
              
              if (data === '[DONE]') {
                // Response completed - streaming response is final
                if (assistantResponse) {
                  const assistantMessage: ChatMessage = {
                    id: Date.now() + 1,
                    message_type: 'assistant',
                    content: assistantResponse,
                    timestamp: new Date().toISOString(),
                  };
                  setMessages(prev => [...prev, assistantMessage]);
                }
                setStreamingResponse('');
                return;
              } else if (data.startsWith('ERROR:')) {
                throw new Error(data.slice(7));
              } else if (data) {
                assistantResponse += data;
                setStreamingResponse(assistantResponse);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError(error instanceof Error ? error.message : 'Failed to send message');
      // Remove the user message if there was an error
      setMessages(prev => prev.filter(msg => msg.id !== tempUserMessage.id));
    } finally {
      setIsLoading(false);
      setStreamingResponse('');
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  if (!isAPIKeySet) {
    return (
      <Paper sx={{ height: '100%', p: 3, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Alert severity="info">
          Please set your OpenAI API key in the settings panel to start chatting.
        </Alert>
      </Paper>
    );
  }

  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Chat Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">Chat with AI Assistant</Typography>
        <Typography variant="body2" color="text.secondary">
          Ask questions about your uploaded documents
        </Typography>
      </Box>

      {/* Messages Area */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
        <List>
          {messages.map((message) => (
            <ListItem key={message.id} sx={{ display: 'block', py: 1 }}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: message.message_type === 'user' ? 'flex-end' : 'flex-start',
                  mb: 1,
                }}
              >
                <Box
                  sx={{
                    maxWidth: '70%',
                    p: 2,
                    borderRadius: 2,
                    backgroundColor: message.message_type === 'user' ? 'primary.main' : 'grey.100',
                    color: message.message_type === 'user' ? 'white' : 'text.primary',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    {message.message_type === 'user' ? (
                      <PersonIcon sx={{ mr: 1, fontSize: 16 }} />
                    ) : (
                      <BotIcon sx={{ mr: 1, fontSize: 16 }} />
                    )}
                    <Typography variant="caption">
                      {message.message_type === 'user' ? 'You' : 'AI Assistant'}
                    </Typography>
                  </Box>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {message.content}
                  </Typography>
                  {message.tokens_used && (
                    <Chip
                      label={`${message.tokens_used} tokens`}
                      size="small"
                      sx={{ mt: 1, fontSize: '0.7rem' }}
                    />
                  )}
                </Box>
              </Box>
            </ListItem>
          ))}

          {/* Streaming Response */}
          {streamingResponse && (
            <ListItem sx={{ display: 'block', py: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 1 }}>
                <Box
                  sx={{
                    maxWidth: '70%',
                    p: 2,
                    borderRadius: 2,
                    backgroundColor: 'grey.100',
                    color: 'text.primary',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <BotIcon sx={{ mr: 1, fontSize: 16 }} />
                    <Typography variant="caption">AI Assistant</Typography>
                    <CircularProgress size={12} sx={{ ml: 1 }} />
                  </Box>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {streamingResponse}
                  </Typography>
                </Box>
              </Box>
            </ListItem>
          )}
        </List>
        <div ref={messagesEndRef} />
      </Box>

      {/* Error Display */}
      {error && (
        <Box sx={{ p: 2 }}>
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Box>
      )}

      {/* Input Area */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Ask a question about your document..."
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            variant="outlined"
            size="small"
          />
          <IconButton
            onClick={sendMessage}
            disabled={!currentMessage.trim() || isLoading}
            color="primary"
            sx={{ alignSelf: 'flex-end' }}
          >
            {isLoading ? <CircularProgress size={24} /> : <SendIcon />}
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
};

export default ChatInterface;
