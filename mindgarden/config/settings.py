"""
Configuration settings for MindGarden.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID", None)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Agent settings
DEFAULT_MODEL = os.getenv("MODEL", "gpt-4o")
AGENT_NAME = os.getenv("AGENT_NAME", "Quinn")


class AppConfig(BaseModel):
    """Application configuration."""
    
    # API keys
    openai_api_key: str = Field(default=OPENAI_API_KEY)
    openai_org_id: Optional[str] = Field(default=OPENAI_ORG_ID)
    
    # Database settings
    neo4j_uri: str = Field(default=NEO4J_URI)
    neo4j_user: str = Field(default=NEO4J_USER)
    neo4j_password: str = Field(default=NEO4J_PASSWORD)
    
    # Agent settings
    model: str = Field(default=DEFAULT_MODEL)
    agent_name: str = Field(default=AGENT_NAME)
    agent_temperature: float = Field(default=0.7)
    agent_max_tokens: Optional[int] = Field(default=None)
    
    # Path settings
    base_dir: Path = Field(default=BASE_DIR)
    data_dir: Path = Field(default=DATA_DIR)
    logs_dir: Path = Field(default=LOGS_DIR)


# Default configuration
config = AppConfig()


def get_config() -> AppConfig:
    """Get the application configuration."""
    return config 