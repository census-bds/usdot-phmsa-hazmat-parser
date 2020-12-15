from . import soup

class SpecPackaging:
    def __init__(self, db):
        self.s = soup.Soup(3)
        self.part_178 = self.s.parsed_soup.find_all('ear', text='Pt. 178')[0].parent

    def get_sects_subjects(self):
        #sectnos_178 = self.part_178.find_all('sectno')
        subparts = self.part_178.find_all('hd')
        subparts = [subpart for subpart in subparts \
            if "Subpart" in subpart.text and "Specifications" in subpart.text]
        for subpart in subparts:
            sectnos = subpart.parent.find_all('sectno')
            for sectno in secnos:
                subject = sectno.find_next()
                assert subject.name == 'subject'
                
        return {sect.text: sect.find_next().text for sect in sectnos_178 \
            if sect.find_next().text[:13] == 'Specification'} 
    