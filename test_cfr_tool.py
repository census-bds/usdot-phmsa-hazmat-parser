import os
import tempfile

import pytest

from cfr_tool import create_app


@pytest.fixture
def client():
    db_fd, cfr_tool.app.config['DATABASE'] = tempfile.mkstemp()
    cfr_tool.app.config['TESTING'] = True

    with cfr_tool.app.test_client() as client:
        with cfr_tool.app.app_context():
            cfr_tool.init_db()
        yield client

    os.close(db_fd)
    os.unlink(cfr_tool.app.config['DATABASE'])

def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'No entries here so far' in rv.data