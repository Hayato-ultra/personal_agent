from agents import (
    function_tool
)
import json
import os


@function_tool
def launch_app(name) :
    '''opens windows application by its name  '''
    with open("tools\\apps.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    app=data["applications"].get(name)
    if app:
        os.startfile(app["path"])
        return "app opened successfully"
    else:
        return "app not found"
