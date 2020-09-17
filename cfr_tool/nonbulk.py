import regex as re
from packaging_standards import PackagingStandards 

class NonBulk(PackagingStandards):
    def __init__(self, db, soup):
        PackagingStandards.__init__(self, db, soup)
        self.categories = self.get_categories()

    def parse_kind_material(self):
        '''
        This grabs nonbulk kind and material codes. For IBCs, kind codes are in a badly
        formatted table and material codes are the same. Need to write checks for this.
        ''' 
        self.create_kinds_table()
        self.create_materials_table()
        id_codes = self.soup.get_part_tag(178, 502)
        texts = [p.text for p in id_codes.find_all('p')]
        parsed_codes = {"packaging_kinds": [], "packaging_materials": []}
        pattern_material = re.compile(
            '((?<=\\“)[A-Z](?=\\”\\smeans\\s))|((?<=means\s).*(?=\.))')
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

    def get_categories(self):
        code_pattern = re.compile("(\d+)([A-Z]+)(\d+)")
        category_pattern = re.compile("(?<=for\sa?n?\s?)(.*)(?=[;\.])")
        categories_data = []
        for subpart in range(504, 524):
            print(subpart)
            subpart_tag = self.soup.get_part_tag(178, subpart)
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
                        print(text)
                        print()
                        kind, material, category_code = code_pattern.findall(text)[0]
                        category_desc = category_pattern.search(text).group()
                        categories_data.append((kind + material + category_code,
                                                int(kind),
                                                material,
                                                int(category_code),
                                                category_desc))
        return categories_data
