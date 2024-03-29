import sqlite3
import click
from flask import Flask, current_app, g, has_app_context
from flask.cli import with_appcontext
import os
from . import __init__

from . import table, explosives, nonbulk
from . import soup
from . import instructions
from . import performance_packaging
from . import spec_packaging
from . import explosives
'''
import table, explosives, nonbulk, soup
'''
DATABASE_PATH = '../hazmat-parser/instance'

def get_db():
    if has_app_context():
        if 'db' not in g:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row

        return g.db
    else:
        db = sqlite3.connect(DATABASE_PATH + '/hazmat-parser.sqlite')
        return db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    print("initializing db")
    db = get_db()
    
    soup_2 = soup.Soup(2)
    print('made soup')
    hazmat_table = table.HazmatTable(db, soup_2)
    hazmat_table.create_load_hazmat_data()
    print("loaded hazmat")

    instructions_parser = instructions.Instructions(db, soup_2)
    instructions_parser.load_all_packaging_reqs()
    print("loaded instructions")

    soup_3 = soup.Soup(3)
    perf_packaging_parser = performance_packaging.PerformancePackaging(db, soup_3)
    perf_packaging_parser.load_packaging_standards()
    print("loaded performance packaging")

    spec_parser = spec_packaging.SpecPackaging(db)
    spec_parser.get_load_sects_subjects()
    print("loaded spec packaging")
    spec_parser.get_load_tank_cars()
    print('loaded tank cars')

    # explosives_parser = explosives.Explosives(db, soup_2)
    # explosives_parser.parse_load_all_explosives()
    # print('loaded explosives')
    '''
    nb = nonbulk.NonBulk(db, soup.Soup(3))
    nb.parse_kind_material()
    print('parsed kind material')
    nb.load_packaging_categories()
    print('loaded categories')
    '''
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