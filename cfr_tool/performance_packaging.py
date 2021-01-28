import regex as re

from .packaging_codes import PackagingCodes
from .soup import Soup

class PerformancePackaging(PackagingCodes):

    def __init__(self, db, soup):
        PackagingCodes.__init__(self, db, soup)
        self.START = 503
        self.END = 940
        #self.code_descriptions = self.get_codes_descriptions(self.START, self.END)
    
        self.part = 178

    def parse_specs(self):
        specs = []
        for subsection in range(self.START, self.END + 1):
            codes = self.get_codes(subsection)
            if codes:
                for code in set(codes):
                    code_row = (code,
                                "performance",
                                subsection)
                    assert len(code_row) == 3
                    specs.append(code_row)
        return specs
    
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

    def create_packaging_specs_table(self):
        self.db.execute('''
            DROP TABLE IF EXISTS packaging_specs;
        ''')
        self.db.execute('''
            CREATE TABLE packaging_specs (
                full_code varchar not null,
                type text,
                subsection integer,
                FOREIGN KEY(full_code) REFERENCES packaging_requirements(packaging_code)
            );
        ''')

    def load_packaging_specs(self):
        self.create_packaging_specs_table()
        self.db.executemany('''
            INSERT INTO packaging_specs (
                full_code,
                type,
                subsection
            ) VALUES (
                ?, ?, ?
            )
        ''', self.parse_specs())