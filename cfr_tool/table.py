import sqlite3
import re

class HazmatTable:
    def __init__(self, db, soup):
        # Maps hazmat table column numbers containing nonunique values to new tables and column names
        self.nonunique_map = {
            0: ("symbols", "symbol"),
            1: ("proper_shipping_names", "proper_shipping_name"),
            5: ("label_codes", "label_code"),
            6: ("special_provisions", "special_provision"),
            7: ("packaging_exceptions", "exception"),
            13: ("other_provisions", "other_provision")
        }
        self.db = db
        self.soup = soup
        self.see_shipping_names = []


    def create_nonunique_table(self, table_name, col_name):
        self.db.executescript("DROP TABLE IF EXISTS {};".format(table_name))
        script = '''
                CREATE TABLE {} (
                row_id integer not null,
                {} text,
                FOREIGN KEY (row_id) REFERENCES hazmat_table (row_id)
                )'''.format(table_name, col_name)
        
        self.db.executescript(script)
        
    def create_packaging_instructions_table(self):
        self.db.executescript(
            '''
            DROP TABLE IF EXISTS packaging_instructions;
            '''
        )
        self.db.executescript(
            '''
            CREATE TABLE packaging_instructions (
                row_id integer not null,
                section text,
                bulk integer,
                FOREIGN KEY (row_id) REFERENCES hazmat_table (row_id)
            )
            '''
        )


    def load_nonunique_table(self, row_id, text, table_name, col_name):
        if table_name == "symbols":
            split_text = re.findall("[A-Z]", text)
            entries = [(row_id, entry.replace("'", "''").strip()) for entry in split_text]
        elif table_name == "proper_shipping_names":
            entries = [(row_id, text)]

        else:
            # TO DO: some are split on "," without a space
            split_text = text.split(",")
            entries = [(row_id, entry.replace("'", "''").strip()) for entry in split_text]
        self.db.executemany(
            "INSERT INTO {} (row_id, {}) VALUES (?, ?)".format(
                table_name, col_name),
            entries)
    
    def load_packaging_instructions(self, row_id, section_num, i):
        if section_num.isdigit():
            self.db.execute(
                '''
                INSERT INTO packaging_instructions (row_id, section, bulk) VALUES (
                    {}, {}, {}
                )
                '''.format(
                    row_id, "173." + section_num, 0 if i == 8 else 1
                )
            )


    def create_hazmat_entries(self):
        '''
        This loops through the hazmat table to create entries for insertion and
        simultaneously calls 'load_nonunique_table' to insert values into those tables
        while parsing.
        '''
        hazmat_tables = self.soup.find_table(
            '§\u2009172.101 Hazardous Materials Table')
        pk = 1
        entries = []
        rows = hazmat_tables.find_all('row')[1:]

        #Checking that first row is 'Accellerene'
        assert rows[0].find_all('ent')[1].text.strip() == \
            'Accellerene, see p-Nitrosodimethylaniline'
        for row in rows:
            skip_row = False
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
                        vals.append(entries[-1][2])
                        if not vals[1]:
                            vals[1] = entries[-1][1]
                        if not vals[2]:
                            vals[2] = entries[-1][2]
                        if prior_symbol != '':
                            self.load_nonunique_table(
                                pk, prior_symbol, *self.nonunique_map[0])
                        self.load_nonunique_table(
                            pk, prior_psn, *self.nonunique_map[1]
                        )
                    elif i == 3:
                        prior_symbol = symbol
                    if i == 0:
                        symbol = ent.text.strip()
                    if ent.text.strip() != '':
                        if i in self.nonunique_map.keys():
                            if i == 1 and " see " in ent.text and len(ents) < 3:
                                '''
                                If the proper shipping name has ' see ' in it and
                                there is no UNNA value in that row, we temporarily
                                load with a row_id of 0 and go back one row_id.
                                '''
                                pk -= 1
                                self.see_shipping_names.append(ent.text)
                                skip_row = True
                                continue
                            else:
                                if i == 1:
                                    prior_psn = ent.text
                                self.load_nonunique_table(
                                    pk, ent.text, *self.nonunique_map[i])
                        elif i == 8 or i == 9:
                            self.load_packaging_instructions(pk, ent.text, i)
                        else:
                            vals.append(ent.text.strip().replace("'", "''"))                           
                    elif not i in self.nonunique_map.keys() and i != 3:
                        vals.append(None)
            pk += 1
            if skip_row:
                continue
            vals = (vals + [None] * 7)[:7]
            assert len(vals) == 7
            entries.append(tuple(vals))
        return entries

    def create_load_hazmat_data(self):
        self.db.executescript("DROP TABLE IF EXISTS hazmat_table;")
        for table_name, column in self.nonunique_map.values():
            self.create_nonunique_table(table_name, column)
        self.create_packaging_instructions_table()
        self.db.executescript(
            '''
            CREATE TABLE hazmat_table (
                row_id integer not null primary key,
                class_division text,
                unna_code text, pg text, passenger_max_quant text,
                cargo_max_quant text, stowage_location text
            );
            '''
        )
        self.db.executescript("DROP TABLE IF EXISTS packaging_requirements;")
        self.db.executescript(
            '''
            CREATE TABLE IF NOT EXISTS packaging_requirements (
                section text,
                authorizing_agency text,
                packaging_code text,
                pattern_match text,
                paragraph text,
                span_0 integer,
                span_1 integer
            )
            '''
        )
        self.db.executemany(
            '''
            INSERT INTO 'hazmat_table' (
                'row_id',
                'class_division',
                'unna_code',
                'pg',
                'passenger_max_quant',
                'cargo_max_quant',
                'stowage_location'
                )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', self.create_hazmat_entries()
        )
        self.handle_see_shipping_names()

    def handle_see_shipping_names(self):
        see_names_load = []
        for name in self.see_shipping_names:
            assert ' see ' in name
            see_name = name[name.find(' see ') + 5:].strip()
            real_row_id = self.db.execute(
                '''
                SELECT row_id
                FROM proper_shipping_names
                WHERE proper_shipping_name = ?
                ''', [see_name]
            )
            row_id = real_row_id.fetchone()
            if row_id:
                see_names_load.append((row_id[0], name))
            # TO DO: think of a way to address names that refer to more than one other row
        self.db.executemany(
            '''
            INSERT INTO proper_shipping_names (
                'row_id',
                'proper_shipping_name'
            )
            VALUES (
                ?, ?
            )
            ''', see_names_load
        )
            
                        

    def get_packaging_173(self, bulk, row_id):
        if bulk:
            table_name = "bulk_packaging"
        else:
            table_name = "non_bulk_packaging"
        requirement = self.db.execute(
            '''
            SELECT requirement FROM {} 
            WHERE row_id = {}
            '''.format(
                table_name, row_id))
        section = requirement.fetchall()[0][0]
        return self.soup.get_section_text(173, int(section))

    