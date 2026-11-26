import os

import click
from flask import Flask


def create_app(database_url=None):
    app = Flask(__name__)
    app.config['DATABASE_URL'] = database_url or os.environ.get('DATABASE_URL', '')

    from . import db
    from .routes import bp
    app.register_blueprint(bp)

    @app.cli.command('init-db')
    def init_db_command():
        """Create the database tables."""
        with db.get_conn(app.config['DATABASE_URL']) as conn:
            db.init_schema(conn)
        click.echo('Schema ready.')

    return app
