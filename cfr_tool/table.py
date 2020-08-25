import sqlite3
from prettytable import from_db_cursor
import re
from .soup import Soup

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

CFR_SOUP = Soup()

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
            elif i in NONUNIQUE_MAP.keys():
                load_nonunique_table(db, pk, ent.text, *NONUNIQUE_MAP[i])
            else:
                cols.append(INDEX_MAP[i])
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

    for table_name, column in NONUNIQUE_MAP.values():
        create_nonunique_table(db, table_name, column)

    hazmat_table = CFR_SOUP.get_hazmat_table()

    pk = 1
    for row in hazmat_table.find_all('row')[1:]:
        # TO DO: check that data starts at row 1
        load_ents(db, row, pk)
        pk += 1
        print("pk is ", pk)

    db.commit()

def get_packaging_173(bulk, hazmat_id, db):
    if bulk:
        table_name = "bulk_packaging"
    else:
        table_name = "non_bulk_packaging"
    requirement = db.execute(
        '''
        SELECT requirement FROM {} 
        WHERE hazmat_id = {}
        '''.format(
            table_name, hazmat_id))
    subpart = requirement.fetchall()[0][0]
    print("the subpart")
    print(int(subpart))
    return CFR_SOUP.get_subpart_text(173, int(subpart))

def build_results(un_id, bulk, db):
    
    hazmat_id_query = db.execute(
        '''
        SELECT hazmat_id, hazmat_name, class_division FROM hazmat_table
        WHERE id_num = '{}';
        '''.format(un_id))
    #TO DO : right now we take the first one, need to address UNIDs with >1 row
    hazmat_id, hazmat_name, class_division = hazmat_id_query.fetchone()
    
    return {'UNID': un_id,
            'hazmat_name': hazmat_name,
            'bulk': 'Bulk' if bulk else 'Non-Bulk',
            'forbidden': True if class_division == 'Forbidden' else False,
            'text': get_packaging_173(bulk, hazmat_id, db)}