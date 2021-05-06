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

    def parse_standards(self):
        standards = []
        for section in range(self.START, self.END + 1):
            codes = self.grab_agency_code_pattern("{}.{}".format(self.part, section))
            if codes:
                standards += codes
        return standards
    

    def create_packaging_standards_table(self):
        self.db.execute('''
            DROP TABLE IF EXISTS packaging_standards;
        ''')
        self.db.execute('''
            CREATE TABLE packaging_standards (
                section integer,
                authorizing_agency text,
                packaging_code text not null,
                type text,
                paragraph text,
                span_0 integer,
                span_1 integer,
                FOREIGN KEY(packaging_code) REFERENCES packaging_requirements(packaging_code)
            );
        ''')

    def load_packaging_standards(self):
        self.create_packaging_standards_table()
        self.db.executemany('''
            INSERT INTO packaging_standards (
                section,
                authorizing_agency,
                packaging_code,
                paragraph,
                type,
                span_0,
                span_1
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?
            )
        ''', self.parse_standards())