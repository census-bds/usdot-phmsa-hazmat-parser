from collections import defaultdict
import logging
import os

import regex as re
import requests
import bs4
import xml.etree.ElementTree as ET
import networkx as nx

class Soup:
    CACHE_DIRECTORY = "cfr_cache"

    def __init__(self, volume):
        if not os.path.exists(self.CACHE_DIRECTORY):
            os.mkdir(self.CACHE_DIRECTORY)
        self.cfr = self.get_cfr_xml(volume)
        self.parsed_soup = bs4.BeautifulSoup(self.cfr, 'lxml')
        self.volume = volume


    def get_cfr_xml(self, volume):
        # govinfo xml url from which to parse the hazmat table
        self.url = 'https://www.govinfo.gov/content/pkg/CFR-2019-title49-vol{}/xml/CFR-2019-title49-vol{}.xml'.format(
            str(volume), str(volume)
        )
        self.cache_path = os.path.join(self.CACHE_DIRECTORY, self.url.split("/")[-1] )
        if os.path.exists(self.cache_path):
            logging.info("using cached CFR volume {}".format(volume))
            with open(self.cache_path) as cache_xml:
                xml = cache_xml.read()
        else:
            logging.info("downloading fresh CFR volume {}".format(volume))
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

    def get_subpart_paragraphs(self, part, subpart):
        """
        returns: a networkx graph object of the paragraphs of this subpart
        """
        subpart = self.get_subpart_text(part, subpart)
        paragraphs = subpart.find_all("p")
        indexed = list(self.gen_paragraph_tree(paragraphs))
        ret_tree = nx.Graph()
        for ix, paragraph in indexed:
            canonical = ".".join(i for i in ix if i)
            parent = ".".join(canonical.split(".")[:-1])
            ret_tree.add_node(canonical, paragraph=paragraph)
            if parent:
                ret_tree.add_edge(parent, canonical)

        return ret_tree 


    @staticmethod
    def gen_paragraph_tree(paragraphs):
        # this reflects the nested paragraph structure
        # e.g. you could look at
        # part 178 subpart 500 paragraph a subparagraph 1
        # sub-sub paragraph i sub-sub-sub paragraph A
        # i.e. 178.500 (a)(1)(i)(A)

        letter_pattern = re.compile(r'\((?=[a-z])([^i])\)') #all chars except i
        number_pattern = re.compile(r'\(([0-9]+)\)')
        numeral_pattern = re.compile(r'\(([ivx]+)\)') # this is horrible
        uppercase_letter_pattern = re.compile(r'\(([A-Z])\)')

        patterns = (letter_pattern, number_pattern, numeral_pattern, uppercase_letter_pattern)
        # letter, number, numeral, uppercase
        indices = [None, None, None, None]
        def _reset_indices_after(ix):
            for i in range(ix + 1, len(indices)):
                indices[i] = None

        for paragraph in paragraphs:
            beginning = paragraph.text.strip()[:6]
            for ix, pattern in enumerate(patterns):
                match = pattern.findall(beginning)
                if match:
                    assert len(match) == 1
                    indices[ix] = match[0]
                    _reset_indices_after(ix)
                    yield tuple(indices), paragraph
