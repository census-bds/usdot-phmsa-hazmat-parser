import regex as re

'''
Some utility functions for parsing and cleaning text.
'''

def build_packaging_text(spans_paragraphs):
    '''
    Take a list with spans in index 0 and paragraphs in index 1 and apply a <mark> tag
    around the specified spans.
    '''
    output_html = []
    for i, paragraph in enumerate(spans_paragraphs[1]):
        spans = spans_paragraphs[0][i]
        marked_par = paragraph
        if spans:
            increment = 0
            for span in spans:
                beginning = marked_par[:span[0] + increment]
                mark = marked_par[span[0] + increment:span[1] + increment]
                end = marked_par[span[1] + increment:]
                marked_par = beginning + "<mark>" + mark + "</mark>" + end
                increment += 13
        output_html.append(marked_par)
    return output_html 

def clean_new_lines(ent):
    return ent.text.strip('\n').replace('\n', ' ')


def parse_names_codes(text):
    #This regex finds 3 groups: the description/name of the packaging, the code, and any slashes after the code (i.e. 5H1/2/3)
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

def parse_packaging_kind_material(texts):
    output = {"packaging_kinds": [], "packaging_materials": []}
    pattern_material = re.compile(
        '((?<=\\“)[A-Z](?=\\”\\smeans\\s))|((?<=means\s).*(?=\.))')
    pattern_kind = re.compile(
        '((?<=\\“)\d(?=\\”\\smeans\\s))|((?<=means\s).*(?=\.))')
    for text in texts:
        matches = pattern_kind.findall(text)
        if matches:
            if matches[0][0]:
                output["packaging_kinds"].append((matches[0][0], matches[1][1]))
            else:
                matches = pattern_material.findall(text)
                output["packaging_materials"].append((matches[0][0], matches[1][1]))
    return output

        