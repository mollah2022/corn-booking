from pathlib import Path
from dynaconf import Dynaconf

BASE_DIR = Path(__file__).resolve().parent.parent.parent

config = Dynaconf(
    envvar_prefix="BOOKING",
    settings_files=[
        BASE_DIR / "settings.toml",
        BASE_DIR / ".secrets.toml",
    ],
    environments=True,
    env_switcher="BOOKING_ENV",
    load_dotenv=True,
)

DATABASE_URL = (
    f"postgresql+psycopg2://{config.db_user}:{config.db_password}"
    f"@{config.db_host}:{config.db_port}/{config.db_name}"
)

BOOKING_API_BASE_URL = config.booking_api_base_url
BOOKING_API_KEY = config.get("booking_api_key", None)

EXCHANGE_RATE_API_BASE_URL = config.exchange_rate_api_base_url

SENTRY_DSN = config.get("sentry_dsn", None)
SENTRY_ENVIRONMENT = config.get("sentry_environment", "development")
