import re
from . import clean_text as ct
from . import patterns

class Explosives:
    def __init__(self, db, soup):
        self.db = db
        self.soup = soup
        self.section = "173.62"

    def create_explosives_table(self):
        self.db.execute(
            '''
            DROP TABLE IF EXISTS explosives;
            '''
        )
        self.db.execute(
            '''
            CREATE TABLE explosives (
                unna_code text,
                pi text not null,
                FOREIGN KEY (unna_code) REFERENCES hazmat_table (unna_code),
                FOREIGN KEY (pi) REFERENCES pis
            );
            '''
        )
        return
    
    def create_pis_table(self):
        self.db.execute(
            '''
            DROP TABLE IF EXISTS pis;
            '''
        )
        self.db.execute(
            '''
            CREATE TABLE pis (
                pi text primary key,
                inner text,
                intermediate text,
                outer text
            )
            '''
        )

    def create_explosive_pis_tables(self):
        self.db.execute(
            '''
            DROP TABLE IF EXISTS explosive_pi_unnas;
            '''
        )
        self.db.execute(
            '''
            CREATE TABLE explosive_pi_unnas (
                pi text,
                column text,
                unna_code text,
                FOREIGN KEY (unna_code) REFERENCES hazmat_table (unna_code),
                FOREIGN KEY (pi) REFERENCES pis (pi)
            );
            '''
        )
        self.db.execute(
            '''
            DROP TABLE IF EXISTS explosive_pi_packaging_codes;
            '''
        )
        self.db.execute(
            '''
            CREATE TABLE explosive_pi_packaging_codes (
                pi text,
                column text,
                packaging_code text,
                FOREIGN KEY (pi) REFERENCES pis (pi),
                FOREIGN KEY (column) REFERENCES explosives_pis_unnas (column)
            );
            '''
        )
        return
    
    def parse_explosives_table(self):
        '''
        Returns items to be inserted into explosives table
        '''
        explosives_table = self.soup.find_table('Explosives Table')
        rows = explosives_table.find_all('row')
        ents = [row.find_all('ent') for row in rows]
        insert = []
        for ent in ents:
            unna_code = ent[0].text
            pi = ent[1].text
            if " or " in pi:
                pis = pi.split(' or ')
                for p in pis:
                    insert.append((p, unna_code))
            else:
                insert.append((pi, unna_code))
        return insert
    
    def parse_packing_methods(self):
        '''
        Returns 3 lists of tuples to be inserted into pis, explosive_pi_unnas, and
        explosive_pi_packaging_codes
        '''
        column_map = {
            0: 'requirements_exceptions',
            1: 'inner_packagings',
            2: 'intermediate_packagings',
            3: 'outer_packagings'
        }
        packing_methods_table = self.soup.find_table('Table of Packing Methods')
        rows = packing_methods_table.find_all('row')
        pi = None
        pis_insert = []
        explosive_pi_unnas_insert = []
        explosive_pi_packaging_codes_insert = []
        for row in rows:
            ents = row.find_all('ent')
            first_cell = ents[0].text
            pi_pattern = re.compile(patterns.PI_PATTERN)
            pi_match = pi_pattern.match(first_cell)
            if pi_match:
                pi = pi_match.group()
                if len(ents) < 4:
                    pis_insert.append((pi, None, None, None))
                    continue
                else:
                    pis_insert.append((pi, ents[1].text, ents[2].text, ents[3].text))
            else:
                for i, ent in enumerate(ents):
                    unna_codes = ct.find_unnas(ent.text)
                    perf_pattern = re.compile(patterns.PERF_PACKAGING)
                    packaging_codes = perf_pattern.findall(ent.text)
                    for unna_code in unna_codes:
                        explosive_pi_unnas_insert.append((pi, column_map[i], unna_code))
                    for packaging_code in packaging_codes:
                        explosive_pi_packaging_codes_insert.append(
                            (pi, column_map[i], packaging_code))

        return pis_insert, explosive_pi_unnas_insert, explosive_pi_packaging_codes_insert

    def parse_load_all_explosives(self):
        self.create_explosives_table()
        self.create_pis_table()
        self.db.executemany(
            '''
            INSERT INTO explosives (unna_code, pi) VALUES (?, ?)
            ''', self.parse_explosives_table()
        )
        self.db.commit()
        self.create_explosive_pis_tables()
        pis_insert, explosive_unnas, explosive_packaging_codes = \
            self.parse_packing_methods()
        self.db.executemany(
            '''
            INSERT INTO pis (pi, inner, intermediate, outer) VALUES (?, ?, ?, ?)
            ''', pis_insert
        )
        self.db.executemany(
            '''
            INSERT INTO explosive_pi_unnas (pi, column, unna_code) VALUES (?, ?, ?)
            ''', explosive_unnas
        )
        self.db.executemany(
            '''
            INSERT INTO explosive_pi_packaging_codes (pi, column, packaging_code)
            VALUES (?, ?, ?)
            ''', explosive_packaging_codes
        )
        return
