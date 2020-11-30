import soup
import packaging_codes as pc

class NonBulkRequirements(pc.PackagingCodes):
    def __init__(self, db, soup):
        pc.PackagingCodes.__init__(self, db, soup)
        self.db = db
        self.soup = self.volume_check(soup)

    def volume_check(self, soup):
        assert soup.volume == 2
        return soup

    def get_packaging_codes(self, requirement):
        text_tags = self.soup.get_subpart_text(173, requirement).find_all()
        return text_tags
        
