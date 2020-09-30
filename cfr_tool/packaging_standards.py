import networkx as nx
import regex as re

from . import clean_text as ct



'''
TO DO:
Change this to be a class tha represents packaging standards in general.
Convert specific subparts to be children of this class.
'''

class PackagingStandards:
    PART = 178 

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

    def get_categories(self, start, end, definition_paragraph='a'):
        #Find the code pattern which is digits, letters, digits
        code_pattern = re.compile("(\d+[A-Z]+\d*)")
        #Find the category name which is some text followed by "for a(n) ", preceded by ; or .
        category_pattern = re.compile("(?<=for\sa?n?\s?)(.*)(?=[;\.])")
        categories_data = []
        for subpart in range(start, end + 1):
            subpart_tag = self.soup.get_subpart_text(self.PART, subpart)
            basic_type = subpart_tag.find("subject").text.split("for")[-1][:-1].strip()
            paragraphs = self.soup.get_subpart_paragraphs(self.PART, subpart)
            definitions = nx.subgraph(paragraphs, paragraphs[definition_paragraph])
            paragraphs = [p.text for d, p in definitions.nodes().data('paragraph')]
            codes = [code_pattern.findall(p) for p in paragraphs] 
            # TODO: remove stopwords?
            descs = [p.split(", ".join(c))[-1] for p, c in zip(paragraphs, codes)]
            types = [basic_type] *  len(codes)
            categories_data.append(tuple(zip(codes, descs, types)))
        return categories_data


