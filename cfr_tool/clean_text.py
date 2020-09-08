import re

'''
Some utility functions for parsing and cleaning text.
'''

def clean_new_lines(ent):
    return ent.text.strip('\n').replace('\n', ' ')

def parse_packaging_codes(text):
    pattern = re.compile('\d\w\d?')
    return pattern.findall(text)

    