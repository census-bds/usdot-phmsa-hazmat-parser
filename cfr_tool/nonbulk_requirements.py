import soup

class NonBulkRequirements:
    def __init__(self, db, soup):
        self.db = db
        self.soup = volume_check(soup)

    def volume_check(self, soup):
        assert soup.volume == 2
        return soup

    def get_packaging_codes(self, requirement):
        text_tags = soup.get_subpart_text(173, requirement).find_all()
        
