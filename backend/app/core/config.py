import os

APP_ENV = os.getenv("APP_ENV", "development")
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
POLYMARKET_URL = os.getenv("POLYMARKET_URL", "https://clob.polymarket.com/markets")
TRIGGER_AUTH_TOKEN = os.getenv("TRIGGER_AUTH_TOKEN", "")
DISCOVERY_SCHEDULER_ENABLED = os.getenv("DISCOVERY_SCHEDULER_ENABLED", "false").lower() == "true"
_raw_interval = int(os.getenv("DISCOVERY_SCHEDULER_INTERVAL", "3600"))
if _raw_interval < 1:
    raise ValueError(
        f"DISCOVERY_SCHEDULER_INTERVAL must be >= 1, got {_raw_interval}"
    )
DISCOVERY_SCHEDULER_INTERVAL: int = _raw_interval
