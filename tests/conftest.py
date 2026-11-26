import os

import pytest

from app import create_app
from app.db import get_conn, init_schema


@pytest.fixture(scope='session')
def test_url():
    url = os.environ.get('TEST_DATABASE_URL')
    if not url:
        pytest.fail('Set TEST_DATABASE_URL to a separate test database before running these tests.')
    if url == os.environ.get('DATABASE_URL'):
        pytest.fail('TEST_DATABASE_URL must differ from DATABASE_URL: tests empty their tables.')
    return url


@pytest.fixture
def client(test_url):
    with get_conn(test_url) as conn:
        init_schema(conn)
        conn.execute('TRUNCATE check_ins, habits RESTART IDENTITY CASCADE')
    return create_app(test_url).test_client()
