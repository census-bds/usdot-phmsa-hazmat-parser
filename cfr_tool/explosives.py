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

    #def parse_packing_methods(soup):