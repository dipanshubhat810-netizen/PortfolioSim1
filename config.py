import os
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

# config.py — Use environment variables for deployment; defaults for local dev
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Atharva@2005")
DB_NAME     = os.getenv("DB_NAME", "PortfolioSim1")

RISK_FREE_RATE        = 0.03
TOP_ASSETS_PER_SECTOR = 2
DEFAULT_CORRELATION   = 0.10

