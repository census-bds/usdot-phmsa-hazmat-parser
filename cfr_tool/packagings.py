import re
import clean_text as ct

class Packagings:
    def __init__(self, db, soup):
        self.db = db
        self.soup = self.volume_check(soup)
    
    def volume_check(self, soup):
        assert soup.volume == 3
        return soup

    def create_kinds_table(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS packaging_kinds(
                id_code integer,
                meaning text
            );
        ''')

    def create_materials_table(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS packaging_materials (
                id_code integer,
                meaning text
            );
        ''')
    

    def parse_kind_material(self):
        self.create_kinds_table()
        self.create_materials_table()
        id_codes = self.soup.get_subpart_text(178, 502)
        ps = [p.text for p in id_codes.find_all('p')]
        parsed_codes = ct.parse_packaging(ps)
        for table, values in parsed_codes.items():
            self.db.executemany('''
                INSERT INTO {} (
                    id_code,
                    meaning
                ) VALUES (
                    ?, ?
                )
            '''.format(table), values)
