import os
import json

from typing import Any


def getFromLocal(varname: str) -> Any:
    with open("secrets.json", "r") as f:
        dic = json.load(f)
        return dic[varname]


def getVar(varname: str) -> Any:
    if varname in os.environ:
        val = os.environ.get(varname)
        return val
    else:
        return getFromLocal(varname)
