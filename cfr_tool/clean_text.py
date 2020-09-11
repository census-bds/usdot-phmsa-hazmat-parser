import regex as re

'''
Some utility functions for parsing and cleaning text.
'''

def clean_new_lines(ent):
    return ent.text.strip('\n').replace('\n', ' ')

def parse_names_codes(text):
    pattern = re.compile(
        '((?<!\d)(?<=\s|^|.\s|.)[^\d\(\).]+\w+(?=[\s|-]\(\d+[A-Z]))|(?<=\(|\sor\s)(\d+[A-Z]+\d?(/\d)*)(?=\)|\sor\s)')
    results = pattern.findall(text)
    last_name = None
    output = []
    for name, code, slashes in results:
        if name:
            last_name = name.strip()
        if slashes:
            base = code[0:code.find("/")]
            output.append((base, last_name))
            for trailing_number in code[code.find("/"):].split("/"):
                if trailing_number:
                    output.append((base[:-1] + trailing_number, last_name))
        if code and slashes == '':
            output.append((code, last_name))
    return output