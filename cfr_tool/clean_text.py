import regex as re

'''
Some utility functions for parsing and cleaning text.
'''

def clean_new_lines(ent):
    return ent.text.strip('\n').replace('\n', ' ')

def parse_packaging_codes(text):
    #TO DO: deal with longer lists like those in PI 117: metal (11A), (11B), (11N), (21A), (21B), (21N), (31A), (31B), (31N)
    pattern = re.compile('(?<=(\()|(\sor\s))(\d+[A-Z]+\d?(/\d)*)(?=(\)|(\sor\s)))')
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
    pattern = re.compile('(?<!\d)(?<=\s|^|.\s|.)[^\d\(\).]+\w+(?=[\s|-]\(\d+[A-Z])')
    return [t.strip() for t in pattern.findall(text)]

def parse_names_codes(text):
    pattern = re.compile(
        '((?<!\d)(?<=\s|^|.\s|.)[^\d\(\).]+\w+(?=[\s|-]\(\d+[A-Z]))|(?<=\(|\sor\s)(\d+[A-Z]+\d?(/\d)*)(?=\)|\sor\s)')
    results = pattern.findall(text)
    last_name = None
    output = {}
    for name, code, slashes in results:
        if name:
            output[name.strip()] = []
            last_name = name.strip()
        if slashes:
            base = code[0:code.find("/")]
            output[last_name].append(base)
            for trailing_number in code[code.find("/"):].split("/"):
                if trailing_number:
                    output[last_name].append(base[:-1] + trailing_number)
        if code and slashes == '':
            output[last_name].append(code)
    return output