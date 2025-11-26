# src/memory.py
import uuid
from typing import Dict, Any

class InMemorySessionService:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, user_id: str) -> str:
        sid = str(uuid.uuid4())
        self.sessions[sid] = {"user_id": user_id, "history": []}
        return sid

    def get_session(self, session_id: str) -> Dict[str, Any]:
        return self.sessions.get(session_id, {"user_id": "unknown", "history": []})

    def save_session(self, session_id: str, session: Dict[str, Any]) -> None:
        self.sessions[session_id] = session
