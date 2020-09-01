import requests
import bs4
import xml.etree.ElementTree as ET

class Soup:
    def __init__(self):
    # govinfo xml url from which to parse the hazmat table
        self.url = 'https://www.govinfo.gov/content/pkg/CFR-2019-title49-vol2/xml/CFR-2019-title49-vol2.xml'
        self.cfr = requests.get(self.url)
        self.parsed_soup = bs4.BeautifulSoup(self.cfr.text, 'lxml')
    
    def find_table(self, table_title):
        tables = self.parsed_soup.find_all('gpotable')
        return [table for table in tables if table.find('ttitle') \
            and table.find('ttitle').text == table_title][0]
    
    def get_subpart_text(self, part, subpart):
        subpart_tag = self.parsed_soup.find(
            'sectno', text="§ {}.{}".format(str(part), str(subpart)))
        return subpart_tag.parent

