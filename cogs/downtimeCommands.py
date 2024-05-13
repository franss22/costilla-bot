from typing import Any, Self

import nextcord  # type: ignore
from nextcord.ext import commands  # type: ignore

import SheetControl as sh
from SheetControl import PJ_COL, gets_pj_data
from utils import CharacterNotFoundError
from varenv import getVar

CRI_GUILD_ID = int(getVar("GUILD_ID"))


class Downtime(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:
        self.client = client

    @nextcord.slash_command(
        description="Cambia el Downtime de tu personaje", guild_ids=[CRI_GUILD_ID]
    )
    @gets_pj_data
    async def dt(self: Self, interaction: nextcord.Interaction, amount: int) -> Any:
        user_id: int = interaction.user.id
        try:
            pj_row = sh.get_pj_row(user_id)
            pj_name = sh.get_pj_data(pj_row, PJ_COL.Name)
        except CharacterNotFoundError:
            return await interaction.send(
                "No se encontró un personaje con ID de discord correspondiente"
            )

        pj_dt: int = int(sh.get_pj_data(pj_row, PJ_COL.Downtime))

        if pj_dt + amount < 0:
            return await interaction.send(
                "No tienes suficiente downtime para esta transacción"
            )

        new_total = pj_dt + amount

        sh.update_pj_data_cell(pj_row, PJ_COL.Downtime, [[new_total]])

        return await interaction.send(
            (
                f"{pj_name} {'gana' if amount > 0 else 'gasta'} {abs(amount)} dias de downtime."
                f" Ahora tiene {new_total // 7} semanas y {new_total % 7} dias ({new_total} dias)"
            )
        )


def setup(client: commands.Bot) -> None:
    client.add_cog(Downtime(client))
