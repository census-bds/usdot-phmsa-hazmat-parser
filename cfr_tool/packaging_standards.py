import regex as re
import clean_text as ct


'''
TO DO:
Change this to be a class tha represents packaging standards in general.
Convert specific subparts to be children of this class.
'''

class PackagingStandards:
    def __init__(self, db, soup):
        self.db = db
        self.soup = self.volume_check(soup)
        self.categories = []
    
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
        '''
        This grabs nonbulk kind and material codes. For IBCs, kind codes are in a badly
        formatted table and material codes are the same. Need to write checks for this.
        ''' 
        self.create_kinds_table()
        self.create_materials_table()
        id_codes = self.soup.get_part_tag(178, 502)
        ps = [p.text for p in id_codes.find_all('p')]
        parsed_codes = ct.parse_packaging_kind_material(ps) #MIGHT MOVE THIS FUNCTION HERE
        for table, values in parsed_codes.items():
            self.db.executemany('''
                INSERT INTO {} (
                    id_code,
                    meaning
                ) VALUES (
                    ?, ?
                )
            '''.format(table), values)

    def create_categories_table(self):
        self.db.execute('''
            DROP TABLE IF EXISTS packaging_categories;
        ''')
        self.db.execute('''
            CREATE TABLE packaging_categories (
                full_code varchar not null primary key,
                kind_id integer,
                material_id text,
                category_id integer,
                category_desc text,
                FOREIGN KEY (kind_id)
                    REFERENCES packaging_kinds (id_code),
                FOREIGN KEY (material_id)
                    REFERENCES packaging_materials (id_code)
            );
        ''')

    def load_packaging_categories(self):
        self.create_categories_table()
        self.db.executemany('''
            INSERT INTO packaging_categories (
                full_code,
                kind_id,
                material_id,
                category_id,
                category_desc
            ) VALUES (
                ?, ?, ?, ?, ?
            )
        ''', self.categories)



            


