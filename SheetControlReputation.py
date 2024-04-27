import json
from functools import wraps
from typing import Any, Callable, Iterable, Self
from icecream import ic

import gspread  # type: ignore

import utils
from utils import Column
from varenv import getVar

REPUTATION_SHEET_ID = 37818595

credentials = json.loads(getVar("GOOGLE"), strict=False)

gc = gspread.service_account_from_dict(credentials)

rep_sheet = gc.open("Megamarch").get_worksheet_by_id(REPUTATION_SHEET_ID)


REP_DATA: list[list[str]]


def update_reputation_data() -> None:
    global REP_DATA
    REP_DATA = rep_sheet.get_all_values(value_render_option="UNFORMATTED_VALUE")


def gets_reputation_data(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapped_func(*args: Any, **kwargs: Any) -> Any:
        update_reputation_data()
        ic("Updated reputation data.")
        await func(*args, **kwargs)

    return wrapped_func


class REP_COL:
    Name: Column = Column("A")
    Discord_id: Column = Column("B")
    Faction: Column = Column("C")
    Reputation: Column = Column("D")

    @classmethod
    def num(cls: Self, col: str) -> int:
        return utils.column_to_num(col)


def first_empty_rep_row() -> int:
    """
    Entrega el index (indexado a 1) de la primera fila vacía de las reputaciones
    """
    column: list[str] = whole_column_rep(REP_COL.Discord_id)
    return len(column) + 2


def whole_column_rep(column: utils.Column) -> list[str]:
    """
    Entrega una columna completa (sin el header)
    """
    return [row[column.excel_index()] for row in REP_DATA][1:]


def get_pj_reps(discord_id: int) -> list[tuple[str, str, str, str, int]]:
    global REP_DATA

    discord_id_str: str = str(discord_id)
    reps: list[tuple[str, str, str, str, int]] = [
        (row[0], row[1], row[2], row[3], REP_DATA.index(row) + 1)
        for row in REP_DATA
        if row[REP_COL.Discord_id.excel_index()] == discord_id_str
    ]
    return reps


def update_rep_row(row_index: int, data: Iterable[Any]) -> None:
    rep_sheet.update([data], f"A{row_index}:D{row_index}")


def get_all_existing_factions() -> set[str]:
    return set(whole_column_rep(REP_COL.Faction))
