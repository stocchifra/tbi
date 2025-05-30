"""
Session management service
"""
import uuid
import time
from typing import Dict, Optional


class SessionService:
    """Service for managing user sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": time.time(),
            "last_activity": time.time(),
            "documents": [],
            "chat_history": []
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self.sessions.get(session_id)
    
    def update_last_activity(self, session_id: str):
        """Update last activity timestamp"""
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = time.time()
    
    def cleanup_old_sessions(self, max_age: int = 24 * 3600):  # 24 hours
        """Remove old sessions"""
        current_time = time.time()
        expired_sessions = [
            sid for sid, data in self.sessions.items()
            if current_time - data["last_activity"] > max_age
        ]
        
        for sid in expired_sessions:
            del self.sessions[sid]
        
        return len(expired_sessions)
