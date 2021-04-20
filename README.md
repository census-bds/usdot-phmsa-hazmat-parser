# hazmat-parser

This tool parses Title 49 of the CFR for regulations about shipping hazardous materials.

## Instructions

Download requirements or create a new environment using the provided requirements.txt file. Run flask in development mode with FLASK_APP=cfr_tool. To initialize the database, be sure to run `flask init-db` before `flask run`. Once the database is initialized, `flask init-db` will no longer be necessary.
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

## Web App

![unna_search](images/unna_search.PNG)
