# hazmat-parser

This tool parses Title 49 of the CFR for regulations about shipping hazardous materials.

## Set up

Download requirements or create a new environment using the provided requirements.txt file. Run flask in development mode with FLASK_APP=cfr_tool. To initialize the database, choose a directory where your database will be saved, and enter the path after the DATABASE_PATH variable within cfr_tool/db.py. For example, the variable is currently set to `DATABASE_PATH = '/phmsa/hazmat-parser/instance'`. Modify that path to your location of choice. Afterwards,  run `flask init-db` before `flask run`. The command `flask init-db` initializes the database and will store the file hazmat_parser.sqlite within your chosen directory. Once the database is initialized, `flask init-db` will no longer be necessary.
<br>
For Linux and Mac:
```
$ export FLASK_APP=cfr_tool
$ export FLASK_ENV=development
$ flask init-db
$ flask run
```
For Windows cmd:
```
> set FLASK_APP=cfr-tool
> set FLASK_ENV=development
> flask init-db
> flask run
```
For Windows PowerShell
```
> $env:FLASK_APP = "cfr_tool"
> $env:FLASK_ENV = "development"
> flask init-db
> flask run
```
Open a browser and type in http://127.0.0.1:5000/packaging.

## Using the Web App

The web app within http://127.0.0.1:5000/packaging displays an option for searching the packaging regulations by UNNA number and bulk/non bulk. UNNA number should be searched in the format 'UNXXXX'.
![unna_search](images/unna_search.PNG)

Searches of UNNA numbers with packaging instructions that vary by packing group will then be asked to specify the packing group. For example UN3271 has different packaging instructions for packing group II and III.
![un3271_pg](images/un3271_pg.PNG)

Search results will display placeholders (currently incomplete) for quantity limitations and special provisions, along with the corresponding packaging instructions in part 173. Throughout the text, UNNA packaging numbers are highlighted.
![un3271_pgiii_nonbulk](images/un3271_pgiii_nonbulk.PNG)

Highlighted UNNA packaging numbers are clickable and will return corresponding packaging standards in the green box to the right. For example, 11G within 173.241 was parsed successfully and will return packaging standards within 178.708. However, many tank car codes and some specification packaging are not yet successfully parsed to match with its packaging standards. Those codes are highlighted but will not return a packaging standard when clicked.
![standards_241_11G](images/standards_241_11G.PNG)

## Using the Database

A complete ER diagram of the database exists in 'CFR Database ER Diagram.pdf' and data dictionary within 'data_dictionary.pdf'.

