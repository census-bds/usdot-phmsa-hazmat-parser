import networkx as nx
import regex as re
from . import clean_text as ct
from . import patterns

'''
TO DO:
Change this to be a class tha represents performance packaging standards in general.
Convert specific sections to be children of this class.
'''

class PackagingCodes:
    def __init__(self, db, soup):
        self.db = db
        self.soup = soup
        self.categories = []
        self.part = None
        self.perf_code_pattern = re.compile(patterns.PERF_PACKAGING)
        self.spec_code_pattern = re.compile(patterns.SPEC_PACKAGING_INSTRUCTIONS)
        self.agency_patterns = [re.compile(p) for p in patterns.AA_PATTERN]

    def grab_agency_code_pattern(self, req):
        '''
        Loops through paragraphs in a section and returns all the codes found in the form
        of a list of tuples for insertion into the database with the info 
        (requirement, authorizing_agency, packaging_code, pattern_match)
        '''
        paragraphs = self._grab_paragraphs(req)
        if paragraphs:
            codes = []
            for p in paragraphs:
                agency_spans = []
                agencies = []
                code_spans = []
                for agency_pattern in self.agency_patterns:
                    for m in agency_pattern.finditer(p[1]):
                        agency_spans.append(m.span())
                        agencies.append(m.group())
                for m in self.spec_code_pattern.finditer(p[1]):
                    code_span = m.span()
                    code = m.group()
                    diffs = {code_span[0] - agency[0]: i \
                        for i, agency in enumerate(agency_spans)}
                    positive_vals = [i for i in diffs.keys() if i > 0]
                    closest_agency = agencies[diffs[min(positive_vals)]]
                    codes.append(
                        (req, closest_agency, code, 'spec', p[0], code_span[0], code_span[1])
                    )
                    code_spans.append(code_span)
                for m in self.perf_code_pattern.finditer(p[1]):
                    code_span = m.span()
                    code = m.group()
                    if not self._check_overlap(code_span, code_spans):
                        codes.append(
                            (req, None, code, 'perf', p[0], code_span[0], code_span[1])
                        )
            return codes

    def grab_pattern_match_spans(self, p):
        '''
        Takes a paragraph and returns a list of character spans to be highlighted
        for specification and performance codes. This includes the nearest preceding
        agency abbreviation (i.e. DOT, AAR, etc.) It checks for SPEC_PACKAGING_INSTRUCTIONS
        first, checks for the agencies, and then checks for PERF_PACKAGING last to avoid
        overlap.
        '''
        matches = []
        agencies = []
        for agency_pattern in self.agency_patterns:
            for m in agency_pattern.finditer(p):
                agencies.append(m.span())
        for m in self.spec_code_pattern.finditer(p):
            code_span = m.span()
            diffs = {code_span[0] - agency[0]: i \
                for i, agency in enumerate(agencies)}
            positive_vals = [i for i in diffs.keys() if i > 0]
            closest_span = agencies[diffs[min(positive_vals)]]
            if not closest_span in matches:
                matches.append(closest_span)
            matches.append(code_span)
        for m in self.perf_code_pattern.finditer(p):
            code_span = m.span()
            if not self._check_overlap(code_span, matches):
                matches.append(code_span)
        return matches
    
    def _check_overlap(self, code_span, matches):
        for match in matches:
            for i in range(code_span[0], code_span[1]):
                if i >= match[0] and i < match[1]:
                    return True
        return False
    
    def _grab_paragraphs(self, section):
        section_tag = self.soup.get_section_text(section)
        if section_tag:
            paragraphs = self.soup.get_section_paragraphs(section)
            return [(d, p.text) for d, p in paragraphs.nodes().data('paragraph')]

    def get_spans_paragraphs(self, section):
        '''
        Extracts packaging codes and the associated text in its tag
        NOte: removed start and end functionality from this. let it loop through in child classes.
        TO DO: convert into a single function which parses both performance and spec packaging.
        '''
        paragraphs = self._grab_paragraphs(section)
        if paragraphs:
            spans = []
            for p in paragraphs:
                spans.append(self.grab_pattern_match_spans(p[1]))
            return spans, paragraphs
            
    def get_codes(self, req):
        spans_paragraphs = self.get_spans_paragraphs(req)
        if spans_paragraphs:
            codes, descs = spans_paragraphs
            packaging_ids = []
            for spans, desc in zip(codes, descs):
                for span in spans:
                    packaging_ids.append(desc[1][span[0]: span[1]])
            return packaging_ids


    def get_codes_descriptions(self, section):
        spans, paragraphs = self.get_spans_paragraphs(section)
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

