import regex as re

from . import packaging_codes as pc

class Instructions(pc.PackagingCodes):

    def __init__(self, db, soup):
        pc.PackagingCodes.__init__(self, db, soup)
        self.part = 173
        self.db = db
        self.soup = soup

    # def package_text_lookup(self, hazmat_id, bulk):
    #     #requirement = requirement_query(self, hazmat_id, bulk)
    #     try:
    #         return self.get_spans_paragraphs(requirement[0])
    #     except:
    #         pass
        
    def get_special_provisions(self, hazmat_id):
        def _match_code(code):
            code_pattern = re.compile(code + "(?![A-Za-z0-9])")
            texts = spec_prov_tag.find_all(text=code_pattern)
            if texts:
                #TO DO: Deal with edge cases where the first match is not the proper match.
                #TO DO: Decide how to display special provisions listed in table format
                #For now, we try to pick matches which occur at the very beginning of the text
                print(code)
                if len(texts) == 1:
                    text = texts[0]
                    span = code_pattern.search(text).span()
                else:
                    spans = [code_pattern.search(text).span() for text in texts]
                    span_starts = [span[0] for span in spans]
                    _, idx = min((val, idx) for (idx, val) in enumerate(span_starts))
                    text = texts[idx]
                    span = spans[idx]
                return text[0:span[0]] + "<b>" + text[span[0]:span[1]] + "</b>" +\
                    text[span[1]:len(text) + 1]
            else:
                return "<b>" + code + "</b>"
        special_prov_query = self.db.execute('''
            SELECT * FROM special_provisions WHERE hazmat_id = {}
        '''.format(hazmat_id))
        special_provisions = special_prov_query.fetchall()
        special_provisions_codes = [x['special_provision'] for x in special_provisions]
        spec_prov_tag = self.soup.get_subpart_text(172, 102)
        return [_match_code(code) for code in special_provisions_codes]

    def load_all_packaging_reqs(self):
        self.load_packaging_table("non_bulk_packaging")
        self.load_packaging_table("bulk_packaging")
        pass


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
            try:
                packaging_ids[req[0]] = self.get_codes(req[0])
            except:
                continue

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