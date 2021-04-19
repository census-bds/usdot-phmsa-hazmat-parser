import networkx as nx
import regex as re
from . import clean_text as ct
from . import patterns

'''
TO DO:
Change this to be a class tha represents performance packaging standards in general.
Convert specific subparts to be children of this class.
'''

class PackagingCodes:
    def __init__(self, db, soup):
        self.db = db
        self.soup = soup
        self.categories = []
        self.part = None


    def get_spans_paragraphs(self, subpart, pattern='performance'):
        #TO DO: make part a property of the child classes and add it as an argument in this function.
        '''
        Extracts packaging codes and the associated text in its tag
        NOte: removed start and end functionality from this. let it loop through in child classes.
        '''
        #Find the code pattern which is digits, letters, digits
        #TO DO: fix it so that it will only capture one or two digits at the beginning of a string or with white space preceding.
        if pattern == 'performance':
            code_pattern = re.compile(patterns.PERF_PACKAGING)
        elif pattern == 'tank_car':
            code_pattern = re.compile(patterns.SPEC_PACKAGING_INSTRUCTIONS)
        subpart_tag = self.soup.get_subpart_text(self.part, subpart)
        if subpart_tag:
            paragraphs = self.soup.get_subpart_paragraphs(self.part, subpart)
            paragraphs = [p.text for d, p in paragraphs.nodes().data('paragraph')]
            spans = []
            for p in paragraphs:

                matches = []
                agencies = []
                if pattern == 'tank_car':
                    for pattern_string in patterns.AA_PATTERN:
                        agency_pattern = re.compile(pattern_string)
                        for m in agency_pattern.finditer(p):
                            agencies.append(m.span())

                for m in code_pattern.finditer(p):
                    code_span = m.span()
                    if agencies:
                        '''
                        Find the nearest occurence of an agency right before the code
                        This should be the smallest positive value of the difference
                        between the code span and the agency span.
                        '''
                        diffs = {code_span[0] - agency[0]: i \
                            for i, agency in enumerate(agencies)}
                        positive_vals = [i for i in diffs.keys() if i > 0]
                        closest_span = agencies[diffs[min(positive_vals)]]
                        if not closest_span in matches:
                            matches.append(closest_span)
                    matches.append(code_span)
                spans.append(matches)
            return spans, paragraphs
            
    def get_codes(self, req, pattern='performance'):
        spans_paragraphs = self.get_spans_paragraphs(req, pattern)
        if spans_paragraphs:
            codes, descs = spans_paragraphs
            packaging_ids = []
            for spans, desc in zip(codes, descs):
                for span in spans:
                    packaging_ids.append(desc[span[0]: span[1]])
            return packaging_ids


    def get_codes_descriptions(self, subpart):
        spans, paragraphs = self.get_spans_paragraphs(subpart)
        codes = [p[s[0][0]:s[-1][1] + 1].strip() for p, s in zip(paragraphs, spans) if s]
        descs = []
        for p, s in zip(paragraphs, spans):
            if s:
                code_span = (s[0][0], s[-1][1] + 1)
                if code_span[0] == 0:
                    descs.append(p[code_span[1]:len(p)].strip())
                elif code_span[1] - 1 == len(p):
                    descs.append(p[0:code_span[0]].strip())
                else:
                    #TO DO: Figure out what to do in a potential case where the codes are in the middle.
                    #For now, just take the end
                    descs.append(p[code_span[1]:len(p)].strip())
        return tuple(zip(codes, descs))

