import os

from flask import Flask
import sqlite3
from . import soup


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'hazmat-parser.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    @app.route('/cfr_tool')
    def cfr_tool():
        return 'Welcome to the cfr tool'

    from . import db
    db.init_app(app)

    from . import packaging
    app.register_blueprint(packaging.bp)
    app.add_url_rule('/', endpoint='packaging')

    return app


def debug_harness(db_name = "instance/hazmat-parser.sqlite"):
    from importlib import reload
    reload(soup)
    s2 = soup.Soup(volume=2)
    s3 = soup.Soup(volume=3)
    db = sqlite3.connect(db_name)
    return s2, s3, db
