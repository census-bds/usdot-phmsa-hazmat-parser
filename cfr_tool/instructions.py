from . import packaging_codes as pc

class Instructions(pc.PackagingCodes):

    def __init__(self, db, soup):
        pc.PackagingCodes.__init__(self, db, soup)
        self.part = 173

    def unna_lookup(self, code, table):
        requirement = self.db.execute('''
            SELECT requirement FROM hazmat_table
            JOIN {}
            ON hazmat_table.hazmat_id = {}.hazmat_id
            WHERE hazmat_table.unna_code = '{}';
        '''.format(table, table, code))
        return self.get_spans_paragraphs(int(requirement.fetchone()[0]))
    
    def load_all_packaging_reqs(self):
        self.load_packaging_table("non_bulk_packaging")
        self.load_packaging_table("bulk_packaging")
    
    def get_codes(self, req):
        codes, descs = self.get_spans_paragraphs(req)
        packaging_ids = []
        for spans, desc in zip(codes, descs):
            for span in spans:
                packaging_ids.append(desc[span[0]: span[1]])
        return packaging_ids

    def load_packaging_table(self, table):
        #TO DO: deal with all reqs that had a letter in them (i.e. 302c)
        nb_reqs_query = self.db.execute(
            '''
            SELECT DISTINCT requirement FROM {};
            '''.format(table)
        )
        nb_reqs = nb_reqs_query.fetchall()
        packaging_ids = {req[0]: [] for req in nb_reqs}
        for req in nb_reqs:
            packaging_ids[req[0]] = self.get_codes(req[0])
            '''
            try:
                packaging_ids[req[0]] = self.get_codes(req[0])
            except:
                continue
            '''
        insert_list = []
        for req, codes in packaging_ids.items():
            if codes:
                for code in codes:
                    if not (req, code) in insert_list:
                        insert_list.append((req, code))
        print(insert_list)
        self.db.executemany(
            '''
            INSERT INTO packaging_requirements VALUES (
                ?, ?
            )
            ''', insert_list
        )       