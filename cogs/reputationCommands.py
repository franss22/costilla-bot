from typing import Any, Self

import nextcord  # type: ignore
from nextcord.ext import commands  # type: ignore

import SheetControl as shpj
import SheetControlReputation as shr
from SheetControl import PJ_COL, gets_pj_data
from SheetControlReputation import REP_COL, gets_rep_data
from utils import CharacterNotFoundError, default_user_option
from varenv import getVar

CRI_GUILD_ID = int(getVar("GUILD_ID"))


class Reputation(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:
        self.client = client

    @nextcord.slash_command(
        description="Revisa tu reputación", guild_ids=[CRI_GUILD_ID]
    )
    @gets_rep_data
    async def reputation(
        self: Self,
        interaction: nextcord.Interaction,
        target: nextcord.Member = default_user_option,
    ) -> Any:
        try:
            assert interaction.user is not None
        except AssertionError:
            return await interaction.send("Error: Null user")
        user_id: int = target.id if target is not None else interaction.user.id
        reps: list[tuple[str, str, str, str, int]] = shr.get_pj_reps(user_id)
        message = ""
        print(reps)
        if len(reps) > 0:
            message = f"# Reputación de {reps[0][REP_COL.Name.excel_index()]}"
            reps.sort(reverse=True, key=lambda r: r[REP_COL.Reputation.excel_index()])
            print(reps)

            for rep in reps:
                row_pj_name, row_discord_id, row_faction, row_reputation, row_index = (
                    rep
                )
                message += f"\n- {row_faction}: {row_reputation}"
        else:
            message = "Tu personaje no tiene reputación con ningún NPC ni facción."
        return await interaction.send(message)

    @nextcord.slash_command(
        description="Actualiza tu reputación con una facción o NPC",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_rep_data
    @gets_pj_data
    async def updatereputation(
        self: Self,
        interaction: nextcord.Interaction,
        amount: int,
        faction: str,
        target: nextcord.Member = default_user_option,
    ) -> Any:

        user_id: int = target.id if target is not None else interaction.user.id

        reps: list[tuple[str, str, str, str, int]] = shr.get_pj_reps(user_id)
        rep_row: list[tuple[str, str, str, str, int]] = [
            row for row in reps if row[REP_COL.Faction.excel_index()] == faction
        ]

        if len(rep_row):
            # Add reptuation
            row_pj_name, row_discord_id, row_faction, row_reputation, row_index = (
                rep_row[0]
            )
            new_rep = int(row_reputation) + amount
            new_row = [row_pj_name, row_discord_id, row_faction, new_rep]
            shr.update_rep_row(row_index, new_row)
            await interaction.send(
                (
                    f"Actualizada la reputación de {row_pj_name} con"
                    f" {faction}: {row_reputation} -> {new_rep}"
                )
            )

        else:
            # Create new line
            try:
                pj_row = shpj.get_pj_row(user_id)
                pj_name = shpj.get_pj_data(pj_row, PJ_COL.Name)
            except CharacterNotFoundError:
                return await interaction.send(
                    "No se encontró un personaje con ID de discord correspondiente"
                )
            row_index = shr.first_empty_rep_row()
            new_row = [pj_name, str(user_id), faction, amount]
            print(new_row)
            shr.update_rep_row(row_index, new_row)
            await interaction.send(
                f"Creada la reputación de {pj_name} con {faction}: {amount}"
            )

    @updatereputation.on_autocomplete("faction")
    async def autocomplete_faction(
        interaction: nextcord.Interaction, faction: str
    ) -> Any:
        filtered_ancestries = []
        if faction:
            if len(faction) == 1:
                shr.update_rep_data()
                print("Updated rep data once")
            filtered_ancestries = [
                a
                for a in shr.get_all_existing_factions()
                if a.lower().startswith(faction.lower())
            ]
        await interaction.response.send_autocomplete(filtered_ancestries)


def setup(client: commands.Bot) -> None:
    client.add_cog(Reputation(client))
