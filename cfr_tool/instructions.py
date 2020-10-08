from .packaging_codes import PackagingCodes
from .soup import Soup

class Instructions(PackagingCodes):
    PART = 173
    START = 201
    END = 202
    def __init__(self, db, soup):
        PackagingCodes.__init__(self, db, soup)
        self.code_descriptions = self.get_codes_descriptions(self.START, self.END)