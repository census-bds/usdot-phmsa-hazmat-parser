from . import soup
import regex as re
#need to rename repo without hyphen so this won't be necessary
import importlib
from . import patterns as pattern

class SpecPackaging:
    def __init__(self, db):
        self.s = soup.Soup(3)
        self.db = db
    
    def get_sections(self, part):
        part = self.s.parsed_soup.find_all('ear', text='Pt. {}'.format(part))[0].parent
        sections = part.find_all('hd')
        return [section for section in sections \
            if "Subpart" in section.text and "Specifications" in section.text]

    def get_load_sects_subjects(self):
        sections = self.get_sections(178)
        output = []
        for section in sections:
            sectnos = section.parent.find_all('sectno')
            for sectno in sectnos:
                subject = sectno.find_next()
                if subject.name != 'subject':
                    continue
                spec_pattern = re.compile(pattern.SPEC_PACKAGING)
                match = spec_pattern.findall(subject.text)
                if not match:
                    continue
                assert len(match) == 1
                description = match[0][1]
                spec_pattern_2 = re.compile(pattern.SPEC_PACKAGING_2)
                match_2 = spec_pattern_2.findall(description)
                if match_2:
                    description = match_2[0][1]
                    output.append((sectno.text, match_2[0][0], description))
                output.append((sectno.text, match[0][0], description))
        self.create_spec_packaging_table()
        self.db.executemany("INSERT INTO spec_packaging VALUES (?, ?, ?)", output)
        pass

    def create_spec_packaging_table(self):
        self.db.execute("DROP TABLE IF EXISTS spec_packaging;")
        self.db.execute('''
            CREATE TABLE spec_packaging(
                section text,
                packaging_code text,
                description text
            );
        ''')

    def create_tank_car_table(self):
        self.db.execute("DROP TABLE IF EXISTS tank_cars;")
        self.db.execute(
            '''
            CREATE TABLE tank_cars (
                packaging_code varchar,
                description text,
                part text,
                subpart integer
            );
            '''
        )
        pass
    
    def get_load_tank_cars(self):
        self.create_tank_car_table()
        subparts = self.get_sections(179)
        insert = []
        for subpart in subparts:
            tank_car_pattern = re.compile(pattern.TANK_CAR_CODE)
            codes = tank_car_pattern.findall(subpart.text)
            description_pattern = re.compile(pattern.TANK_CAR_DESCRIPTION)
            description = description_pattern.findall(subpart.text)
            for code in codes:
                insert.append((code, description[0], '179', subpart.text))
        self.db.executemany("INSERT INTO tank_cars VALUES (?, ?, ?, ?)", insert)
        pass