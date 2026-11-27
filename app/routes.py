from flask import Blueprint, current_app, jsonify, render_template, request

from . import db
from .clock import today_manila

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
    return render_template('index.html')


@bp.get('/api/habits')
def get_habits():
    with db.get_conn(_url()) as conn:
        habits = db.list_habits(conn, today_manila())
    return jsonify(habits), 200


@bp.post('/api/habits')
def create_habit():
    cleaned, error = validate_habit(request.get_json(silent=True))
    if error:
        return jsonify({'error': error}), 400
    with db.get_conn(_url()) as conn:
        habit = db.insert_habit(conn, cleaned['name'], cleaned['weekly_target'])
    return jsonify(habit), 201


# max=2147483647 keeps ids inside Postgres's integer range; larger ids are a plain 404.
@bp.post('/api/habits/<int(max=2147483647):habit_id>/toggle')
def toggle_habit(habit_id):
    with db.get_conn(_url()) as conn:
        checked = db.toggle_check_in(conn, habit_id, today_manila())
    if checked is None:
        return jsonify({'error': 'Habit not found.'}), 404
    return jsonify({'checked': checked}), 200


@bp.delete('/api/habits/<int(max=2147483647):habit_id>')
def delete_habit(habit_id):
    with db.get_conn(_url()) as conn:
        deleted = db.delete_habit(conn, habit_id)
    if not deleted:
        return jsonify({'error': 'Habit not found.'}), 404
    return '', 204
