from flask import Blueprint, current_app, render_template

from .db import ping

bp = Blueprint('main', __name__)


@bp.get('/')
def index():
    db_ok = ping(current_app.config['DATABASE_URL'])
    return render_template('index.html', db_ok=db_ok)
