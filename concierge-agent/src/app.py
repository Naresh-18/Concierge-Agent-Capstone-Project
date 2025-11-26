# src/app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.memory import InMemorySessionService
from src.tools import RecipeTool, WebSearchTool, ShoppingTool
from src.ai_agent import Coordinator
from src.logger import logger

app = FastAPI(title="Concierge Agent Backend")

class QueryRequest(BaseModel):
    session_id: Optional[str] = None
    query: str
    parallel: bool = False

# Initialize tools, memory, coordinator (singletons)
_tools = {
    "recipe": RecipeTool(),
    "web": WebSearchTool(),
    "shopping": ShoppingTool(),
}
_session_service = InMemorySessionService()
_coordinator = Coordinator(_session_service, _tools)


@app.post("/ask")
async def ask(req: QueryRequest):
    try:
        sid = req.session_id or _session_service.create_session("user")
        out = _coordinator.handle_request(sid, req.query, parallel=req.parallel)
        return out
    except Exception as e:
        logger.error(f"Backend /ask failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
