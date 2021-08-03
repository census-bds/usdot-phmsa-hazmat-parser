from flask import (
    Blueprint, flash, g, make_response, redirect, render_template, request, session, url_for
)

from . import db
from . import clean_text as ct
from . import code_lookup

bp = Blueprint('packaging', __name__)
        

def check_packaging(unna, db):
    db.execute("SELECT pg FROM hazmat_table WHERE unna_code = '{}'".format(unna))
    pgs = db.fetchall()
    if len(pgs) > 1:
        #TO DO: render packaging.html so it shows the multiple PG options for the user to select.
        render_template('packaging.html')

@bp.route('/',  methods=('GET', 'POST'))
def packaging():
    if request.method == 'POST':
        un_id = request.form['un_id']
        bulk = request.form.get('bulk')
        hazmat_db = db.get_db()
        if not request.form.get('packing-group'):
            #check_packaging(un_id, hazmat_db)
            pg = None
        else:
            pg = request.form['packing-group']
        error = None
      

        if not un_id:
            error = 'UNID is required.'
        else:
            render_results = code_lookup.build_results(
                un_id, 
                True if bulk == "on" else False,
                pg,
                hazmat_db)
            return render_template(
                'packaging.html', len=len(render_results['text']), results=render_results)


        flash(error)

    return render_template('packaging.html')

