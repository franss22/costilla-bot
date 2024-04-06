import json
from functools import wraps

import gspread

from varenv import getVar

PJ_SHEET_ID = 1542430594

credentials = json.loads(getVar("GOOGLE"), strict=False)

gc = gspread.service_account_from_dict(credentials)

pj_sheet = gc.open("Dungeonmarch").get_worksheet_by_id(PJ_SHEET_ID)

PJ_DATA = None


def update_pj_data():
    global PJ_DATA
    PJ_DATA = pj_sheet.get_all_values(value_render_option="UNFORMATTED_VALUE")
    # print(PJ_DATA)


def gets_pj_data(func):
    @wraps(func)
    async def wrapped_func(*args, **kwargs):
        update_pj_data()
        await func(*args, **kwargs)

    return wrapped_func


class PJ_COL:
    Personaje = "A"
    discord_ID = "B"
    Jugadores = "C"
    Tier = "D"
    Niveles = "E"
    Raza = "F"
    Subraza = "G"
    Alignment = "H"
    Altura = "I"
    Peso = "J"
    Edad = "K"
    money_pp = "L"
    money_gp = "M"
    money_ep = "N"
    money_sp = "O"
    money_cp = "P"
    money_total = "Q"
    Renombre = "R"
    Deidad = "S"
    Cantidad = "T"
    Downtime = "U"
    DivineFavor = "V"
    Reputacion = "W"
    Crianza = "X"
    Expresion = "Y"
    Infamia = "Z"

    @classmethod
    def num(cls, col: str):
        return "ABCDEFGHIJKLMNOPQRSTUVWXYZ".index(col)

    @classmethod
    def has_value(cls, value):
        return value in cls.__dict__.values()


def whole_column(column: str) -> list[str]:
    c_index = PJ_COL.num(column)

    return [row[c_index] for row in PJ_DATA]


class CharacterNotFoundError(Exception):
    pass


def get_pj_row(discord_id: int) -> int:
    try:
        column = whole_column(PJ_COL.discord_ID)
        id_row = column.index(str(discord_id))
        # index del primer valor con [discord_id] de todos los ids (+1 por 0 indexed)
        return id_row
    except ValueError:
        raise CharacterNotFoundError(
            f"Character with discord ID '{discord_id}' was not found"
        )


def first_empty_PJ_row() -> int:
    column = whole_column(PJ_COL.discord_ID)
    # print(column)
    return column.index("")


def get_pj_data(pj_row: int, col: str) -> str:
    try:
        return PJ_DATA[pj_row][PJ_COL.num(col)]
    except IndexError:
        return None


def get_pj_full(row: int) -> list[str]:
    return PJ_DATA[row][: PJ_COL.num(PJ_COL.Infamia) + 1]


def get_pj_coins(row: int) -> list[float]:
    pp = PJ_COL.num(PJ_COL.money_pp)
    total = PJ_COL.num(PJ_COL.money_total)
    coins = PJ_DATA[row][
        pp : total + 1
    ]  # pj_sheet.get(f"{PJ_COL.Money_pp}{row}:{PJ_COL.Money_total}{row}", value_render_option = "UNFORMATTED_VALUE")[0]
    return [float(x) for x in coins]


def update_range_PJ(pj_row: int, start_column: str, end_column: str, values: list):
    pj_sheet.update(values, f"{start_column}{pj_row+1}:{end_column}{pj_row+1}")


def update_pj_data_cell(pj_row: int, col: str, value):
    pj_sheet.update(value, f"{col}{pj_row+1}")


def update_pj_coins(row: int, values):
    pj_sheet.update(values, f"{PJ_COL.money_pp}{row+1}:{PJ_COL.money_total}{row+1}")


if __name__ == "__main__":
    # print(COL.name)
    # print(get_pj_data_with_name("test", COL.money_total))
    # print(detect_other_PJ(15))
    pass
