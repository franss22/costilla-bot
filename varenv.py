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
        try:
            assert val is not None
        except AssertionError as e:
            raise ValueError(f"{varname} was not found in ENV")
        return val
    else:
        return getFromLocal(varname)
