from . import soup
import regex as re
#need to rename repo without hyphen so this won't be necessary
import importlib
from . import patterns 

class SpecPackaging:
    def __init__(self, db):
        self.s = soup.Soup(3)
        self.db = db
        self.spec_data = self.get_sects_subjects()
        self.tank_cars = self.get_tank_cars()
    
    def get_sections(self, part):
        part = self.s.parsed_soup.find_all('ear', text='Pt. {}'.format(part))[0].parent
        all_sections = part.find_all('hd')
        non_content = [s for s in all_sections if s.parent.parent.name != 'contents']
        #avoid parsing the table of contents
        return [section for section in non_content \
            if "Standards" in section.text or "Specifications for" in section.text]

    def get_sects_subjects(self):
        sections = self.get_sections(178)
        output = []
        for section in sections:
            sectnos = section.parent.find_all('sectno')
            for sectno in sectnos:
                subject = sectno.find_next()
                if subject.name != 'subject':
                    continue
                spec_pattern = re.compile(patterns.SPEC_PACKAGING)
                match = spec_pattern.findall(subject.text)
                if not match:
                    continue
                assert len(match) == 1
                subsection = sectno.text[sectno.text.find('178.') + 4: len(sectno.text)]
                output.append((subsection, match[0][0], match[0][1]))
        return [(row[1], "specification", row[0]) for row in output]
    
    def load_packaging(self):
        self.db.executemany('''
            INSERT INTO packaging_specs (
                full_code,
                type,
                subsection
            ) VALUES (
                ?, ?, ?
            )
        ''', self.spec_data + self.tank_cars)
    
    def get_tank_cars(self):
        sections = self.get_sections(179)
        input = []
        for section in sections:
            tank_car_pattern = re.compile(patterns.TANK_CAR_CODE)
            codes = tank_car_pattern.findall(section.text)
            subsection = section.find_next().text
            subsect_no = subsection[
                subsection.find('179.') + 4: subsection.find('179.') + 7]
            for code in codes:
                input.append((code, "tank car", subsect_no))
        return input
            # not worrying about descriptions for now
            # description_pattern = re.compile(patterns.TANK_CAR_DESCRIPTION)
            # description = description_pattern.findall(section.text)
            # print(description)
            # print()