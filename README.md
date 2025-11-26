# Concierge Agent – Capstone Project

A multi-agent **Concierge Assistant** that helps users plan meals and generate shopping lists using an LLM-powered planner, tool-driven worker agents, and a clean FastAPI + Streamlit stack.

This project was built as a capstone for the **Google AI Agents / Kaggle 5 Days of AI** track, applying the concepts of multi-agent systems, tools, and memory in a real end-to-end application.

---

## 🎯 Project Objective

The goal of this project is to build an **AI concierge agent** that:

- Understands natural-language queries like  
  _“Plan a healthy vegetarian dinner for 4 people and generate a shopping list.”_
- Breaks the query into **step-by-step actions** using an LLM planner.
- Executes each step using different **specialized tools** (recipe, shopping, web lookup).
- Returns a **human-friendly plan + consolidated shopping list** via a web interface.

This demonstrates practical usage of:

- Multi-agent orchestration (Planner → Worker → Tools → Coordinator)
- Tool usage and context engineering
- Basic session memory and state
- Web deployment style patterns with FastAPI + Streamlit

---

## 🧠 High-Level Architecture

The system is composed of:

1. **Planner Agent (LLM via OpenRouter / Gemma)**
   - Takes the user query (e.g., “Plan dinner for 4…”)  
   - Generates 2–4 **numbered steps**, each representing a sub-task.

2. **Worker Agent**
   - Reads each planner step and decides **which tool** to call:
     - `RecipeTool` – suggests a recipe and ingredients.
     - `ShoppingTool` – builds a shopping list.
     - `WebSearchTool` – (optionally) searches the web, or returns mock results.

3. **Coordinator**
   - Orchestrates the full flow:
     - Calls the Planner to get steps.
     - Calls Worker for each step.
     - Updates session history in `InMemorySessionService`.
     - Returns a structured JSON response.

4. **Backend API (FastAPI)**
   - Exposes a single `/ask` endpoint.
   - Accepts `{ "query": "...", "session_id": optional }`.
   - Returns the full plan + tool results as JSON.

5. **Frontend UI (Streamlit)**
   - Simple chat-style interface.
   - Shows:
     - The **plan steps** (numbered).
     - A combined **shopping list** (ingredients + items from tools).
     - Raw JSON under an expander (for debugging / evaluation).

---

## 📁 Project Structure

```bash
Concierge-Agent-Capstone-Project/
│
├── concierge-agent/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── app.py              # FastAPI backend (entrypoint for API)
│   │   ├── ai_agent.py         # Planner / Worker / Coordinator multi-agent logic
│   │   ├── tools.py            # RecipeTool, ShoppingTool, WebSearchTool
│   │   ├── memory.py           # InMemorySessionService (session + history)
│   │   ├── config.py           # Environment / .env loader
│   │   └── logger.py           # Loguru logger configuration
│   │
│   ├── frontend/
│   │   └── streamlit_app.py    # Streamlit web UI
│   │
│   ├── research/
│   │   └── trials.ipynb        # Optional notebook for experiments
│   │
│   ├── requirements.txt        # Python dependencies
│   ├── setup.py                # (Optional) installable package config
│   ├── .env.example            # Example environment file (no secrets)
│   ├── .gitignore
│   └── README.md (optional, or use repo root README)
│
├── template.sh                 # Project scaffolding script (creates directories/files)
├── README.md                   # You are here
└── LICENSE                     # Apache-2.0
```
---

## 🧩 Key Components
1. ```config.py```
   - Loads environment variables from ```.env``` using ```python-dotenv```.
   - Centralizes access to:
      - ```OPENAI_API_KEY```
      - ```OPENAI_API_BASE``` (OpenRouter base)
      - ```GOOGLE_API_KEY```, ```GOOGLE_CSE_ID``` (optional, for Google Custom Search)
   - Keeps configuration simple (no pydantic settings dependency).

2. ```ai_agent.py```
   Implements the multi-agent logic:
   - ```PlannerAgent```
      - Uses ```requests``` to call OpenRouter ```/chat/completions``` with model: ```deepseek/deepseek-chat```
      - Prompted to break the user query into numbered, short, actionable steps.
      - Parses the LLM output into a list of ```{ id, description }``` step objects.
      - On error, falls back to heuristic multi-step plans for meal/recipe/travel queries.

   - ```WorkerAgent```
      - For each step:
        - If it mentions “recipe” or “meal” → calls ```RecipeTool```.
        - If it mentions “shopping” / “shopping list” → calls ```ShoppingTool```.
        - Otherwise → calls ```WebSearchTool```.
       
   - ```Coordinator```
      - Accepts ```session_id``` and ```user_query```.
      - Gets or creates a session from ```InMemorySessionService```.
      - Calls planner → gets plan.
      - Sequentially executes each step via ```WorkerAgent```.
      - Records step results + execution time.
      - Returns ```{ session_id, plan, results }``` as JSON.

3. ```tools.py```
   - ```RecipeTool```
     - Returns a demo recipe such as “Mixed Veg Stir Fry” with:
       - Ingredients like ```["carrot", "beans", "peas", "oil", "salt"]```
       - Basic steps

   - ```ShoppingTool```
     - Returns a basic list of items: ```["rice", "dal", "veggies"]```
     - In a real extension, this could aggregate ingredients from planner steps.

   - ```WebSearchTool```
     - If Google CSE keys are configured: tries ```https://www.googleapis.com/customsearch/v1.```
     - On any error (403, quota, etc.) or missing keys: logs error and returns mock results to keep the agent flow stable.      

4. ```app.py``` (FastAPI)
   - Defines:
     ```bash
     POST /ask
     {
      "query": "...",
      "session_id": "optional",
      "parallel": false
     }
     ```
   - Instantiates:
     - Tools (```RecipeTool```, ```ShoppingTool```, ```WebSearchTool```)
     - ```InMemorySessionService```
     - ```Coordinator```
   - Returns ```Coordinator.handle_request(...)``` output.
   - Also exposes a simple ```/health``` endpoint.

5. ```frontend/streamlit_app.py```
   - Simple UI:
     - Textarea for the user query.
     - “Send” button which:
       - Calls ```http://127.0.0.1:8000/ask``` with JSON body.
       - Displays a formatted response.
   - Output format:
     - Plan (Steps) – numbered list of descriptions.
     - Suggested Shopping List – merged, unique items from:
       - ```ShoppingTool.items```
       - ```RecipeTool.recipe.ingredients```
     - Raw JSON (debug) – available under a Streamlit expander for inspection.

---

