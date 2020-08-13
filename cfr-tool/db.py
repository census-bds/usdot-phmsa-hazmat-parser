import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
import os

from . import table
from . import soup

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    # uncomment when running a flask app
    db = get_db()
    '''
    if not os.path.isfile('hazmat-parser.sqlite'):
        # comment out when running a flask app
        
        db = sqlite3.connect(
            os.path.join(os.getcwd(), 'hazmat-parser.sqlite'),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
    '''
    db.executescript("DROP TABLE IF EXISTS hazmat_table;")
    db.executescript(
        '''
        CREATE TABLE hazmat_table (
            hazmat_id integer not null primary key,
            hazmat_name text, class_division text,
            id_num text, pg text, rail_max_quant text,
            aircraft_max_quant text, stowage_location text
        );
        '''
    )
    print("created hazmat table")

    for table_name, column in soup.NONUNIQUE_MAP.values():
        table.create_nonunique_table(db, table_name, column)

    def find_hazmat_table(soup_table):
        table_title = soup_table.find('ttitle')
        return table_title and ("Hazardous Materials Table" in table_title.contents[0])

    hazmat_table = list(
        filter(find_hazmat_table, soup.SOUP.find_all('gpotable')))[0]
    print("found the hazmat table")
    pk = 1
    
    for row in hazmat_table.find_all('row')[1:]:
        # TO DO: check that data starts at row 1
        table.load_ents(db, row, pk)
        pk += 1
        print("pk is ", pk)
    db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)