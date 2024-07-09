from typing import Any, Self

import dndice
import nextcord  # type: ignore
from nextcord.ext import commands  # type: ignore

from SheetControl import PJ_COL, get_level_global, gets_pj_data
import SheetControl as sh
from .moneyCommands import add_money_helper
import utils
from PF2eData import EARN_INCOME, SKILLS, LORELESS_SKILLS, PROF
from varenv import getVar
import random
from SheetControlSkills import get_pj_skill_bonus, gets_skill_data


CRI_GUILD_ID = int(getVar("GUILD_ID"))


class EarnIncome(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:
        self.client = client
    # =====================================================================================================================

    @nextcord.slash_command(
        description="Calcula las ganancias de Earn Income", guild_ids=[CRI_GUILD_ID]
    )
    async def earn_income(
        self: Self,
        interaction: nextcord.Interaction,
        taskLevel: int = nextcord.SlashOption(
            "task-level", "Nivel del trabajo", True, min_value=0, max_value=21
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
            min_value=7,
            default=7,
        ),
        checkBonus: int = nextcord.SlashOption(
            "check-bonus", "Bono al check utilizado", True
        ),
        dcChange: int = nextcord.SlashOption(
            "dc-adjustment", "Cambios al DC impuestos por el DM. +3 para habilidades que no sean Performance, Crafting o Lore.", False, default=0
        ),
    ) -> Any:
        await interaction.response.defer()
        dice = dndice.basic("1d20")
        check_value = dice + checkBonus
        DC = EARN_INCOME[taskLevel][0] + dcChange
        check_result = utils.check_results(DC, check_value, dice)
        prof_column = ["Trained", "Expert", "Master", "Legendary"].index(profLevel) + 1
        income: float

        income, final_dt_usage = calc_job_income_and_dt(taskLevel, downtimeUsed, check_result, prof_column)

        message = f"""Con un {check_value} ({dice}+{checkBonus}) vs DC {DC} , obtienes un {utils.result_name(check_result)}.
    Trabajas {final_dt_usage} dias y obtienes {income:.2f} gp al día, por un total de {income * final_dt_usage:.2f} gp.
    (Por ahora, debes updatearlos manualmente)
    """  # noqa: E501
        await interaction.followup.send(message)
    # =====================================================================================================================

    @nextcord.slash_command(
        description="Calcula las ganancias de Earn Income, usando tus bonos de forma automática. El DC se calcula solo.", guild_ids=[CRI_GUILD_ID]
    )
    @gets_skill_data
    @gets_pj_data
    async def earn_income_automatic(
        self: Self,
        interaction: nextcord.Interaction,
        taskLevel: int = nextcord.SlashOption(
            "task-level", "Nivel del trabajo", True, min_value=0, max_value=21
        ),
        skill: str = nextcord.SlashOption(
            "skill",
            "Skill utilizada. Trained Only.",
            True,
            choices=[sk_name for sk_name, _ in LORELESS_SKILLS] + ["Lore/Otro"],
        ),
        downtimeUsed: int = nextcord.SlashOption(
            "downtime-used",
            "Dias de downtime usados en trabajar",
            True,
            min_value=7,
            default=7,
        ),
        altSkill: str = nextcord.SlashOption(
            "alt-skill-profi",
            "Para utilizar otras skills. Usa additional-check-bonus. Pon el +3 al DC de ser necesario",
            False,
            choices=["Trained", "Expert", "Master", "Legendary"],
            default=None
        ),
        checkBonus: int = nextcord.SlashOption(
            "additional-check-bonus", "Bonos adicionales al check utilizado", False, default=0
        ),
        dcChange: int = nextcord.SlashOption(
            "dc-adjustment", "Cambios al DC impuestos por el DM.", False, default=0
        ),
        experiencedProf: bool = nextcord.SlashOption(
            "experienced-professional", "Aplicar Experienced Professional, solo para Lore.", False, default=False
        ),
    ) -> Any:
        await interaction.response.defer()
        user_id = interaction.user.id
        try:
            pj_row = sh.get_pj_row(user_id)
            pj_name = sh.get_pj_data(pj_row, PJ_COL.Name)
        except utils.CharacterNotFoundError:
            return await interaction.followup.send(
                "No se encontró un personaje con ID de discord correspondiente"
            )
        if skill == "Lore/Otro":
            if altSkill is None:
                return await interaction.followup.send("Debes seleccionar el nivel de proficiencia en alt-skill-profi si usas la skill 'Otro'.")
            if checkBonus == 0:
                return await interaction.followup.send("Debes especificar tu bono a la skill en additional-check-bonus si usas la skill 'Otro'.")
            bonus = 0
            profLevel = altSkill
            skill_msg = ""
        else:
            bonus, profLevel, skill_msg = get_pj_skill_bonus(user_id, skill)
        if bonus is None:
            return await interaction.followup.send("Debes setear tus skills con /set_all_skills para usar este comando.")
        if profLevel == PROF.Untrained:
            return await interaction.followup.send("No puedes hacer Earn Income con una skill Untrained")

        skill_msg += "" if checkBonus == 0 else f"[Additional: {checkBonus:+}]"

        pj_dt: int = int(sh.get_pj_data(pj_row, PJ_COL.Downtime))

        if pj_dt - downtimeUsed < 0:
            return await interaction.followup.send(
                "No tienes suficiente downtime para esta transacción"
            )

        dice = dndice.basic("1d20")
        check_value = dice + bonus + checkBonus
        DC = EARN_INCOME[taskLevel][0] + dcChange
        check_result = utils.check_results(DC, check_value, dice)
        double = False
        if experiencedProf:  # https://2e.aonprd.com/Feats.aspx?ID=5144
            if check_result == 1 and altSkill != "Trained":
                double = True
            if check_result == 0:
                check_result = 1

        prof_column = ["Trained", "Expert", "Master", "Legendary"].index(profLevel) + 1
        income, final_dt_usage = calc_job_income_and_dt(taskLevel, downtimeUsed, check_result, prof_column)
        income *= 2 if double else 1

        new_dt_total = pj_dt - final_dt_usage
        sh.update_pj_data_cell(pj_row, PJ_COL.Downtime, [[new_dt_total]])

        pp, gp, sp, cp, old_gp_total = sh.get_pj_coins(pj_row)
        pp, gp, sp, cp, new_gp_total = add_money_helper(income * final_dt_usage, pj_row)

        crit_fail_message = "" if check_result != 0 else "\nDebido a tu crit failure, tu proximo trabajo tiene un -1 al nivel."

        message = f"""## {pj_name}: Earn income de {skill}
Con un {check_value} ({dice}{(bonus + checkBonus):+} {skill_msg}) vs DC {DC}, obtienes un {utils.result_name(check_result)}.
    Trabajas {final_dt_usage} dias y obtienes {income:.2f} gp al día, por un total de {income * final_dt_usage:.2f} gp.
    Cambio de DT: {pj_dt} -> {new_dt_total}
    Cambio de Dinero: {old_gp_total} -> {new_gp_total}{crit_fail_message}
    """  # noqa: E501
        await interaction.followup.send(message)
    # =====================================================================================================================

    @nextcord.slash_command(
        description="Genera trabajos especiales.", guild_ids=[CRI_GUILD_ID]
    )
    async def gen_jobs(
        self: Self,
        interaction: nextcord.Interaction,
        taskLevel: int = nextcord.SlashOption(
            "task-level", "Nivel base de los trabajos", False, min_value=0, max_value=21, default=None
        ),
        tasksAmt: int = nextcord.SlashOption(
            "tasks-amount", "Cantidad de trabajos", False, min_value=0, max_value=10, default=4
        ),
    ) -> Any:
        await interaction.response.defer()
        taskLevel = taskLevel if taskLevel is not None else get_level_global()
        message = ("# Trabajos mensuales\n"
                   "Todos los trabajos duran 14 dias y se pueden hacer 1 sola vez por PJ.\n"
                   "Como recordatorio, todos los trabajos con skills que no sean Crafting, Performance o Lore tienen un +3 al DC\n\n")
        chosen_skills = random.sample(LORELESS_SKILLS, tasksAmt)
        job_messages = [job_message(sk, taskLevel) for (sk, _ab) in chosen_skills]
        message += "\n".join(job_messages)

        await interaction.followup.send(message)


def job_message(skill: str, base_lvl: int) -> str:
    """"""
    lvl = min(21, base_lvl + random.choices([0, 1, 2], [0.6, 0.3, 0.1])[0])
    if skill_is_standard(skill):
        dc_adjustment = -random.choice([0, 1, 2])
        dc_message = f"{dc_adjustment:+} al DC"
        non_standard_penalty = 0

    else:
        dc_adjustment = -random.choice([1, 2, 3])
        dc_message = f"{dc_adjustment:+} al DC (+3 por skill no estandar)"
        non_standard_penalty = 3

    dc = EARN_INCOME[lvl][0] + dc_adjustment + non_standard_penalty

    return (f"### Trabajo de **{skill}**:\n"
            f"Trabajo de Nivel {lvl}. {dc_message} (DC total {dc})"
            f"```/earn_income_automatic task-level:{lvl} skill:{skill} downtime-used:14 dc-adjustment:{dc_adjustment + non_standard_penalty}```")


def calc_job_income_and_dt(taskLevel: int, downtimeUsed: int, check_result: int, prof_column: int) -> tuple[float, int]:
    if check_result == 0:
        # crit failure
        income = 0
        final_dt_usage = 7
    if check_result == 1:
        # failure
        income = EARN_INCOME[taskLevel][1][0]
        final_dt_usage = 7
    if check_result == 2:
        # success
        income = EARN_INCOME[taskLevel][1][prof_column]
        final_dt_usage = downtimeUsed
    if check_result == 3:
        # Critical success
        income = EARN_INCOME[taskLevel + 1][1][prof_column]
        final_dt_usage = downtimeUsed
    return income, final_dt_usage


def skill_is_standard(skill: str) -> str:
    return skill == "Performance" or skill == "Crafting" or skill.startswith("Lore")


def setup(client: commands.Bot) -> None:
    client.add_cog(EarnIncome(client))
