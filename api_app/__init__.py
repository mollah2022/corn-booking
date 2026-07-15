from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from api_app.config import REDIS_URL

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL,
)


def create_api_app():
    app = Flask(__name__)

    limiter.init_app(app)

    from api_app.routes.booking_routes import booking_bp
    app.register_blueprint(booking_bp)

    return app
