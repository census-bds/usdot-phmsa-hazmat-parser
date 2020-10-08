import networkx as nx
import regex as re
import clean_text as ct



'''
TO DO:
Change this to be a class tha represents packaging standards in general.
Convert specific subparts to be children of this class.
'''

class PackagingCodes:

    def __init__(self, db, soup):
        self.db = db
        self.soup = soup
        self.categories = []
    
    def get_codes_descriptions(self, start, end, definition_paragraph='a'):
        '''
        Extracts packaging codes and the associated text in its tag
        '''
        #Find the code pattern which is digits, letters, digits
        code_pattern = re.compile("(\d+[A-Z]+\d*)")
        categories_data = []
        for subpart in range(start, end + 1):
            subpart_tag = self.soup.get_subpart_text(self.PART, subpart)
            basic_type = subpart_tag.find("subject").text.split("for")[-1][:-1].strip()
            paragraphs = self.soup.get_subpart_paragraphs(self.PART, subpart)
            definitions = nx.subgraph(paragraphs, paragraphs[definition_paragraph])
            paragraphs = [p.text for d, p in definitions.nodes().data('paragraph')]
            spans = [[m.span() for m in code_pattern.finditer(p)] for p in paragraphs]
            # TODO: remove stopwords?
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
            types = [basic_type] *  len(codes)
            categories_data.append(tuple(zip(codes, descs, types)))
        return categories_data


