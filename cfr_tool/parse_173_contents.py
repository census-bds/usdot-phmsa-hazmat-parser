import soup
import csv
import sqlite3

s = soup.Soup(2)
contents = s.parsed_soup.findAll(
    'hd',
    text='PART 173—SHIPPERS—GENERAL REQUIREMENTS FOR SHIPMENTS AND PACKAGINGS')[0].find_next(
        'contents')
sectnos = [tag.text[tag.text.find('.') + 1:] for tag in contents.findAll('sectno')]
subjects = [tag.text for tag in contents.findAll('subject')]
db = sqlite3.connect('test.db')
cur = db.cursor()

nb_query = cur.execute(
    '''
    select requirement, count(requirement) from non_bulk_packaging group by requirement;
    ''')
nb = nb_query.fetchall()
b_query = cur.execute(
    '''
    select requirement, count(requirement) from bulk_packaging group by requirement;
    ''')
b = b_query.fetchall()
sectno_counts = {sectno: 0 for sectno in sectnos}
for req, freq in nb:
    if sectno_counts.get(req) != None:
        sectno_counts[req] = sectno_counts[req] + freq
for req, freq in b:
    if sectno_counts.get(req) != None:
        sectno_counts[req] = sectno_counts[req] + freq

with open('part_173_summary.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for i, sect in enumerate(sectnos):
        writer.writerow([sect, subjects[i], sectno_counts[sect]])
