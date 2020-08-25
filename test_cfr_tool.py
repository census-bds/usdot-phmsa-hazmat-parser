import os
import tempfile

import pytest

from cfr_tool import create_app, db


@pytest.fixture
def client():
    cfr_tool = create_app()
    db_fd, cfr_tool.config['DATABASE'] = tempfile.mkstemp()
    cfr_tool.config['TESTING'] = True

    with cfr_tool.test_client() as client:
        with cfr_tool.app_context():
            db.init_db()
        yield client

    os.close(db_fd)
    os.unlink(cfr_tool.config['DATABASE'])

def test_empty_db(client):

    rv = client.post('/packaging')
    assert rv.data