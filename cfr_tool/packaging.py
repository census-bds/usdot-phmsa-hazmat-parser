from flask import (
    Blueprint, Flask, flash, g, make_response, redirect, render_template, request, session, url_for
)

from . import db
from . import instructions
from . import soup
from . import clean_text as ct

bp = Blueprint('packaging', __name__)

def build_results(un_id, bulk, pg, db):
    table = "bulk_packaging" if bulk else "non_bulk_packaging"
    if pg:
        query_text = '''
        SELECT hazat_table.row_id, proper_shipping_name, class_division
        FROM hazmat_table
        JOIN proper_shipping_names
        ON hazmat_table.row_id = proper_shipping_names.row_id
        WHERE unna_code = '{}' and pg = '{}';
        '''.format(un_id, pg)
    else:
        query_text = '''
        SELECT hazmat_table.row_id, proper_shipping_name, class_division
        FROM hazmat_table
        JOIN proper_shipping_names
        ON hazmat_table.row_id = proper_shipping_names.row_id
        WHERE unna_code = '{}'
        '''.format(un_id)
    row_id_query = db.execute(query_text)
    #TO DO : make sure that UNNA code and pg uniquely identify each row.
    row_id, hazmat_name, class_division = row_id_query.fetchone()
    ins = instructions.Instructions(db, soup.Soup(2))
    requirement = ins.requirement_query(row_id, bulk)

    try:
        spans_paragraphs = ins.get_spans_paragraphs(requirement)
    except:
        spans_paragraphs = None
    bulk_text = 'Bulk' if bulk else 'Non-Bulk'
    if spans_paragraphs:
        packaging_text = ct.build_packaging_text(spans_paragraphs)
    else:
        packaging_text = ["No {} packaging instructions of {} available.".format(
            bulk_text.lower(), hazmat_name)]
    return {'UNID': un_id,
            'hazmat_name': hazmat_name,
            'bulk': bulk_text,
            'part_num': requirement,
            'forbidden': True if class_division == 'Forbidden' else False,
            'text': packaging_text}

           

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
            render_results = build_results(
                un_id, 
                True if bulk == "on" else False,
                pg,
                hazmat_db)
            return render_template(
                'results.html', len=len(render_results['text']), results=render_results)


        flash(error)

    return render_template('packaging.html')

