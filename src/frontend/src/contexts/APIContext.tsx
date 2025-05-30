import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios, { AxiosInstance } from 'axios';
import { useSession } from './SessionContext';

interface APIContextType {
  apiClient: AxiosInstance;
  isAPIKeySet: boolean;
  setAPIKey: (apiKey: string) => Promise<boolean>;
  clearAPIKey: () => void;
  baseURL: string;
}

const APIContext = createContext<APIContextType | undefined>(undefined);

export const useAPI = () => {
  const context = useContext(APIContext);
  if (!context) {
    throw new Error('useAPI must be used within an APIProvider');
  }
  return context;
};

interface APIProviderProps {
  children: ReactNode;
}

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const APIProvider: React.FC<APIProviderProps> = ({ children }) => {
  const { sessionId } = useSession();
  const [isAPIKeySet, setIsAPIKeySet] = useState(false);
  const [apiClient] = useState<AxiosInstance>(() => {
    return axios.create({
      baseURL: `${BASE_URL}/api`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  });

  useEffect(() => {
    // Check if API key is stored
    const storedAPIKey = localStorage.getItem('ai-doc-analysis-apikey');
    setIsAPIKeySet(!!storedAPIKey);
  }, []);

  const setAPIKey = async (apiKey: string): Promise<boolean> => {
    try {
      const response = await apiClient.post('/config/openai-key', {
        api_key: apiKey,
        session_id: sessionId,
      });

      if (response.data.status === 'success') {
        localStorage.setItem('ai-doc-analysis-apikey', 'set'); // Don't store the actual key
        setIsAPIKeySet(true);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to set API key:', error);
      return false;
    }
  };

  const clearAPIKey = () => {
    localStorage.removeItem('ai-doc-analysis-apikey');
    setIsAPIKeySet(false);
  };

  return (
    <APIContext.Provider
      value={{
        apiClient,
        isAPIKeySet,
        setAPIKey,
        clearAPIKey,
        baseURL: BASE_URL,
      }}
    >
      {children}
    </APIContext.Provider>
  );
};
