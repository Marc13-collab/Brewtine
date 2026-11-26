from flask import Blueprint, current_app, jsonify, render_template, request

from . import db
from .db import ping

bp = Blueprint('main', __name__)


def validate_habit(payload):
    """Return (cleaned, None) for a valid body, or (None, error message)."""
    if not isinstance(payload, dict):
        return None, 'Request body must be a JSON object.'
    name = payload.get('name')
    if not isinstance(name, str) or not name.strip():
        return None, 'name is required.'
    name = name.strip()
    if len(name) > 60:
        return None, 'name must be 60 characters or fewer.'
    target = payload.get('weekly_target', 7)
    if isinstance(target, bool) or not isinstance(target, int) or not 1 <= target <= 7:
        return None, 'weekly_target must be a whole number from 1 to 7.'
    return {'name': name, 'weekly_target': target}, None


def _url():
    return current_app.config['DATABASE_URL']


@bp.get('/')
def index():
    db_ok = ping(_url())
    return render_template('index.html', db_ok=db_ok)


@bp.get('/api/habits')
def get_habits():
    with db.get_conn(_url()) as conn:
        habits = db.list_habits(conn)
    return jsonify(habits), 200


@bp.post('/api/habits')
def create_habit():
    cleaned, error = validate_habit(request.get_json(silent=True))
    if error:
        return jsonify({'error': error}), 400
    with db.get_conn(_url()) as conn:
        habit = db.insert_habit(conn, cleaned['name'], cleaned['weekly_target'])
    return jsonify(habit), 201
