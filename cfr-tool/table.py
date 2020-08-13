import sqlite3
from prettytable import from_db_cursor
import re
from . import soup

def create_nonunique_table(db, table_name, col_name):
    db.executescript("DROP TABLE IF EXISTS {};".format(table_name))
    db.executescript('''
            CREATE TABLE {} (
            hazmat_id integer not null,
            {} text,
            FOREIGN KEY (hazmat_id)
            REFERENCES hazmat_table (hazmat_id)
            )
            '''.format(table_name, col_name)
    )
    db.commit()
    print("created table ", table_name)


def load_nonunique_table(db, hazmat_id, text, table_name, col_name):
    if table_name == "symbols":
        split_text = re.findall("[A-Z]", text)
    else:
        # TO DO: some are split on "," without a space
        split_text = text.split(", ")
    entries = [(hazmat_id, entry.replace("'", "''").strip())
               for entry in split_text]
    db.executemany(
        "INSERT INTO {} (hazmat_id, {}) VALUES (?, ?)".format(
            table_name, col_name),
        entries)
    db.commit()
    print("loaded into ", table_name)


def load_ents(db, row, pk):
    ents = row.find_all('ent')
    if ents:
        cols = []
        vals = []
        for i, ent in enumerate(ents):
            if not ent or ent.text.strip() == '' or ent.text == "None":
                continue
            elif i in soup.NONUNIQUE_MAP.keys():
                load_nonunique_table(db, pk, ent.text, *soup.NONUNIQUE_MAP[i])
            else:
                cols.append(soup.INDEX_MAP[i])
                vals.append(ent.text.strip().replace("'", "''"))

        col_names = "', '".join(cols)
        val_names = str(pk) + ", '" + "', '".join(vals)
        db.executescript('''
        INSERT INTO 'hazmat_table' ('hazmat_id', '{}') VALUES ({}')
        '''.format(col_names, val_names)
        )
        db.commit()
        print("loaded ", col_names)