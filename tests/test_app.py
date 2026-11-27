from app import create_app


def get(path):
    return create_app('postgresql://x').test_client().get(path)


def test_index_has_form():
    r = get('/')
    assert r.status_code == 200 and b'id="habit-form"' in r.data and b'database: connected' not in r.data


def test_static_assets_are_served():
    assert get('/static/app.js').status_code == 200
    assert get('/static/style.css').status_code == 200
