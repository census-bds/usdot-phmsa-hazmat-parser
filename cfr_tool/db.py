import sqlite3
import click
from flask import Flask, current_app, g, has_app_context
from flask.cli import with_appcontext
import os
import __init__
'''
from . import table, explosives, nonbulk
from .soup import Soup
'''
import table, explosives, nonbulk, soup

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
        db = sqlite3.connect('/phmsa/hazmat-parser/instance/hazmat-parser.sqlite')
        return db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    print("initializing db")
    db = get_db()
    
    soup_2 = soup.Soup(2)
    hazmat_table = table.HazmatTable(db, soup_2)
    hazmat_table.create_load_hazmat_data()
    print("loaded hazmat")
    explosives_parser = explosives.Explosives(db, soup_2)
    explosives_parser.create_load_explosives()
    print("loaded explosives")
    
    nb = nonbulk.NonBulk(db, soup.Soup(3))
    print('made soup')
    nb.parse_kind_material()
    print('parsed kind material')
    nb.load_packaging_categories()
    print('loaded categories')
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