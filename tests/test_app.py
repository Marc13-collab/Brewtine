from app import create_app


def test_index_ok(monkeypatch):
    monkeypatch.setattr('app.routes.ping', lambda url: True)
    r = create_app('postgresql://x').test_client().get('/')
    assert r.status_code == 200 and b'Brewtine' in r.data and b'database: connected' in r.data
