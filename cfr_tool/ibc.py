import regex as re
from . import packaging_standards as ps

class IBC(ps.PackagingStandards):
    START = 705
    END = 710
    def __init__(self, db, soup):
        PackagingStandards.__init__(self, db, soup)
        self.categories = self.get_categories(self.START, self.END)
