import json
import os


def getFromLocal(varname: str) -> str:
    with open("secretsDungeonmarch.json", "r") as f:
        dic = json.load(f)
        return dic[varname]


def getVar(varname: str) -> str:
    if varname in os.environ:
        return os.environ.get(varname)
    else:
        return getFromLocal(varname)
