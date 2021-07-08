import sqlite3
import pandas as pd

db = sqlite3.connect('instance/hazmat-parser.sqlite')
cur = db.cursor()
cur.execute(
    "select name from sqlite_master where type='table'; ")
tables = cur.fetchall()

for table in tables:
    table_df = pd.read_sql_query("SELECT * FROM {};".format(table[0]), db)
    table_df.to_csv('csvs/{}.csv'.format(table[0]))