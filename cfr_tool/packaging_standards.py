import regex as re
from . import clean_text as ct


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

    def get_categories(self, start, end):
        #Find the code pattern which is digits, letters, digits
        code_pattern = re.compile("(\d+)([A-Z]+)(\d+)")
        #Find the category name which is some text followed by "for a(n) ", preceded by ; or .
        category_pattern = re.compile("(?<=for\sa?n?\s?)(.*)(?=[;\.])")
        categories_data = []
        for subpart in range(start, end):
            subpart_tag = self.soup.get_subpart_text(178, subpart)
            ps = [p.text for p in subpart_tag.find_all('p')]
            id_codes_text = [(idx, text) for idx, text in enumerate(ps) if \
                " identification codes for " in text]
            if len(id_codes_text) > 0:
                start_idx = id_codes_text[0][0]
                end_idx = [(idx, text) for idx, text in enumerate(ps) if \
                    "Construction requirements for " in text][0][0]
                category_code_text = ps[start_idx: end_idx]
                for text in category_code_text:
                    matched = code_pattern.findall(text)
                    if matched:
                        kind, material, category_code = code_pattern.findall(text)[0]
                        category_desc = category_pattern.search(text).group()
                        categories_data.append((kind + material + category_code,
                                                int(kind),
                                                material,
                                                int(category_code),
                                                category_desc))
        return categories_data


            


