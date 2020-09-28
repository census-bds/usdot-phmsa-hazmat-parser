import os

import requests
import bs4
import xml.etree.ElementTree as ET

class Soup:
    CACHE_DIRECTORY = "cfr_cache"
    def __init__(self, volume):
        # govinfo xml url from which to parse the hazmat table
        self.cfr = 
        self.parsed_soup = bs4.BeautifulSoup(self.cfr, 'lxml')
        self.volume = volume


    def get_cfr_xml(self, volume):
        self.url = 'https://www.govinfo.gov/content/pkg/CFR-2019-title49-vol{}/xml/CFR-2019-title49-vol{}.xml'.format(
            str(volume), str(volume)
        )
       	self.cache_path = os.path.join(self.CACHE_DIRECTORY, self.url.split("/")[-1] )
        if os.path.exists(self.cache_path):
            with open(self.cache_path) as cache_xml:
                xml = cache_xml.read()
        else:
            xml = requests.get(self.url).text
            with open(self.cache_path, "w+") as cache_xml:
                cache_xml.write(xml)
 
        return xml
            
    
    def find_table(self, table_title):
        tables = self.parsed_soup.find_all('gpotable')
        return [table for table in tables if table.find('ttitle') \
            and table.find('ttitle').text == table_title][0]
    
    def get_subpart_text(self, part, subpart):
        subpart_tag = self.parsed_soup.find(
            'sectno', text="§ {}.{}".format(str(part), str(subpart)))
        return subpart_tag.parent

