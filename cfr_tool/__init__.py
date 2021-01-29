import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from . import soup
#import soup


def create_app(test_config=None):
    # create and configure the app

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db = SQLAlchemy(app)

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

    from . import code_lookup
    app.add_url_rule('/code_lookup', 'code_lookup', code_lookup.code_lookup)

    from . import pg_lookup
    app.add_url_rule('/pg_lookup', 'pg_lookup', pg_lookup.pg_lookup)

    return app


    from . import database

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        database.db_session.remove()
