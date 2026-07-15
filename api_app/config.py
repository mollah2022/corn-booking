from pathlib import Path
from dynaconf import Dynaconf

BASE_DIR = Path(__file__).resolve().parent.parent

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

REDIS_HOST = config.redis_host
REDIS_PORT = config.redis_port
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
