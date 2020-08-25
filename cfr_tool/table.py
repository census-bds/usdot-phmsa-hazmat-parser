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

def create_tables(db):

    '''
    if not os.path.isfile('hazmat-parser.sqlite'):
        # comment out when running a flask app
        
        db = sqlite3.connect(
            os.path.join(os.getcwd(), 'hazmat-parser.sqlite'),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
    '''
    db.executescript("DROP TABLE IF EXISTS hazmat_table;")
    db.executescript(
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

    for table_name, column in soup.NONUNIQUE_MAP.values():
        create_nonunique_table(db, table_name, column)

    hazmat_table = list(
        filter(lambda x: "Hazardous Materials Table" in x.find('ttitle').contents[0],
            soup.SOUP.find_all('gpotable')))[0]
    print("found the hazmat table")

    pk = 1
    for row in hazmat_table.find_all('row')[1:]:
        # TO DO: check that data starts at row 1
        load_ents(db, row, pk)
        pk += 1
        print("pk is ", pk)
        
    db.commit()