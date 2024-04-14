import json
from functools import wraps
from typing import Any, Callable, Tuple

import gspread  # type: ignore

import utils
from PF2eData import ABILITIES
from utils import Column
from varenv import getVar

SKILLS_SHEET_ID = 738258837
ABILITIES_SHEET_ID = 41455486


credentials = json.loads(getVar("GOOGLE"), strict=False)

gc = gspread.service_account_from_dict(credentials)

skill_sheet = gc.open("Megamarch").get_worksheet_by_id(SKILLS_SHEET_ID)
ability_sheet = gc.open("Megamarch").get_worksheet_by_id(ABILITIES_SHEET_ID)

SKILL_DATA: list[list[str]]
ABILITY_DATA: list[list[str]]


def _update_skill_data() -> None:
    "Actualiza los singletons SKILL_DATA, ABILITY_DATA"
    global SKILL_DATA, ABILITY_DATA
    SKILL_DATA = skill_sheet.get_all_values(value_render_option="UNFORMATTED_VALUE")
    ABILITY_DATA = ability_sheet.get_all_values(value_render_option="UNFORMATTED_VALUE")


def gets_skill_data(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapped_func(*args: Any, **kwargs: Any) -> Any:
        _update_skill_data()
        print("Updated skill/ability data.")
        await func(*args, **kwargs)

    return wrapped_func


class SKILL_COL:
    Name: Column = Column("A")
    Discord_id: Column = Column("B")
    Skill: Column = Column("C")
    Proficiency: Column = Column("D")
    ExtraBonuses: Column = Column("E")
    ExtraDescription: Column = Column("F")


class ABILITY_COL:
    Name: Column = Column("A")
    Discord_id: Column = Column("B")
    Str: Column = Column("C")
    Dex: Column = Column("D")
    Con: Column = Column("E")
    Int: Column = Column("F")
    Wis: Column = Column("G")
    Cha: Column = Column("H")


def _column(DATA: list[list[str]], column: utils.Column) -> list[str]:
    return [row[column.excel_index()] for row in DATA]


def _first_empty_row(DATA: list[list[str]], col: utils.Column) -> int:
    """
    Entrega el index (indexado a 1) de la primera fila vacía de un excel
    """
    col: list[str] = _column(DATA, col)
    return len(col) + 1


def _get_id_row(DATA: list[list[str]], col: Column, id: int) -> int | None:
    """Retorna la row (index 0) de la primera fila de DATA con el id indicado."""
    id_column: list[str] = _column(DATA, col)
    print("id int:", id)
    print("id str:", str(id))
    print("column:", id_column)

    try:
        return id_column.index(str(id))
    except ValueError:
        return None


def first_empty_ability_row() -> int:
    """
    Entrega el index (indexado a 1) de la primera fila vacía de las habilidades
    """
    global ABILITY_DATA
    return _first_empty_row(ABILITY_DATA, ABILITY_COL.Discord_id)


def first_empty_skill_row() -> int:
    """
    Entrega el index (indexado a 1) de la primera fila vacía de las skills
    """
    global SKILL_DATA
    return _first_empty_row(SKILL_DATA, SKILL_COL.Discord_id)


def _get_pj_skills_raw(id: int) -> list[Tuple[int, list[str]]]:
    """
    Returna una lista de tuplas con la row (index 1) y los raw datos de todas las filas de skill con el id indicado
    """
    global SKILL_DATA
    data: list[Tuple[int, list[str]]] = []
    for index_i0, row in enumerate(SKILL_DATA):
        if row[SKILL_COL.Discord_id.excel_index()] == str(id):
            data.append((index_i0 + 1, row))
    return data


def get_pj_skills(discord_id: int) -> Tuple[str, dict[str, dict[str, str | int]]]:
    """
    Retorna el nombre del PJ y un diccionario con las sills del pj tal que:
    {skill_name: {prof_level: str, extra_bonus: int, extra_descripcion: str, row (index 1): int}}
    Las skills que no estén definidas no van en el dict (dict vacío en caso de no tener skills definidas)
    Nombre is none si el dict es vacío.
    """
    skills_raw: list[Tuple[int, list[str]]] = _get_pj_skills_raw(discord_id)
    if len(skills_raw) == 0:
        return (None, {})

    name = skills_raw[0][1][SKILL_COL.Name.excel_index()]
    skills: dict[str, dict[str, str | int]] = {}
    for index_i1, row in skills_raw:
        skill_name = row[SKILL_COL.Skill.excel_index()]
        prof_level = row[SKILL_COL.Proficiency.excel_index()]
        extra_bonus = row[SKILL_COL.ExtraBonuses.excel_index()]
        extra_descripcion = row[SKILL_COL.ExtraDescription.excel_index()]
        row = index_i1

        skills[skill_name] = {
            "prof_level": prof_level,
            "extra_bonus": extra_bonus,
            "extra_descripcion": extra_descripcion,
            "row": row,
        }
    return (name, skills)


def get_pj_abilities(
    discord_id: int,
) -> Tuple[str | None, int | None, dict[str, int] | None]:
    """
    Retorna el nombre del PJ, la row (index 1) y un diccionario con los ability modifiers del pj tal que:
    {ability (tipo Ability): int}
    None * 3 si el PJ no ha definido sus mods
    """
    global ABILITY_DATA
    row_i0: int | None = _get_id_row(ABILITY_DATA, ABILITY_COL.Discord_id, discord_id)
    if row_i0 is None:
        return (None, None, None)

    raw_data = ABILITY_DATA[row_i0]
    name = raw_data[ABILITY_COL.Name.excel_index()]
    stats = {
        ABILITIES.Str: int(raw_data[ABILITY_COL.Str.excel_index()]),
        ABILITIES.Dex: int(raw_data[ABILITY_COL.Dex.excel_index()]),
        ABILITIES.Con: int(raw_data[ABILITY_COL.Con.excel_index()]),
        ABILITIES.Int: int(raw_data[ABILITY_COL.Int.excel_index()]),
        ABILITIES.Wis: int(raw_data[ABILITY_COL.Wis.excel_index()]),
        ABILITIES.Cha: int(raw_data[ABILITY_COL.Cha.excel_index()]),
    }
    return (name, row_i0 + 1, stats)


def update_skill_row(row_index: int, data: Tuple[str, str, int, int, str]) -> None:
    """
    Actualiza o crea una nueva row de skill.
    row_index es indexado a 1
    data debe ser tal que: [nombre_pj, discord_id, skill_name, prof_level, extra_bonuses, extra_bonuses_description]
    """
    skill_sheet.update([data], f"A{row_index}:F{row_index}")


def multi_update_skill_row(
    rows_and_data: list[Tuple[int, Tuple[str, str, int, int, str]]]
) -> None:
    """
    Actualiza o crea múltiples rows de skill.
    row_index es indexado a 1
    data debe ser tal que: [nombre_pj, discord_id, skill_name, prof_level, extra_bonuses, extra_bonuses_description]
    """
    send_batch = []
    for row_index, data in rows_and_data:
        send_batch.append({"range": f"A{row_index}:F{row_index}", "values": [data]})

    skill_sheet.batch_update(send_batch)


def update_ability_row(
    row_index: int, data: Tuple[str, str, int, int, int, int, int, int]
) -> None:
    """
    Actualiza o crea una nueva row de habilidades.
    row_index es indexado a 1
    data debe ser tal que: [nombre_pj, discord_id, STR, DEX, CON, INT, WIS, CHA]
    """
    ability_sheet.update([data], f"A{row_index}:H{row_index}")


def get_all_existing_lore_subnames(id: int | None = None) -> list[str]:
    global SKILL_DATA

    data = SKILL_DATA if id is None else [row for index, row in _get_pj_skills_raw(id)]
    print("id", id)
    print("data", data)
    skill_names = _column(data, SKILL_COL.Skill)
    print("skill_names column", skill_names)

    # Se asume que todos los lores están en formato "Lore (subname)"
    lore_subnames = [skill[6:-1] for skill in skill_names if skill.startswith("Lore")]
    return lore_subnames
