from flask import (
    Blueprint, Flask, flash, g, make_response, redirect, render_template, request, session, url_for
)

from . import db
from . import table

bp = Blueprint('packaging', __name__)

@bp.route('/packaging',  methods=('GET', 'POST'))
def packaging():
    if request.method == 'POST':
        print(request.form)

        un_id = request.form['un_id']
        bulk = request.form.get('bulk')
        hazmat_db = db.get_db()
        error = None

        print("here's what it got")
        print(un_id)
        print(bulk)

        if not un_id:
            error = 'UNID is required.'
        else:
            return render_template(
                'results.html', results=table.build_results(un_id, bulk, hazmat_db))


        flash(error)

    return render_template('packaging.html')

