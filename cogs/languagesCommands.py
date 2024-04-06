from typing import Any, Self

import nextcord  # type: ignore
from nextcord.ext import commands  # type: ignore

import SheetControl as sh
from PF2eData import LANGUAGES
from SheetControl import PJ_COL, gets_pj_data
from utils import default_user_option
from varenv import getVar

CRI_GUILD_ID = int(getVar("GUILD_ID"))


class Languages(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:
        self.client = client

    @nextcord.slash_command(
        description="Muestra la lista de tus lenguajes", guild_ids=[CRI_GUILD_ID]
    )
    @gets_pj_data
    async def languages(
        self: Self,
        interaction: nextcord.Interaction,
        target: nextcord.Member = default_user_option,
    ) -> Any:
        try:
            assert interaction.user is not None
        except AssertionError:
            return await interaction.send("Error: Null user")
        user_id: int = target.id if target is not None else interaction.user.id
        try:
            pj_row: int = sh.get_pj_row(user_id)
            pj_name: str = sh.get_pj_data(pj_row, PJ_COL.Name)
            pj_languages: str = sh.get_pj_data(pj_row, PJ_COL.Languages)
        except sh.CharacterNotFoundError:
            return await interaction.send(
                "No se encontró un personaje con ID de discord correspondiente"
            )
        if pj_languages is not None:
            languages = pj_languages.split(", ")
            language_list = "\n- ".join(languages)
            message = f"""**Lenguajes de {pj_name}:**
    - {language_list}"""
        else:
            message = f"{pj_name} no sabe ningún lenguaje."
        return await interaction.send(message)

    @nextcord.slash_command(
        description="Añade un lenguaje a la lista de tu PJ", guild_ids=[CRI_GUILD_ID]
    )
    @gets_pj_data
    async def addlanguage(
        self: Self,
        interaction: nextcord.Interaction,
        addedlanguage: str = nextcord.SlashOption(
            "lenguaje", "Lenguaje que quieres añadir a tu PJ", True, choices=LANGUAGES
        ),
        target: nextcord.Member = default_user_option,
    ) -> Any:
        try:
            assert interaction.user is not None
        except AssertionError:
            return await interaction.send("Error: Null user")
        user_id: int = target.id if target is not None else interaction.user.id
        try:
            pj_row: int = sh.get_pj_row(user_id)
            pj_name: str = sh.get_pj_data(pj_row, PJ_COL.Name)
            pj_languages: str = sh.get_pj_data(pj_row, PJ_COL.Languages)
        except sh.CharacterNotFoundError:
            return await interaction.send(
                "No se encontró un personaje con ID de discord correspondiente"
            )
        languages = [] if pj_languages in [None, ""] else pj_languages.split(", ")
        if addedlanguage not in languages:
            languages.append(addedlanguage)
            sh.update_pj_data_cell(pj_row, PJ_COL.Languages, [[", ".join(languages)]])
            return await interaction.send(
                f"{addedlanguage} ha sido añadido a la lista de {pj_name}."
            )
        else:
            return await interaction.send(
                f"{addedlanguage} ya está en la lista de {pj_name}."
            )


def setup(client: commands.Bot) -> None:
    client.add_cog(Languages(client))
