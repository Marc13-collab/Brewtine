import os

from flask import Flask


def create_app(database_url=None):
    app = Flask(__name__)
    app.config['DATABASE_URL'] = database_url or os.environ.get('DATABASE_URL', '')

    from .routes import bp
    app.register_blueprint(bp)
    return app
