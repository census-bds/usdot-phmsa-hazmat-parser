from flask import (
    Blueprint, Flask, flash, g, make_response, redirect, render_template, request, session, url_for
)
'''
from . import db
from . import instructions
from . import soup
'''
import db
import instructions
import soup

bp = Blueprint('packaging', __name__)

def build_results(un_id, bulk, pg, db):
    table = "bulk_packaging" if bulk else "non_bulk_packaging"
    hazmat_id_query = db.execute(
        '''
        SELECT hazmat_id, hazmat_name, class_division FROM hazmat_table
        WHERE unna_code = '{}' and pg = '{}';
        '''.format(un_id, pg))
    #TO DO : make sure that UNNA code and pg uniquely identify each row.
    hazmat_id, hazmat_name, class_division = hazmat_id_query.fetchone()
    ins = instructions.Instructions(db, soup.Soup(2))
    return {'UNID': un_id,
            'hazmat_name': hazmat_name,
            'bulk': 'Bulk' if bulk else 'Non-Bulk',
            'forbidden': True if class_division == 'Forbidden' else False,
            'text': ins.unna_lookup(un_id, table)}

@bp.route('/packaging',  methods=('GET', 'POST'))
def packaging():
    if request.method == 'POST':
        print(request.form)

        un_id = request.form['un_id']
        bulk = request.form.get('bulk')
        pg = request.form['packing-group']
        hazmat_db = db.get_db()
        error = None

        print("here's what it got")
        print(un_id)
        print(bulk)

        if not un_id:
            error = 'UNID is required.'
        else:
            return render_template(
                'results.html', results=build_results(
                    un_id, 
                    True if bulk == "on" else False,
                    pg,
                    hazmat_db))


        flash(error)

    return render_template('packaging.html')

