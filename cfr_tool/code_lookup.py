import json
import flask

from . import db
from . import packaging_codes as pc
from . import soup
from . import clean_text as ct
from . import instructions

def build_results(un_id, bulk, pg, db):
    print("bulk")
    print(bulk)
    if pg:
        query_text = '''
        SELECT hazmat_id, hazmat_name, class_division FROM hazmat_table
        WHERE unna_code = '{}' and pg = '{}';
        '''.format(un_id, pg)
    else:
        query_text = '''
        SELECT hazmat_id, hazmat_name, class_division FROM hazmat_table
        WHERE unna_code = '{}'
        '''.format(un_id)
    hazmat_id_query = db.execute(query_text)
    #TO DO : make sure that UNNA code and pg uniquely identify each row.
    hazmat_id, hazmat_name, class_division = hazmat_id_query.fetchone()
    ins = instructions.Instructions(db, soup.Soup(2))
    requirement_query = ins.db.execute('''
            SELECT requirement FROM {}
            WHERE hazmat_id = {}
        '''.format("bulk_packaging" if bulk == "true" else "non_bulk_packaging", hazmat_id))
    requirement = requirement_query.fetchone()
    requirement = requirement[0]
    special_prov_query = ins.db.execute('''
        SELECT * FROM special_provisions WHERE hazmat_id = {}
    '''.format(hazmat_id))
    special_provisions = special_prov_query.fetchall()
    try:
        spans_paragraphs = ins.get_spans_paragraphs(requirement)
    except:
        spans_paragraphs = None
    bulk_text = 'Bulk' if bulk == "true" else 'Non-Bulk'
    if spans_paragraphs:
        packaging_text = ct.build_packaging_text(spans_paragraphs)
    else:
        packaging_text = ["No {} packaging instructions of {} available.".format(
            bulk_text.lower(), hazmat_name)]
    print(special_provisions)
    return {'UNID': un_id,
            'hazmat_name': hazmat_name,
            'bulk': bulk_text,
            'part_num': requirement,
            'forbidden': True if class_division == 'Forbidden' else False,
            'text': packaging_text,
            'special_provisions': [x['special_provision'] for x in special_provisions]}

def code_lookup():
    print(flask.request.args)
    un = flask.request.args.get("un", None)
    bulk = flask.request.args.get("bulk", None)
    pg = flask.request.args.get("pg", None)
    code = flask.request.args.get("code", None)
    if un:
        hazmat_db = db.get_db()
        render_results = build_results(un, bulk, pg, hazmat_db)
        return flask.render_template(
            'packaging.html', len=len(render_results['text']), results=render_results)
    if code:
        cur = db.get_db().cursor()
        cur.execute('''
            SELECT * FROM packaging_standards WHERE full_code='{}'
        '''.format(code))
        rows = cur.fetchall()
        #For now, grabs the first result
        subpart = rows[0]['subpart']
        p = pc.PackagingCodes(cur, soup.Soup(3))
        p.part = 178
        spans_paragraphs = p.get_spans_paragraphs(subpart)
        html_list = ct.build_packaging_text(spans_paragraphs)
        html_text = ''
        for p in html_list:
            html_text += '<p>'
            html_text += p
            html_text += '</p>'
        return json.dumps({"status": "success",
                           "subpart": subpart,
                           "html": html_text})
    else:
        return flask.render_template("packaging.html", results=False)
