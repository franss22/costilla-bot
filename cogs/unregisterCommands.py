"""
Eliminar un PJ del excel, ya sea completamente, o moviendolo al cementerio.

Pasos:
- Verificar que el personaje exista.
    - Si no existe, enviar un mensaje de error.
- Por default, copiar el personaje a la hoja cementerio. Especificando en el input:
    - Turno de Muerte
    - Narrador de Muerte
    - Causa de muerte
    - Nivel al morir (sacar del nivel global)
- Eliminar:
    - Reputación
    - Skills
    - Ability Mods
    - PJ
"""

from typing import Any, Callable, Self

import nextcord  # type: ignore
from nextcord.ext import commands

import SheetControl as sh
from SheetControl import PJ_COL, gets_pj_data
from utils import CharacterNotFoundError
from varenv import getVar

CRI_GUILD_ID = int(getVar("GUILD_ID"))


class Unregister(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:
        self.client = client
