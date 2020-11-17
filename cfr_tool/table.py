import sqlite3
from prettytable import from_db_cursor
import re

class HazmatTable:
    def __init__(self, db, soup):
        # Maps hazmat table column numbers containing nonunique values to new tables and column names
        self.nonunique_map = {
            0: ("symbols", "symbol"),
            5: ("label_codes", "label_code"),
            6: ("special_provisions", "special_provision"),
            7: ("packaging_exceptions", "exception"),
            8: ("non_bulk_packaging", "requirement"),
            9: ("bulk_packaging", "requirement"),
            13: ("stowage_codes", "stowage_code")
        }
        self.db = db
        self.soup = soup


    def create_nonunique_table(self, table_name, col_name):
        self.db.executescript("DROP TABLE IF EXISTS {};".format(table_name))
        '''
        Packaging requirements will be loaded later. Nonbulk and bulk requirements will
        need a foreign key to this table.
        '''
        script = '''
                CREATE TABLE {} (
                hazmat_id integer not null,
                {} text,
                FOREIGN KEY (hazmat_id) REFERENCES hazmat_table (hazmat_id)
                )'''.format(table_name, col_name)
        
        if table_name == "non_bulk_packaging" or table_name == "bulk_packaging":
            self.db.executescript(
                script[:-1] + ''',
                FOREIGN KEY (requirement) REFERENCES packaging_requirements (requirement))
                ''')
        else:
            self.db.executescript(script)
        
        


    def load_nonunique_table(self, hazmat_id, text, table_name, col_name):
        if table_name == "symbols":
            split_text = re.findall("[A-Z]", text)
        else:
            # TO DO: some are split on "," without a space
            split_text = text.split(",")
        entries = [(hazmat_id, entry.replace("'", "''").strip())
                for entry in split_text]
        self.db.executemany(
            "INSERT INTO {} (hazmat_id, {}) VALUES (?, ?)".format(
                table_name, col_name),
            entries)


    def create_hazmat_entries(self):
        '''
        This loops through the hazmat table to create entries for insertion and
        simultaneously calls 'load_nonunique_table' to insert values into those tables
        while parsing.
        '''
        hazmat_tables = self.soup.find_table("§ 172.101 Hazardous Materials Table")
        pk = 1
        entries = []
        rows = hazmat_tables.find_all('row')[1:]
        #Checking that first row is 'Accellerene'
        assert rows[0].find_all('ent')[1].text.strip() == \
            'Accellerene, see p-Nitrosodimethylaniline'
        for row in rows:
            ents = row.find_all('ent')
            vals = [pk]
            for i, ent in enumerate(ents):   
                if ent:                
                    if ent.text.strip() == '' and i == 3:
                        '''
                        i == 3 is the UNNA column. If it's blank, load the prior UNNA. If
                        the prior name and hazard class from the previous entry wasn't
                        blank, copy from those and load in the prior entry's symbol if it
                        wasn't blank.
                        '''
                        vals.append(entries[-1][3])
                        if not vals[1]:
                            vals[1] = entries[-1][1]
                        if not vals[2]:
                            vals[2] = entries[-1][2]
                        if prior_symbol != '':
                            self.load_nonunique_table(
                                pk, prior_symbol, "symbols", "symbol")
                    elif i == 3:
                        prior_symbol = symbol
                    if i == 0:
                        symbol = ent.text.strip()
                    if ent.text.strip() != '':
                        if i in self.nonunique_map.keys():
                            self.load_nonunique_table(pk, ent.text, *self.nonunique_map[i])
                        else:
                            vals.append(ent.text.strip().replace("'", "''"))
                    elif not i in self.nonunique_map.keys():
                        vals.append(None)
            vals = (vals + [None] * 7)[:8]
            assert len(vals) == 8
            entries.append(tuple(vals))
            pk += 1
        return entries

    def create_load_hazmat_data(self):
        self.db.executescript("DROP TABLE IF EXISTS hazmat_table;")
        for table_name, column in self.nonunique_map.values():
            self.create_nonunique_table(table_name, column)
        self.db.executescript(
            '''
            CREATE TABLE hazmat_table (
                hazmat_id integer not null primary key,
                hazmat_name text, class_division text,
                unna_code text, pg text, rail_max_quant text,
                aircraft_max_quant text, stowage_location text
            );
            '''
        )
        self.db.executescript(
            '''
            CREATE TABLE IF NOT EXISTS packaging_requirements (
                requirement text,
                packaging_code text
            )
            '''
        )
        self.db.executemany(
            '''
            INSERT INTO 'hazmat_table' (
                'hazmat_id',
                'hazmat_name',
                'class_division',
                'unna_code',
                'pg',
                'rail_max_quant',
                'aircraft_max_quant',
                'stowage_location'
                )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', self.create_hazmat_entries()
        )
            

    def get_packaging_173(self, bulk, hazmat_id):
        if bulk:
            table_name = "bulk_packaging"
        else:
            table_name = "non_bulk_packaging"
        requirement = self.db.execute(
            '''
            SELECT requirement FROM {} 
            WHERE hazmat_id = {}
            '''.format(
                table_name, hazmat_id))
        subpart = requirement.fetchall()[0][0]
        print("the subpart")
        print(int(subpart))
        return self.soup.get_subpart_text(173, int(subpart))

    