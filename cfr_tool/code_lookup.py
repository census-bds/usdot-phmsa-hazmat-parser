import json
import flask

def code_lookup():
    code = flask.request.args.get("code")
    if code:
        return json.dumps({"the code is": code})
    else:
        return json.dumps({"a test of": "an api endpoint"})
