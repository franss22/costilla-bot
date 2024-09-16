import json
from functools import wraps
from typing import Any, Callable, Iterable, Self
from icecream import ic
import gspread  # type: ignore

import utils
from utils import CharacterNotFoundError, Column
from varenv import getVar

PJ_SHEET_ID = 0
SUELDO_SHEET_ID = 1681819644

credentials = json.loads(getVar("GOOGLE"), strict=False)

gc = gspread.service_account_from_dict(credentials)

pj_sheet = gc.open("Megamarch").get_worksheet_by_id(PJ_SHEET_ID)
sueldo_sheet = gc.open("Megamarch").get_worksheet_by_id(SUELDO_SHEET_ID)

PJ_DATA: list[list[str]]


def update_pj_data() -> None:
    global PJ_DATA
    PJ_DATA = pj_sheet.get_all_values(value_render_option="UNFORMATTED_VALUE")


def gets_pj_data(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapped_func(*args: Any, **kwargs: Any) -> Any:
        update_pj_data()
        ic("Updated PC data.")
        await func(*args, **kwargs)

    return wrapped_func


class PJ_COL:
    Name: Column = Column("A")
    Discord_id: Column = Column("B")
    Player: Column = Column("C")
    Class: Column = Column("D")
    Arquetypes: Column = Column("E")
    Ancestry: Column = Column("F")
    Heritage: Column = Column("G")
    Downtime: Column = Column("H")
    Money_pp: Column = Column("I")
    Money_gp: Column = Column("J")
    Money_sp: Column = Column("K")
    Money_cp: Column = Column("L")
    Money_total: Column = Column("M")
    Languages: Column = Column("N")
    Religion: Column = Column("O")

    @classmethod
    def num(cls: Self, col: str) -> int:
        return utils.column_to_num(col)


def whole_column_pj(column: Column) -> list[str]:
    """
    Entrega una columna completa (con el header)
    """
    return [row[column.excel_index()] for row in PJ_DATA]


def get_pj_row(discord_id: int) -> int:
    try:
        column = whole_column_pj(PJ_COL.Discord_id)
        # ic(column)
        id_row = column.index(str(discord_id))
        # index del primer valor con [discord_id] de todos los ids (+1 por 0 indexed)
        return id_row
    except ValueError:
        raise CharacterNotFoundError(
            f"Error: No se encontró un personaje con ID de discord '{discord_id}'."
        )


def first_empty_PJ_row() -> int:
    column = whole_column_pj(PJ_COL.Discord_id)
    return column.index("") + 1


def get_pj_data(pj_row: int, col: Column) -> str:
    global PJ_DATA

    try:
        return PJ_DATA[pj_row][col.excel_index()]
    except IndexError:
        raise CharacterNotFoundError(
            "Error: No se encontró un personaje en la fila indicada."
        )


def get_pj_full(row: int) -> list[str]:
    global PJ_DATA

    return PJ_DATA[row]


def get_pj_coins(row: int) -> list[float]:
    global PJ_DATA

    pp = PJ_COL.Money_pp.excel_index()
    total = PJ_COL.Money_total.excel_index()
    # pj_sheet.get(f"{PJ_COL.Money_pp}{row}:{PJ_COL.Money_total}{row}", value_render_option = "UNFORMATTED_VALUE")[0]
    coins = PJ_DATA[row][pp: total + 1]  # noqa: E203
    return [float(x) for x in coins]


def update_range_PJ(values: Iterable[Iterable[Any]], pos: str) -> None:
    pj_sheet.update(values, pos)


def update_pj_data_cell(pj_row: int, col: str, value: Iterable[Iterable[Any]]) -> None:
    "row indexado a 0"
    pj_sheet.update(value, f"{col}{pj_row + 1}")


def update_pj_coins(row: int, values: Iterable[Iterable[Any]]) -> None:
    "row indexado a 0"
    pj_sheet.update(values, f"{PJ_COL.Money_pp}{row + 1}:{PJ_COL.Money_total}{row + 1}")


def get_sueldo(level: int) -> tuple[float, int]:
    data = sueldo_sheet.get_all_values(value_render_option="UNFORMATTED_VALUE")
    sueldo_gp = data[level][2]
    sueldo_dt = data[3][3]
    return (float(sueldo_gp), int(sueldo_dt))


LEVEL_GLOBAL = 4


def update_level_global(new_value: int = None) -> None:
    global LEVEL_GLOBAL
    if new_value is None:
        data = sueldo_sheet.get_all_values(value_render_option="UNFORMATTED_VALUE")
        LEVEL_GLOBAL = int(data[6][3])
    else:
        sueldo_sheet.update([[new_value]], "D7")
        LEVEL_GLOBAL = new_value


def get_level_global() -> int:
    global LEVEL_GLOBAL
    return LEVEL_GLOBAL
