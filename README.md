# hazmat-parser

This tool parses Title 49 of the CFR for regulations about shipping hazardous materials.

## Instructions

Run flask in development mode with FLASK_APP=cfr-tool.
<br>
For Linux and Mac:
```
$ export FLASK_APP=cfr-tool
$ export FLASK_ENV=development
$ flask run
```
For Windows cmd:
```
> set FLASK_APP=cfr-tool
> set FLASK_ENV=development
> flask run
```
For Windows PowerShell
```
> $env:FLASK_APP = "cfr_tool"
> $env:FLASK_ENV = "development"
> flask run
```
Open a browser and type in http://127.0.0.1:5000/packaging.