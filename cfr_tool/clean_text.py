import regex as re

'''
Some utility functions for parsing and cleaning text.
'''

def build_packaging_text(spans_paragraphs):
    '''
    Take a list with spans in index 0 and paragraphs in index 1 and apply a <mark> tag
    around the specified spans.
    '''
    print(spans_paragraphs)
    output_html = []
    for i, paragraph in enumerate(spans_paragraphs[1]):
        spans = spans_paragraphs[0][i]
        marked_par = paragraph[1]
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

def int_to_roman(input):
    """ Convert an integer to a Roman numeral. """
    # Taken from https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s24.html

    if not isinstance(input, type(1)):
        raise TypeError("expected integer, got %s" % type(input))
    if not 0 < input < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = []
    for i in range(len(ints)):
        count = int(input / ints[i])
        result.append(nums[i] * count)
        input -= ints[i] * count
    return ''.join(result)

def roman_to_int(input):
    """ Convert a Roman numeral to an integer. """
    # Taken from https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s24.html
    if not isinstance(input, type("")):
        raise TypeError("expected string, got %s" % type(input))
    input = input.upper(  )
    nums = {'M':1000, 'D':500, 'C':100, 'L':50, 'X':10, 'V':5, 'I':1}
    sum = 0
    for i in range(len(input)):
        try:
            value = nums[input[i]]
            # If the next place holds a larger number, this value is negative
            if i+1 < len(input) and nums[input[i+1]] > value:
                sum -= value
            else: sum += value
        except KeyError:
            raise ValueError('input is not a valid Roman numeral: %s' % input)
    # easiest test for validity...
    if int_to_roman(sum) == input:
        return sum
    else:
        raise ValueError('input is not a valid Roman numeral: %s' % input)

        