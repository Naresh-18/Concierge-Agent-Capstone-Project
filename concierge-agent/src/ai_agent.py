# src/ai_agent.py

"""
Concierge Agent - Planner / Worker / Coordinator

This version calls OpenRouter directly via `requests` instead of the
openai Python client, to avoid Client.__init__ / proxies issues.

Model used: google/gemma-3n-e2b-it:free
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, List
import uuid
import json
import time
import requests

from src.logger import logger
from src.tools import RecipeTool, WebSearchTool, ShoppingTool
from src.memory import InMemorySessionService
from src.config import settings

MODEL_NAME = "deepseek/deepseek-chat"


def call_openrouter_chat(model: str, messages: List[Dict[str, str]], max_tokens: int = 300) -> str:
    """
    Call OpenRouter's /chat/completions endpoint via HTTP.
    Returns the text content of the first choice.
    """
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set in environment/.env")

    base = settings.OPENAI_API_BASE or "https://openrouter.ai/api/v1"
    url = base.rstrip("/") + "/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
        # optional but good practice with OpenRouter:
        "HTTP-Referer": "http://localhost",
        "X-Title": "Concierge-Agent-Capstone",
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"OpenRouter error {resp.status_code}: {resp.text}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Unexpected OpenRouter response shape: {e}, data={data}")


class PlannerAgent:
    def __init__(self, model_name: str = MODEL_NAME, max_tokens: int = 300):
        self.model_name = model_name
        self.max_tokens = max_tokens

    def plan(self, user_query: str) -> List[Dict[str, Any]]:
        """
        Use the LLM (OpenRouter + Gemma) to break down a user query into steps.
        If anything fails, fall back to heuristic steps.
        """
        prompt = (
            "You are a planner agent. Break the user's request into 2–4 numbered, "
            "short, actionable steps.\n\n"
            f"User request: {user_query}\n\nSteps:\n"
        )

        try:
            plan_text = call_openrouter_chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful planner agent that returns numbered steps.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
            )

            lines = [ln.strip() for ln in plan_text.splitlines() if ln.strip()]
            parsed: List[Dict[str, Any]] = []
            for ln in lines:
                cleaned = ln
                # remove leading "1.", "1)", "- " etc.
                if len(ln) > 2 and ln[0].isdigit() and (ln[1] in ".)"):
                    cleaned = ln[2:].strip()
                elif ln.startswith("- "):
                    cleaned = ln[2:].strip()
                parsed.append({"id": str(uuid.uuid4()), "description": cleaned})

            if not parsed:
                raise ValueError("No parsed steps from LLM")
            return parsed

        except Exception as e:
            logger.error(f"PlannerAgent LLM error: {e}")
            # 🔁 fallback heuristic (what you already saw working)
            q = user_query.lower()
            if any(word in q for word in ["meal", "recipe", "dinner", "breakfast", "lunch"]):
                return [
                    {"id": str(uuid.uuid4()), "description": "Search for an appropriate recipe"},
                    {"id": str(uuid.uuid4()), "description": "Generate a shopping list from the recipe"},
                    {"id": str(uuid.uuid4()), "description": "Provide cooking steps overview"},
                ]
            if "travel" in q or "itinerary" in q:
                return [
                    {"id": str(uuid.uuid4()), "description": "Search top travel options"},
                    {"id": str(uuid.uuid4()), "description": "Generate day-by-day itinerary"},
                ]
            return [{"id": str(uuid.uuid4()), "description": "Perform a web search for the query"}]


class WorkerAgent:
    def __init__(self, tools: Dict[str, Any]):
        self.tools = tools

    def run_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        desc = step.get("description", "").lower()
        if "recipe" in desc or "meal" in desc:
            return self.tools["recipe"].search(desc)
        if "shopping" in desc or "shopping list" in desc:
            return self.tools["shopping"].create_list(desc)
        return self.tools["web"].search(desc)


class Coordinator:
    def __init__(self, session_service: InMemorySessionService, tools: Dict[str, Any]):
        self.session_service = session_service
        self.planner = PlannerAgent()
        self.worker = WorkerAgent(tools)

    def handle_request(self, session_id: str, user_query: str, parallel: bool = False) -> Dict[str, Any]:
        session = self.session_service.get_session(session_id)
        plan = self.planner.plan(user_query)
        results = []

        for step in plan:
            start = time.time()
            res = self.worker.run_step(step)
            elapsed = time.time() - start
            results.append(
                {"step": step, "result": res, "elapsed_seconds": round(elapsed, 3)}
            )
            session["history"].append({"step": step, "result": res})
            self.session_service.save_session(session_id, session)

        return {"session_id": session_id, "plan": plan, "results": results}


# -----------------------
# Standalone test / demo
# -----------------------
if __name__ == "__main__":
    tools = {"recipe": RecipeTool(), "web": WebSearchTool(), "shopping": ShoppingTool()}
    memory = InMemorySessionService()
    sid = memory.create_session("demo_user")

    sample_query = "Plan a healthy vegetarian dinner for 4 people and generate a shopping list."
    print(f"Sample query: {sample_query}")
    print("----\n")

    out = Coordinator(memory, tools).handle_request(sid, sample_query)
    print(json.dumps(out, indent=2))
