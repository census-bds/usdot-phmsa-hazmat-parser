from flask import request, render_template

from . import db

def pg_lookup():
    un_id = request.args.get("un")
    hazmat_db = db.get_db().cursor()
    hazmat_db.execute("SELECT pg FROM hazmat_table WHERE unna_code = '{}'".format(un_id))
    db_rows = hazmat_db.fetchall()
    pgs = [row['pg'] for row in db_rows]
    return {"pgs": pgs}