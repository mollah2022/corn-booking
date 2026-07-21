import sentry_sdk
from app.config.settings import SENTRY_DSN, SENTRY_ENVIRONMENT


def init_sentry():
    if not SENTRY_DSN:
        print("SENTRY_DSN not set - Sentry disabled")
        return
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        traces_sample_rate=0.1,
        send_default_pii=False,
        debug=True,
    )
    print(f"Sentry initialized with DSN: {SENTRY_DSN[:30]}...")
