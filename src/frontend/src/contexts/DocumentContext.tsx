import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAPI } from './APIContext';
import { useSession } from './SessionContext';

interface Document {
  id: number;
  filename: string | null;
  size: number;
  upload_timestamp: string;
}

interface DocumentContextType {
  documents: Document[];
  selectedDocumentId: number | null;
  isLoading: boolean;
  error: string | null;
  loadDocuments: () => Promise<void>;
  selectDocument: (documentId: number | null) => void;
  getSelectedDocument: () => Document | null;
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

export const useDocument = () => {
  const context = useContext(DocumentContext);
  if (!context) {
    throw new Error('useDocument must be used within a DocumentProvider');
  }
  return context;
};

interface DocumentProviderProps {
  children: ReactNode;
}

export const DocumentProvider: React.FC<DocumentProviderProps> = ({ children }) => {
  const { apiClient, isAPIKeySet } = useAPI();
  const { sessionId } = useSession();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDocuments = async () => {
    if (!sessionId || !isAPIKeySet) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(`/documents/${sessionId}`);
      const fetchedDocuments = response.data;
      setDocuments(fetchedDocuments);
      
      // Auto-select the most recent document if none is selected
      if (fetchedDocuments.length > 0 && !selectedDocumentId) {
        const mostRecent = fetchedDocuments.reduce((latest: Document, current: Document) => 
          new Date(current.upload_timestamp) > new Date(latest.upload_timestamp) ? current : latest
        );
        setSelectedDocumentId(mostRecent.id);
      }
    } catch (error) {
      console.error('Error loading documents:', error);
      setError('Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  };

  const selectDocument = (documentId: number | null) => {
    setSelectedDocumentId(documentId);
  };

  const getSelectedDocument = () => {
    return documents.find(doc => doc.id === selectedDocumentId) || null;
  };

  useEffect(() => {
    loadDocuments();
  }, [sessionId, isAPIKeySet]);

  return (
    <DocumentContext.Provider value={{
      documents,
      selectedDocumentId,
      isLoading,
      error,
      loadDocuments,
      selectDocument,
      getSelectedDocument,
    }}>
      {children}
    </DocumentContext.Provider>
  );
};
