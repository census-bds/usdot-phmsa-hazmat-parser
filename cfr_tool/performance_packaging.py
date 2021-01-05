import regex as re

from .packaging_codes import PackagingCodes
from .soup import Soup

class PerformancePackaging(PackagingCodes):

    def __init__(self, db, soup):
        PackagingCodes.__init__(self, db, soup)
        self.START = 500
        self.END = 940
        #self.code_descriptions = self.get_codes_descriptions(self.START, self.END)
        self.part = 178

    def parse_standards(self):
        standards = []
        kind_pattern = re.compile('^\d{1,2}')
        material_pattern = re.compile('(?<=\d)[A-Z]{1,2}(?=$|\d)')
 
        for subpart in range(self.START, self.END + 1):
            codes = self.get_codes(subpart)
            if codes:
                for code in set(codes):
                    kind = kind_pattern.search(code)
                    material = material_pattern.search(code)
                    code_row = (code,
                                int(kind.group(0)) if kind else None,
                                material.group(0) if material else None,
                                "performance",
                                subpart)
                    standards.append(code_row)
        return standards
    
    # Not really sure if these are necessary
    # def create_kinds_table(self):
    #     self.db.execute('''
    #         CREATE TABLE IF NOT EXISTS packaging_kinds(
    #             id_code integer,
    #             meaning text
    #         );
    #     ''')

    # def create_materials_table(self):
    #     self.db.execute('''
    #         CREATE TABLE IF NOT EXISTS packaging_materials (
    #             id_code integer,
    #             meaning text
    #         );
    #     ''') 

    def create_packaging_standards_table(self):
        self.db.execute('''
            DROP TABLE IF EXISTS packaging_standards;
        ''')
        self.db.execute('''
            CREATE TABLE packaging_standards (
                full_code varchar not null,
                kind_id integer,
                material_id text,
                type text,
                subpart integer,
                FOREIGN KEY(full_code) REFERENCES packaging_requirements(packaging_code)
            );
        ''')

    def load_packaging_standards(self):
        self.create_packaging_standards_table()
        self.db.executemany('''
            INSERT INTO packaging_standards (
                full_code,
                kind_id,
                material_id,
                type,
                subpart
            ) VALUES (
                ?, ?, ?, ?, ?
            )
        ''', self.parse_standards())