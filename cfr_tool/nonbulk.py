import regex as re
from . import packaging_standards as ps 

class NonBulk(ps.PackagingStandards):
    START = 504
    END = 523
    def __init__(self, db, soup):
        ps.PackagingStandards.__init__(self, db, soup)
        self.categories = self.get_categories(self.START, self.END)

    def parse_kind_material(self):
        self.create_kinds_table()
        self.create_materials_table()
        id_codes = self.soup.get_subpart_text(178, 502)
        texts = [p.text for p in id_codes.find_all('p')]
        parsed_codes = {"packaging_kinds": [], "packaging_materials": []}
        # Looks for the 'B' and 'aluminum within '(ii) “B” means aluminum.'
        pattern_material = re.compile(
            '((?<=\\“)[A-Z](?=\\”\\smeans\\s))|((?<=means\s).*(?=\.))')
        # Looks for the '1' and 'drum' within '(i) “1” means a drum.'
        pattern_kind = re.compile(
            '((?<=\\“)\d(?=\\”\\smeans\\s))|((?<=means\s).*(?=\.))')
        for text in texts:
            matches = pattern_kind.findall(text)
            if matches:
                if matches[0][0]:
                    parsed_codes["packaging_kinds"].append((matches[0][0], matches[1][1]))
                else:
                    matches = pattern_material.findall(text)
                    parsed_codes["packaging_materials"].append(
                        (matches[0][0], matches[1][1]))
        for table, values in parsed_codes.items():
            self.db.executemany('''
                INSERT INTO {} (
                    id_code,
                    meaning
                ) VALUES (
                    ?, ?
                )
            '''.format(table), values)
