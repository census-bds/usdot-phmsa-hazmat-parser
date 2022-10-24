from collections import defaultdict
import logging
import os

import regex as re
import requests
import bs4
from datetime import date as dt

class Ecfr:
    CACHE_DIRECTORY = "cfr_cache"

    def __init__(self):
        if not os.path.exists(self.CACHE_DIRECTORY):
            os.mkdir(self.CACHE_DIRECTORY)

    def get_section_content(self, part, section, date=None):
        if not date:
            date = dt.today()
        self.url = "https://ecfr.federalregister.gov/api/renderer/v1/content/enhanced/{}-{}-{}/title-49?chapter=I&part={}&section={}".format(
            date.year, date.month, date.day, part, str(part) + "." + str(section)
        )
        self.cache_path = os.path.join(self.CACHE_DIRECTORY, str(part) + "." + str(section))
        if os.path.exists(self.cache_path):
            logging.info("using cached CFR section {}".format(section))
            with open(self.cache_path, encoding="utf-8") as cache_html:
                html = cache_html.read()
        else:
            logging.info("downloading fresh CFR section {}".format(section))
            html = requests.get(self.url).text
            with open(self.cache_path, "w+", encoding="utf-8") as cache_html:
                cache_html.write(html)
 
        return html

