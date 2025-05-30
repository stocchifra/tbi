import React, { useState, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as DocumentIcon,
} from '@mui/icons-material';
import { useAPI } from '../contexts/APIContext';
import { useSession } from '../contexts/SessionContext';
import { useDocument } from '../contexts/DocumentContext';

const DocumentUploader: React.FC = () => {
  const { apiClient, isAPIKeySet } = useAPI();
  const { sessionId } = useSession();
  const { documents, loadDocuments } = useDocument();
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type (text files only)
    if (!file.type.startsWith('text/') && !file.name.endsWith('.txt')) {
      setError('Please upload a text file (.txt)');
      return;
    }

    // Validate file size (1MB max)
    if (file.size > 1024 * 1024) {
      setError('File too large. Maximum size is 1MB.');
      return;
    }

    setIsUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const content = await file.text();
      await uploadDocument(content, file.name);
    } catch (error) {
      console.error('Error reading file:', error);
      setError('Failed to read file content');
    } finally {
      setIsUploading(false);
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const uploadDocument = async (content: string, filename: string | null) => {
    try {
      const response = await apiClient.post('/documents/upload', {
        content,
        filename,
        session_id: sessionId,
      });

      setSuccess(`Document uploaded successfully!`);
      loadDocuments(); // Refresh document list
    } catch (error: any) {
      console.error('Error uploading document:', error);
      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError('Failed to upload document. Please try again.');
      }
    }
  };

  return (
    <Paper sx={{ p: 2, height: 'fit-content' }}>
      <Typography variant="h6" gutterBottom>
        Document Upload
      </Typography>

      {/* File Upload */}
      <Box sx={{ mb: 2 }}>
        <input
          type="file"
          accept=".txt,text/*"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
          ref={fileInputRef}
          disabled={isUploading || !isAPIKeySet}
        />
        <Button
          variant="contained"
          startIcon={<UploadIcon />}
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading || !isAPIKeySet}
          fullWidth
        >
          Upload Text File (.txt)
        </Button>
      </Box>

      {/* Status Messages */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {!isAPIKeySet && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Set your OpenAI API key first to upload documents.
        </Alert>
      )}

      {/* Document List */}
      {documents.length > 0 && (
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Uploaded Documents ({documents.length})
          </Typography>
          <List dense>
            {documents.map((doc) => (
              <ListItem key={doc.id} sx={{ px: 0 }}>
                <ListItemIcon>
                  <DocumentIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={doc.filename || 'Text content'}
                  secondary={`${formatFileSize(doc.size)} • ${new Date(
                    doc.upload_timestamp
                  ).toLocaleDateString()}`}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Paper>
  );
};

export default DocumentUploader;
