import os

APP_ENV = os.getenv("APP_ENV", "development")
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
POLYMARKET_URL = os.getenv("POLYMARKET_URL", "https://clob.polymarket.com/markets")
TRIGGER_AUTH_TOKEN = os.getenv("TRIGGER_AUTH_TOKEN", "")
DISCOVERY_SCHEDULER_ENABLED = os.getenv("DISCOVERY_SCHEDULER_ENABLED", "false").lower() == "true"
DISCOVERY_SCHEDULER_INTERVAL = int(os.getenv("DISCOVERY_SCHEDULER_INTERVAL", "3600"))
