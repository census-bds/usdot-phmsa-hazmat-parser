import os
import tempfile
import sqlite3
import pytest

from cfr_tool import create_app, db, table, soup


TEST_SOUP = soup.Soup()

@pytest.fixture(scope="function")
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    yield app

    os.close(db_fd)
    os.unlink(db_path)

'''
@pytest.fixture(scope="function")
def client():
    cfr_tool = create_app()
    db_fd, cfr_tool.config['DATABASE'] = tempfile.mkstemp()
    cfr_tool.config['TESTING'] = True

    with cfr_tool.test_client() as client:
        with cfr_tool.app_context():
            client.test_db = db.get_db()
        yield client

    os.close(db_fd)
    os.unlink(cfr_tool.config['DATABASE'])
'''


def test_create_nonunique_tables(app):
    with app.app_context():
        test_db = db.get_db()
        cur = test_db.cursor()
        cur.execute("CREATE TABLE hazmat_table (hazmat_id);")
        table.create_nonunique_table(cur, "symbols", "symbol")
        cur.execute("PRAGMA table_info(symbols);")
        output = cur.fetchall()
        assert [tuple(output[0]), tuple(output[1])] == \
            [(0, 'hazmat_id', 'integer', 1, None, 0), (1, 'symbol', 'text', 0, None, 0)]

def test_hazmat_table_length():
    hazmat_table = TEST_SOUP.get_hazmat_table()
    assert len(hazmat_table.find_all('ent')) == 42738

def test_get_subpart_text():
    sect_tag = TEST_SOUP.get_subpart_text(173, 62).find('sectno')
    assert sect_tag.text == '§\u2009173.62' 