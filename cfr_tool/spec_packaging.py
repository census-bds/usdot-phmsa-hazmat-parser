from . import soup
import regex as re
#need to rename repo without hyphen so this won't be necessary
import importlib
pattern =  importlib.import_module("cfr_tool.phmsa-package-regexps.patterns")

class SpecPackaging:
    def __init__(self, db):
        self.s = soup.Soup(3)
    
    def get_subparts(self, part):
        part = self.s.parsed_soup.find_all('ear', text='Pt. {}'.format(part))[0].parent
        subparts = part.find_all('hd')
        return [subpart for subpart in subparts \
            if "Subpart" in subpart.text and "Specifications" in subpart.text]

    def get_sects_subjects(self):
        subparts = self.get_subparts(178)
        output = []
        for subpart in subparts:
            sectnos = subpart.parent.find_all('sectno')
            for sectno in sectnos:
                subject = sectno.find_next()
                if subject.name != 'subject':
                    continue
                spec_pattern = re.compile(pattern.SPEC_PACKAGING)
                match = spec_pattern.findall(subject.text)
                if len(match) == 0:
                    continue
                assert len(match) == 1
                output.append((sectno.text, match[0][0], match[0][1]))
        return output
    
    def get_tank_cars(self):
        subparts = self.get_subparts(179)
        for subpart in subparts:
            tank_car_pattern = re.compile(pattern.TANK_CAR_CODE)
            codes = tank_car_pattern.findall(subpart.text)
            description_pattern = re.compile(pattern.TANK_CAR_DESCRIPTION)
            description = description_pattern.findall(subpart.text)
            print(codes)
            print(description)
            print()