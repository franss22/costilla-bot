import logging
from typing import Any

import nextcord  # type: ignore
from nextcord.ext import commands  # type: ignore

import SheetControl as sh
import utils
from cogs import (
    downtimeCommands,
    earn_incomeCommands,
    languagesCommands,
    moneyCommands,
    registerCommands,
    reputationCommands,
    skillCommands,
)
from SheetControl import PJ_COL, gets_pj_data
from utils import CharacterNotFoundError, default_user_option
from varenv import getVar

CRI_GUILD_ID = int(getVar("GUILD_ID"))
PANCHO_ID = getVar("PANCHO_ID")
BOT_TOKEN = getVar("TOKEN")

logging.basicConfig(level=logging.INFO)
bot = commands.Bot()


@bot.event
async def on_ready() -> None:
    print(f"We have logged in as {bot.user}")


@bot.slash_command(
    description="Entrega la info de tu personaje", guild_ids=[CRI_GUILD_ID]
)
@gets_pj_data
async def status(
    interaction: nextcord.Interaction, user: nextcord.Member = default_user_option
) -> Any:
    user_id: int = interaction.user.id if user is None else user.id
    try:
        pj_row = sh.get_pj_row(user_id)
    except CharacterNotFoundError:
        return await interaction.send(
            "No se encontró un personaje con ID de discord correspondiente"
        )
    data = sh.get_pj_full(pj_row)
    (
        Name,
        Id,
        Player,
        Class,
        Arquetypes,
        Ancestry,
        Heritage,
        Dt,
        pp,
        gp,
        sp,
        cp,
        total,
        languages,
        religion,
    ) = data
    Dt_int: int = int(Dt)
    message = f"""# Status de {Name}
- Jugador: {Player}
- Clase: {Class}{", " if Arquetypes else ""}{Arquetypes}
- Ascendencia: {Ancestry}, {Heritage}
- Dinero: {pp}pp, {gp}gp, {sp}sp, {cp}cp, **Total: {total:.2f}gp**
- Downtime: {Dt_int // 7} semanas y {Dt % 7} dias ({Dt_int} dias)
"""
    return await interaction.send(message)


@bot.slash_command(
    description="Gana el downtime y dinero esperado de terminar una misión",
    guild_ids=[CRI_GUILD_ID],
)
@gets_pj_data
async def salary(
    interaction: nextcord.Interaction,
    overwrite_level: int = None,
    target: nextcord.Member = default_user_option,
) -> Any:
    try:
        assert interaction.user is not None
    except AssertionError:
        return await interaction.send("Error: Null user")
    user_id: int = target.id if target is not None else interaction.user.id
    try:
        pj_row = sh.get_pj_row(user_id)
        pj_name = sh.get_pj_data(pj_row, PJ_COL.Name)
    except CharacterNotFoundError:
        return await interaction.send(
            "No se encontró un personaje con ID de discord correspondiente"
        )
    overwrite_level = (
        sh.get_level_global() if overwrite_level is None else overwrite_level
    )

    sueldo_gp, sueldo_dt = sh.get_sueldo(overwrite_level)

    pj_coins = sh.get_pj_coins(pj_row)
    pp, gp, sp, cp, total = pj_coins

    new_total_gp = total + sueldo_gp
    new_coins = utils.gp_to_coin_list(new_total_gp)
    pp, gp, sp, cp = new_coins

    pj_dt = int(sh.get_pj_data(pj_row, PJ_COL.Downtime))
    new_total_dt = pj_dt + sueldo_dt

    sh.update_pj_data_cell(pj_row, PJ_COL.Downtime, [[new_total_dt, pp, gp, sp, cp]])

    return await interaction.send(
        (
            f"{pj_name}: Misión nivel {overwrite_level} completada!"
            f"\n Se te suma el sueldo de la misión:"
            f" {sueldo_gp: .2f}gp (ahora tienes {new_total_gp: .2f}gp)"
            f"\n Se te suman {sueldo_dt} días de dt "
            f"(ahora tienes {new_total_dt} dias de dt)"
        )
    )


registerCommands.setup(bot)
reputationCommands.setup(bot)
downtimeCommands.setup(bot)
moneyCommands.setup(bot)
earn_incomeCommands.setup(bot)
languagesCommands.setup(bot)
skillCommands.setup(bot)

sh.update_level_global()


@bot.slash_command(
    description="Cambia el nivel de todos los personajes", guild_ids=[CRI_GUILD_ID]
)
async def update_global_level(
    interaction: nextcord.Interaction, level: int = None
) -> Any:
    sh.update_level_global(level)
    return await interaction.send("Nivel global actualizado")


bot.run(BOT_TOKEN)
