from datetime import date

import pytest


def post(client, body):
    return client.post('/api/habits', json=body)


def test_create_returns_201(client):
    r = post(client, {'name': 'Study', 'weekly_target': 5})
    assert r.status_code == 201 and r.json['name'] == 'Study' and r.json['weekly_target'] == 5


def test_target_defaults_to_7(client):
    assert post(client, {'name': 'Run'}).json['weekly_target'] == 7


def test_name_is_trimmed(client):
    assert post(client, {'name': '  Read  '}).json['name'] == 'Read'


@pytest.mark.parametrize('body', [
    {'name': '   '},
    {'name': 'x' * 61},
    {'name': 'A', 'weekly_target': 0},
    {'name': 'A', 'weekly_target': 8},
    {'name': 'A', 'weekly_target': '5'},
    {'name': 'A', 'weekly_target': True},
    {},
    [],
    {'weekly_target': 3},
])
def test_bad_body_400(client, body):
    r = post(client, body)
    assert r.status_code == 400 and 'error' in r.json


def test_non_json_400(client):
    r = client.post('/api/habits', data='nope', content_type='text/plain')
    assert r.status_code == 400


def test_list_200(client):
    post(client, {'name': 'Study'})
    r = client.get('/api/habits')
    assert r.status_code == 200 and [h['name'] for h in r.json] == ['Study']


def test_toggle_on_then_off(client):
    hid = post(client, {'name': 'A'}).json['id']
    assert client.post(f'/api/habits/{hid}/toggle').json == {'checked': True}
    assert client.get('/api/habits').json[0]['checked_today'] is True
    assert client.post(f'/api/habits/{hid}/toggle').json == {'checked': False}
    assert client.get('/api/habits').json[0]['checked_today'] is False


def test_toggle_uses_manila_date(client, conn, monkeypatch):
    monkeypatch.setattr('app.routes.today_manila', lambda: date(2026, 11, 27))
    hid = post(client, {'name': 'A'}).json['id']
    client.post(f'/api/habits/{hid}/toggle')
    assert conn.execute('SELECT check_date FROM check_ins').fetchone()[0] == date(2026, 11, 27)


def test_checked_today_follows_the_date(client, monkeypatch):
    hid = post(client, {'name': 'A'}).json['id']
    monkeypatch.setattr('app.routes.today_manila', lambda: date(2026, 11, 26))
    client.post(f'/api/habits/{hid}/toggle')
    assert client.get('/api/habits').json[0]['checked_today'] is True
    monkeypatch.setattr('app.routes.today_manila', lambda: date(2026, 11, 27))
    assert client.get('/api/habits').json[0]['checked_today'] is False


@pytest.mark.parametrize('hid', ['999999', '99999999999'])
def test_toggle_unknown_404(client, hid):
    assert client.post(f'/api/habits/{hid}/toggle').status_code == 404


def test_delete_204_and_cascades(client, conn):
    hid = post(client, {'name': 'A'}).json['id']
    client.post(f'/api/habits/{hid}/toggle')
    assert client.delete(f'/api/habits/{hid}').status_code == 204
    assert client.get('/api/habits').json == []
    assert conn.execute('SELECT count(*) FROM check_ins').fetchone()[0] == 0


@pytest.mark.parametrize('hid', ['999999', '99999999999'])
def test_delete_unknown_404(client, hid):
    assert client.delete(f'/api/habits/{hid}').status_code == 404
