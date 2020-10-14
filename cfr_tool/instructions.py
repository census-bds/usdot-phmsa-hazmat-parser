from packaging_codes import PackagingCodes
from soup import Soup

class Instructions(PackagingCodes):

    def __init__(self, db, soup):
        PackagingCodes.__init__(self, db, soup)
        self.part = 173

    def unna_lookup(self, code, table):
        print('''
            SELECT requirement FROM hazmat_table
            JOIN {}
            ON hazmat_table.hazmat_id = {}.hazmat_id
            WHERE hazmat_table.unna_code = '{}';
        '''.format(table, table, code))
        requirement = self.db.execute('''
            SELECT requirement FROM hazmat_table
            JOIN {}
            ON hazmat_table.hazmat_id = {}.hazmat_id
            WHERE hazmat_table.unna_code = '{}';
        '''.format(table, table, code))
        return self.get_codes_descriptions(int(requirement.fetchone()[0]), 'b')