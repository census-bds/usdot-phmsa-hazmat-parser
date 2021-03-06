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
        SELECT row_id, hazmat_name, class_division FROM hazmat_table
        WHERE unna_code = '{}' and pg = '{}';
        '''.format(un_id, pg)
    else:
        query_text = '''
        SELECT row_id, hazmat_name, class_division FROM hazmat_table
        WHERE unna_code = '{}'
        '''.format(un_id)
    row_id_query = db.execute(query_text)
    #TO DO : make sure that UNNA code and pg uniquely identify each row.
    row_id, hazmat_name, class_division = row_id_query.fetchone()
    ins = instructions.Instructions(db, soup.Soup(2))
    requirement_query = ins.db.execute('''
            SELECT section FROM packaging_instructions
            WHERE row_id = {} AND bulk = {}
        '''.format(row_id, 1 if bulk == 'true' else 0))

    try:
        requirement = requirement_query.fetchone()
        requirement = requirement[0]
        spans_paragraphs = ins.get_spans_paragraphs(requirement)
    except:
        spans_paragraphs = None
    bulk_text = 'Bulk' if bulk == "true" else 'Non-Bulk'
    if spans_paragraphs:
        packaging_text = ct.build_packaging_text(spans_paragraphs)
    else:
        packaging_text = ["No {} packaging instructions of {} available.".format(
            bulk_text.lower(), hazmat_name)]

    return {'UNID': un_id,
            'hazmat_name': hazmat_name,
            'bulk': bulk_text,
            'pg': pg,
            'part_num': requirement,
            'forbidden': True if class_division == 'Forbidden' else False,
            'text': packaging_text,
            'special_provisions': ins.get_special_provisions(row_id)}

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
            SELECT * FROM packaging_standards WHERE packaging_code='{}'
        '''.format(code))
        rows = cur.fetchall()
        #For now, grabs the first result
        section = rows[0]['section']
        p = pc.PackagingCodes(cur, soup.Soup(3))
        p.part = 178
        spans_paragraphs = p.get_spans_paragraphs(section)
        html_list = ct.build_packaging_text(spans_paragraphs)
        html_text = ''
        for p in html_list:
            html_text += '<p>'
            html_text += p
            html_text += '</p>'
        return json.dumps({"status": "success",
                           "section": section,
                           "html": html_text})
    else:
        return flask.render_template("packaging.html", results=False)
