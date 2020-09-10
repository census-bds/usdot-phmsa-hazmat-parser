import regex as re

'''
Some utility functions for parsing and cleaning text.
'''

def clean_new_lines(ent):
    return ent.text.strip('\n').replace('\n', ' ')

def parse_packaging_codes(text):
    #TO DO: deal with longer lists like those in PI 117: metal (11A), (11B), (11N), (21A), (21B), (21N), (31A), (31B), (31N)
    pattern = re.compile('(?<=(\()|(\sor\s))(\d+[A-Z]\d?(/\d)*)(?=(\)|(\sor\s)))')
    matches = pattern.findall(text)
    codes = []
    first_entry = None
    for match in matches:
        if match[4] == ' or ' and match[5] == ' or ':
            first_entry = match[2]
        elif first_entry and match[1] == ' or ':
            entry = (match[2], first_entry)
            codes.append(entry)
            first_entry = None
        else:
            codes.append(match[2])
    return codes

def parse_packaging_names(text):
    #TO DO: deal with typos where there is no space after a period
    pattern = re.compile('((?<!\d)(?<=\s|^|.\s|.)[^\d\(\).]+(?=[\s|-]\(\d+[A-Z]))')
    return [t.strip() for t in pattern.findall(text)]

    