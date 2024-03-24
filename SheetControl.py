import gspread  # type: ignore
import utils
from varenv import getVar
import json

from functools import wraps
from typing import Callable


PJ_SHEET_ID = 0
REPUTATION_SHEET_ID = 37818595
SUELDO_SHEET_ID = 1681819644

credentials = json.loads(getVar("GOOGLE"), strict=False)

gc = gspread.service_account_from_dict(credentials)

pj_sheet = gc.open("Megamarch").get_worksheet_by_id(PJ_SHEET_ID)
rep_sheet = gc.open("Megamarch").get_worksheet_by_id(REPUTATION_SHEET_ID)
sueldo_sheet = gc.open("Megamarch").get_worksheet_by_id(SUELDO_SHEET_ID)

PJ_DATA: list[list[str]]


def update_pj_data() -> None:
    global PJ_DATA
    PJ_DATA = pj_sheet.get_all_values(value_render_option="UNFORMATTED_VALUE")


def gets_pj_data(func) -> Callable:
    @wraps(func)
    async def wrapped_func(*args, **kwargs):
        update_pj_data()
        print("Updated PC data.")
        await func(*args, **kwargs)
    return wrapped_func


class PJ_COL:
    Name = "A"
    Discord_id = "B"
    Player = "C"
    Class = "D"
    Arquetypes = "E"
    Ancestry = "F"
    Heritage = "G"
    Downtime = "H"
    Money_pp = "I"
    Money_gp = "J"
    Money_sp = "K"
    Money_cp = "L"
    Money_total = "M"
    Languages = "N"
    Religion = "O"

    @classmethod
    def num(cls, col: str) -> int:
        return utils.column_to_num(col)


def whole_column_pj(column: str) -> list[str]:
    c_index: int = PJ_COL.num(column)

    return [row[c_index] for row in PJ_DATA]


class CharacterNotFoundError(Exception):
    pass


def get_pj_row(discord_id: int) -> int:
    try:
        column = whole_column_pj(PJ_COL.Discord_id)
        id_row = column.index(str(discord_id))
        # index del primer valor con [discord_id] de todos los ids (+1 por 0 indexed)
        return id_row
    except ValueError:
        raise CharacterNotFoundError(
            f"Character with discord ID '{discord_id}' was not found")


def first_empty_PJ_row() -> int:
    column = whole_column_pj(PJ_COL.Discord_id)
    return column.index("")+1


def get_pj_data(pj_row: int, col: str) -> str:
    try:
        return PJ_DATA[pj_row][PJ_COL.num(col)]
    except IndexError:
        raise CharacterNotFoundError()


def get_pj_full(row: int) -> list[str]:
    return PJ_DATA[row]


def get_pj_coins(row: int) -> list[float]:
    pp = PJ_COL.num(PJ_COL.Money_pp)
    total = PJ_COL.num(PJ_COL.Money_total)
    # pj_sheet.get(f"{PJ_COL.Money_pp}{row}:{PJ_COL.Money_total}{row}", value_render_option = "UNFORMATTED_VALUE")[0]
    coins = PJ_DATA[row][pp:total+1]
    return [float(x) for x in coins]


def update_range_PJ(values, pos: str):
    pj_sheet.update(values, pos)


def update_pj_data_cell(pj_row: int, col: str, value):
    pj_sheet.update(value, f"{col}{pj_row+1}")


def update_pj_coins(row: int, values):
    pj_sheet.update(
        values, f"{PJ_COL.Money_pp}{row+1}:{PJ_COL.Money_total}{row+1}")


REP_DATA: list[list[str]]


def update_rep_data()->None:
    global REP_DATA
    REP_DATA = rep_sheet.get_all_values(
        value_render_option="UNFORMATTED_VALUE")


def gets_rep_data(func)->Callable:
    @wraps(func)
    async def wrapped_func(*args, **kwargs):
        update_rep_data()
        print("Updated reputation data.")
        await func(*args, **kwargs)
    return wrapped_func


class REP_COL:
    Name = "A"
    Discord_id = "B"
    Faction = "C"
    Reputation = "D"

    @classmethod
    def num(cls, col: str)->int:
        return utils.column_to_num(col)


def first_empty_rep_row() -> int:
    column: list[str] = whole_column_rep(REP_COL.Discord_id)
    return len(column)+1


def whole_column_rep(column: str) -> list[str]:
    c_index: int = REP_COL.num(column)

    return [row[c_index] for row in REP_DATA]


def get_pj_reps(discord_id: int)->list[tuple[str, str, str, str, int]]:
    discord_id_str: str = str(discord_id)
    reps: list[tuple[str, str, str, str, int]] = [(row[0], row[1], row[2], row[3], REP_DATA.index(row)+1) for row in REP_DATA if row[REP_COL.num(REP_COL.Discord_id)] == discord_id_str]
    return reps


def update_rep_row(row_index: int, data: list):
    rep_sheet.update([data], f"A{row_index}:D{row_index}")


def get_pj_faction():
    pass


def get_all_existing_factions() -> set[str]:
    return set(whole_column_rep(REP_COL.Faction))


def get_sueldo(level: int):
    data = sueldo_sheet.get_all_values(value_render_option="UNFORMATTED_VALUE")
    sueldo_gp = data[level][2]
    sueldo_dt = data[3][3]
    return (float(sueldo_gp), int(sueldo_dt))


if __name__ == "__main__":
    # print(COL.name)
    # print(get_pj_data_with_name("test", COL.money_total))
    # print(detect_other_PJ(15))
    pass
