from setuptools import setup, find_packages

setup(
    name="concierge-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi", "uvicorn[standard]", "openai",
        "requests", "streamlit", "python-dotenv",
        "loguru", "pydantic"
    ],
)