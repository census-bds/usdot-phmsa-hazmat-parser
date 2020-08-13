from flask import (
    Blueprint, Flask, flash, g, make_response, redirect, render_template, request, session, url_for
)

from . import db

from . import table
from . import soup

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

        if error is None:
            if bulk:
                table_name = "bulk_packaging"
            else:
                table_name = "non_bulk_packaging"
            hazmat_id_query = hazmat_db.execute(
                '''
                SELECT hazmat_id, hazmat_name FROM hazmat_table
                WHERE id_num = '{}';
                '''.format(un_id))
            #TO DO : right now we take the first one, need to address UNIDs with >1 row
            hazmat_id, hazmat_name = hazmat_id_query.fetchone()
            requirement = hazmat_db.execute(
                '''
                SELECT requirement FROM {} 
                WHERE hazmat_id = {}
                '''.format(
                    table_name, hazmat_id))
            subpart_string = requirement.fetchall()[0][0]
            subpart_tag = soup.SOUP.find(
                'sectno', text="§ 173.{}".format(subpart_string))
            '''
            template = render_template('results.xml', results=subpart_tag.parent)
            response = make_response(template)
            response.headers['Content-Type'] = 'application/xml'
            return response
            '''
            results_dict = {'UNID': un_id,
                            'hazmat_name': hazmat_name,
                            'bulk': 'Bulk' if bulk else 'Non-Bulk',
                            'text': subpart_tag.parent}
            return render_template('results.html', results=results_dict)


        flash(error)

    return render_template('packaging.html')

