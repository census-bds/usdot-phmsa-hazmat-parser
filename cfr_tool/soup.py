import requests
import bs4
import xml.etree.ElementTree as ET

#TO DO: switch from bs4 to ElementTree since I'm having trouble downloading lxml

# govinfo xml url from which to parse the hazmat table
CFR_URL = 'https://www.govinfo.gov/content/pkg/CFR-2019-title49-vol2/xml/CFR-2019-title49-vol2.xml'

# Maps hazmat table column numbers to column names
INDEX_MAP = {
    1: "hazmat_name",
    2: "class_division",
    3: "id_num",
    4: "pg",
    10: "rail_max_quant",
    11: "aircraft_max_quant",
    12: "stowage_location"
}
# Maps hazmat table column numbers containing nonunique values to new tables and column names
NONUNIQUE_MAP = {
    0: ("symbols", "symbol"),
    5: ("label_codes", "label_code"),
    6: ("special_provisions", "special_provision"),
    7: ("packaging_exceptions", "exception"),
    8: ("non_bulk_packaging", "requirement"),
    9: ("bulk_packaging", "requirement"),
    13: ("stowage_codes", "stowage_code")
}
print("initializing..")
cfr = requests.get(CFR_URL)
print("got cfr")
SOUP = bs4.BeautifulSoup(cfr.text, 'lxml')
