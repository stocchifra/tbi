import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { v4 as uuidv4 } from 'uuid';

interface SessionContextType {
  sessionId: string;
  resetSession: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

interface SessionProviderProps {
  children: ReactNode;
}

export const SessionProvider: React.FC<SessionProviderProps> = ({ children }) => {
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    // Get or create session ID
    let storedSessionId = localStorage.getItem('ai-doc-analysis-session');
    if (!storedSessionId) {
      storedSessionId = uuidv4();
      localStorage.setItem('ai-doc-analysis-session', storedSessionId);
    }
    setSessionId(storedSessionId);
  }, []);

  const resetSession = () => {
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    localStorage.setItem('ai-doc-analysis-session', newSessionId);
    // Clear other session-related data
    localStorage.removeItem('ai-doc-analysis-apikey');
  };

  return (
    <SessionContext.Provider value={{ sessionId, resetSession }}>
      {children}
    </SessionContext.Provider>
  );
};
