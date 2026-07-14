from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    from app.config.settings import Settings
    app.config.from_object(Settings)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import booking  # noqa: F401  (model registration)

    return app