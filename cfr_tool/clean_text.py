import re

'''
Some utility functions for parsing and cleaning text.
'''

def clean_new_lines(ent):
    return ent.text.strip('\n').replace('\n', ' ')

def parse_packaging_codes(text):
    #TO DO: make look behind a fixed width pattern
    pattern = re.compile('(?<=(..\()|(\sor\s))(\d[A-Z]\d?(/\d)*)*(?=(\)|(\sor\s)))')
    return pattern.findall(text)

def parse_packaging_names(text):
    pattern = re.compile('[a-zA-Z,\s-]+(?=((\s)|(\W))*\((\w|\s|/)*\))')
    return pattern.findall(text)

    