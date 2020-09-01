import re

class Explosives:
    def __init__(self, db, soup):
        self.db = db
        self.soup = soup

    def create_load_explosives(self):
        self.parse_load_pis()

    def parse_load_pis(self):
        self.db.executescript("DROP TABLE IF EXISTS explosives_table;")
        self.db.executescript('''
            CREATE TABLE explosives_table (
                id_num text,
                packaging_instruction text,
                FOREIGN KEY (id_num)
                    REFERENCES hazmat_table (id_num)
            )
        ''')
        explosives = self.soup.find_table("Explosives Table")
        print("created explosives table")
        entries = []
        for row in explosives.find_all('row'):
            text = [ent.text for ent in row.find_all('ent')]
            un_na = text[0]
            pis = text[1].split(' or ')
            for pi in pis:
                entries.append((un_na, pi))
        self.db.executemany('''
            INSERT INTO explosives_table (id_num, packaging_instruction)
            VALUES (?, ?)
        ''', entries)
        print("loaded explosives table")

    def parse_load_packing_methods(self):
        self.db.executescript("DROP TABLE IF EXISTS packing_methods;")
        self.db.executescript('''
            CREATE TABLE packing_methods (
                packaging_instruction text,
                inner_packagings_type text,
                intermediate_packagings_type text,
                outer_packagings_type text,
                requirements_exceptions text,
                inner_packagings_material text,
                intermediate_packagings_material text,
                outer_packagings_material text,
                FOREIGN KEY (packaging_instruction)
                    REFERENCES explosives_table (packaging_instruction)
            );
        ''')
        packing_rows = self.soup.find_table("Table of Packing Methods").find_all('row')
        symbol = True
        full_data = []
        for row in packing_rows:
            ents = row.find_all('ent')
            if symbol:
                #make sure there are three digits at the beginning
                three_digits = re.compile("\d\d\d")
                assert three_digits.match(ents[0].text)
                data = [ent.text for ent in ents]
                while len(data) < 4:
                    data.append(None)
            else:
                for ent in ents:
                    #skip the rows that just say "PARTICULAR PACKING REQUIREMENTS OR EXCEPTIONS:"
                    if ent.text == "PARTICULAR PACKING REQUIREMENTS OR EXCEPTIONS:" and \
                        len(ents) == 1:
                        continue
                    data.append(ent.text)
                while len(data) < 8:
                    data.append(None)
                full_data.append(tuple(data))
            symbol = not symbol
        self.db.executemany('''
            INSERT INTO packing_methods (
                packaging_instruction,
                inner_packagings_type,
                intermediate_packagings_type,
                outer_packagings_type,
                requirements_exceptions,
                inner_packagings_material,
                intermediate_packagings_material,
                outer_packagings_material
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', full_data)


