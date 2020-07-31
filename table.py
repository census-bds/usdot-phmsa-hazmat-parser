import xml.etree.ElementTree as ET
import bs4
import requests
import sqlite3
from prettytable import from_db_cursor

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
soup = bs4.BeautifulSoup(cfr.text, 'lxml')
print("created soup")
conn = sqlite3.connect('cfr.db')
cur = conn.cursor()


def find_hazmat_table(table):
    table_title = table.find('ttitle')
    return table_title and ("Hazardous Materials Table" in table_title.contents[0])


def create_nonunique_table(cur, table_name, col_name):
    cur.execute('''
            CREATE TABLE {} (
            hazmat_id integer not null,
            {} text,
            FOREIGN KEY (hazmat_id)
            REFERENCES hazmat_table (hazmat_id)
            )
            '''.format(table_name, col_name))


def load_nonunique_table(cur, hazmat_id, text, table_name, col_name):
    if table_name == "symbols":
        # TO DO: fix the text splitting for symbols
        split_text = text.split(" ")
    else:
        split_text = text.split(", ")
    entries = [(hazmat_id, entry.replace("'", "''").strip())
               for entry in split_text]
    cur.executemany(
        "INSERT INTO {} (hazmat_id, {}) VALUES (?, ?)".format(
            table_name, col_name),
        entries)
    pass


def load_ents(row, pk, cur):
    ents = row.find_all('ent')
    if ents:
        cols = []
        vals = []
        for i, ent in enumerate(ents):
            if not ent or ent.text.strip() == '' or ent.text == "None":
                continue
            elif i in NONUNIQUE_MAP.keys():
                load_nonunique_table(cur, pk, ent.text, *NONUNIQUE_MAP[i])
            else:
                cols.append(INDEX_MAP[i])
                vals.append(ent.text.strip().replace("'", "''"))

        col_names = "', '".join(cols)
        val_names = str(pk) + ", '" + "', '".join(vals)
        cur.execute('''
        INSERT INTO 'hazmat_table' ('hazmat_id', '{}') VALUES ({}')
        '''.format(col_names, val_names)
        )


cur.execute(
    '''
    CREATE TABLE hazmat_table (
        hazmat_id integer not null primary key,
        hazmat_name text, class_division text,
        id_num text, pg text, rail_max_quant text,
        aircraft_max_quant text, stowage_location text
    );
    '''


)
print("created hazmat table")
conn.commit()

for table, column in NONUNIQUE_MAP.values():
    create_nonunique_table(cur, table, column)

hazmat_table = list(filter(find_hazmat_table, soup.find_all('gpotable')))[0]
pk = 1
for row in hazmat_table.find_all('row')[1:]:
    # TO DO: check that data starts at row 1
    load_ents(row, pk, cur)
    pk += 1

conn.commit()
