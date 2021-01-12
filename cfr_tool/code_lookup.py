import json
import flask

from . import db
from . import packaging_codes as pc
from . import soup
from . import clean_text as ct

def code_lookup():
    code = flask.request.args.get("code")
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
        return json.dumps({"status": "code not found"})
