import sqlite3
from prettytable import from_db_cursor
import re

import soup

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
        split_text = re.findall("[A-Z]", text)
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
            elif i in soup.NONUNIQUE_MAP.keys():
                load_nonunique_table(cur, pk, ent.text, *soup.NONUNIQUE_MAP[i])
            else:
                cols.append(soup.INDEX_MAP[i])
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
conn.commit()

for table, column in soup.NONUNIQUE_MAP.values():
    create_nonunique_table(cur, table, column)

hazmat_table = list(
    filter(find_hazmat_table, soup.SOUP.find_all('gpotable')))[0]
pk = 1
for row in hazmat_table.find_all('row')[1:]:
    # TO DO: check that data starts at row 1
    load_ents(row, pk, cur)
    pk += 1

conn.commit()
conn.close()
