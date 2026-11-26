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
