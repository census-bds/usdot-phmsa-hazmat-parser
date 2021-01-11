from flask import (
    Blueprint, Flask, flash, g, make_response, redirect, render_template, request, session, url_for
)

from . import db
from . import instructions
from . import soup
'''
import db
import instructions
import soup
'''
bp = Blueprint('packaging', __name__)

def build_results(un_id, bulk, pg, db):
    table = "bulk_packaging" if bulk else "non_bulk_packaging"
    if pg:
        query_text = '''
        SELECT hazmat_id, hazmat_name, class_division FROM hazmat_table
        WHERE unna_code = '{}' and pg = '{}';
        '''.format(un_id, pg)
    else:
        query_text = query_text = '''
        SELECT hazmat_id, hazmat_name, class_division FROM hazmat_table
        WHERE unna_code = '{}'
        '''.format(un_id)
    hazmat_id_query = db.execute(query_text)
    #TO DO : make sure that UNNA code and pg uniquely identify each row.
    hazmat_id, hazmat_name, class_division = hazmat_id_query.fetchone()
    ins = instructions.Instructions(db, soup.Soup(2))
    requirement = ins.requirement_query(hazmat_id, bulk)
    try:
        spans_paragraphs = ins.get_spans_paragraphs(requirement)
    except:
        spans_paragraphs = None
    bulk_text = 'Bulk' if bulk else 'Non-Bulk'
    if spans_paragraphs:
        packaging_text = build_packaging_text(spans_paragraphs)
    else:
        packaging_text = ["No {} packaging instructions of {} available.".format(
            bulk_text.lower(), hazmat_name)]
    return {'UNID': un_id,
            'hazmat_name': hazmat_name,
            'bulk': bulk_text,
            'part_num': requirement,
            'forbidden': True if class_division == 'Forbidden' else False,
            'text': packaging_text}

def build_packaging_text(spans_paragraphs):
    '''
    Take a list with spans in index 0 and paragraphs in index 1 and apply a <mark> tag
    around the specified spans.
    '''
    output_html = []
    for i, paragraph in enumerate(spans_paragraphs[1]):
        spans = spans_paragraphs[0][i]
        marked_par = paragraph
        if spans:
            increment = 0
            for span in spans:
                beginning = marked_par[:span[0] + increment]
                mark = marked_par[span[0] + increment:span[1] + increment]
                end = marked_par[span[1] + increment:]
                marked_par = beginning + "<mark>" + mark + "</mark>" + end
                increment += 13
        output_html.append(marked_par)

    return output_html              

def check_packaging(unna, db):
    db.execute("SELECT pg FROM hazmat_table WHERE unna_code = '{}'".format(unna))
    pgs = db.fetchall()
    if len(pgs) > 1:
        #TO DO: render packaging.html so it shows the multiple PG options for the user to select.
        render_template('packaging.html')

@bp.route('/packaging',  methods=('GET', 'POST'))
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
            render_results= build_results(
                un_id, 
                True if bulk == "on" else False,
                pg,
                hazmat_db)
            return render_template(
                'results.html', len=len(render_results['text']), results=render_results)


        flash(error)

    return render_template('packaging.html')

