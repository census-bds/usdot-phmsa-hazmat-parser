import regex as re
from .packaging_standards import PackagingStandards 

class IBC(PackagingStandards):
    START = 705
    END = 710
    def __init__(self, db, soup):
        PackagingStandards.__init__(self, db, soup)
