import os
import json

def getFromLocal(varname:str):
    with open("local_vars.json", "r") as f:
        dic = json.load(f)
        return dic[varname]

def getVar(varname:str):
    if varname in os.environ:
        return os.environ.get(varname)
    else:
        return getFromLocal(varname)