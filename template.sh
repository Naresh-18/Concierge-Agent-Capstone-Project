# Create main project folder
mkdir -p concierge-agent
cd concierge-agent

# -------------------------------
# Create directories
# -------------------------------
mkdir -p src
mkdir -p research
mkdir -p frontend

# -------------------------------
# Create src files
# -------------------------------
touch src/__init__.py
touch src/config.py
touch src/logger.py
touch src/memory.py
touch src/tools.py
touch src/ai_agent.py
touch src/app.py

# -------------------------------
# Create research files
# -------------------------------
touch research/trials.ipynb

# -------------------------------
# Create frontend files
# -------------------------------
touch frontend/streamlit_app.py

# -------------------------------
# Create root-level project files
# -------------------------------
touch .env
touch setup.py
touch requirements.txt