from packaging_codes import PackagingCodes
from soup import Soup

class Instructions(PackagingCodes):
    START = 201
    END = 202
    def __init__(self, db, soup):
        PackagingCodes.__init__(self, db, soup)
        self.PART = 173

    def unna_lookup(self, code, bulk):
        table = "bulk_packaging" if bulk else "non_bulk_packaging"
        requirement = self.db.execute('''
            SELECT requirement FROM hazmat_table
            JOIN {}
            ON hazmat_table.hazmat_id = {}.hazmat_id
            WHERE hazmat_table.id_num = '{}';
        '''.format(table, table, code))
        return self.get_codes_descriptions(int(requirement.fetchone()[0]), 'b')