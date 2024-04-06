from typing import Any, Self

import dndice
import nextcord  # type: ignore
from nextcord.ext import commands  # type: ignore

import utils
from PF2eData import EARN_INCOME
from varenv import getVar

CRI_GUILD_ID = int(getVar("GUILD_ID"))


class EarnIncome(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:
        self.client = client

    @nextcord.slash_command(
        description="Calcula las ganancias de Earn Income", guild_ids=[CRI_GUILD_ID]
    )
    async def earnincome(
        self: Self,
        interaction: nextcord.Interaction,
        taskLevel: int = nextcord.SlashOption(
            "task-level", "Nivel del trabajo", True, min_value=0, max_value=20
        ),
        profLevel: str = nextcord.SlashOption(
            "proficiency-level",
            "Nivel de proficiencia de la skill usada",
            True,
            choices=["Trained", "Expert", "Master", "Legendary"],
        ),
        downtimeUsed: int = nextcord.SlashOption(
            "downtime-used",
            "Dias de downtime usados en trabajar",
            True,
            min_value=1,
            default=1,
        ),
        checkBonus: int = nextcord.SlashOption(
            "check-bonus", "Bono al check utilizado", True
        ),
        dcChange: int = nextcord.SlashOption(
            "dc-adjustment", "Cambios al DC impuestos por el DM", False, default=0
        ),
    ) -> Any:
        dice = dndice.basic("1d20")
        check_value = dice + checkBonus
        DC = EARN_INCOME[taskLevel][0] + dcChange
        check_result = utils.check_results(DC, check_value, dice)
        prof_column = ["Trained", "Expert", "Master", "Legendary"].index(profLevel) + 1
        income: float

        if check_result == 0:
            # crit failure
            income = 0
            final_dt_usage = 1
        if check_result == 1:
            # failure
            income = EARN_INCOME[taskLevel][1][0]
            final_dt_usage = min(7, downtimeUsed)
        if check_result == 2:
            # success
            income = EARN_INCOME[taskLevel][1][prof_column]
            final_dt_usage = downtimeUsed
        if check_result == 3:
            # Critical success
            income = EARN_INCOME[taskLevel + 1][1][prof_column]
            final_dt_usage = downtimeUsed

        message = f"""Con un {check_value} ({dice}+{checkBonus}) vs DC {DC} , obtienes un {utils.result_name(check_result)}.
    Trabajas {final_dt_usage} dias y obtienes {income:.2f} gp al día, por un total de {income * final_dt_usage:.2f} gp.
    (Por ahora, debes updatearlos manualmente)
    """  # noqa: E501
        await interaction.send(message)


def setup(client: commands.Bot) -> None:
    client.add_cog(EarnIncome(client))
