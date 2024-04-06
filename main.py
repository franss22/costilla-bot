import logging
from typing import Any

import nextcord
from nextcord.ext import commands

import SheetControl as sh
import utils
from SheetControl import PJ_COL, gets_pj_data
from varenv import getVar

logging.basicConfig(level=logging.INFO)

CRI_GUILD_ID = int(getVar("GUILD_ID"))
PANCHO_ID = getVar("PANCHO_ID")
BOT_TOKEN = getVar("TOKEN")

bot = commands.Bot()


@bot.event
async def on_ready() -> None:
    print(f"We have logged in as {bot.user}")


@bot.slash_command(
    description="Registra un nuevo personaje de Dungeonmarch.", guild_ids=[CRI_GUILD_ID]
)
@gets_pj_data
async def registrar(
    interaction: nextcord.Interaction, nombre_pj: str, nombre_jugador: str
) -> Any:
    # Conseguir el ID del usuario
    user_id: int = interaction.user.id
    print(user_id)
    # Revisar que no tenga otro PJ
    already_has_character = True
    try:
        pj_row = sh.get_pj_row(user_id)
    except sh.CharacterNotFoundError:
        already_has_character = False
    if already_has_character:
        return await interaction.send(
            f"Ya tienes un personaje en la fila {pj_row}, muevelo al cementario para registrar uno nuevo."
        )

    values = [nombre_pj, str(user_id), nombre_jugador]
    pj_row = sh.first_empty_PJ_row()
    sh.update_range_PJ(pj_row, PJ_COL.Personaje, PJ_COL.Jugadores, [values])
    await interaction.send(f"Registrado {nombre_pj} en la fila {pj_row+1}")


@bot.slash_command(
    description="Entrega la info de tu personaje", guild_ids=[CRI_GUILD_ID]
)
@gets_pj_data
async def resumen(
    interaction: nextcord.Interaction,
    full_data: bool = False,
    user: nextcord.Member = None,
) -> Any:
    user_id: int = interaction.user.id if user is None else user.id
    try:
        pj_row = sh.get_pj_row(user_id)
    except sh.CharacterNotFoundError:
        return await interaction.send(
            "No se encontró un personaje con ID de discord correspondiente"
        )
    data = sh.get_pj_full(pj_row)
    print(data)
    (
        Name,
        Id,
        Player,
        Tier,
        Levels,
        Race,
        Subrace,
        Alignment,
        height,
        weight,
        age,
        pp,
        gp,
        ep,
        sp,
        cp,
        total,
        renombre,
        deidad,
        piedad,
        downtime,
        divinefavor,
        reputacion,
        crianza,
        expresion,
        infamia,
    ) = data
    Dt = int(downtime)
    message = f"""# Status de {Name}, Tier {Tier}
- Jugador: {Player}
- Niveles: {Levels}
- Raza: {Race}, {Subrace}
- Deidad: {deidad}, {piedad} de piedad
- Renombre: {renombre}
- Dinero: {pp}pp, {gp}gp, {ep}ep, {sp}sp, {cp}cp, **Total: {total}gp**
- Downtime: {Dt//1} semanas y {Dt*10//10} dias
"""
    if full_data:
        message += f"""
- Favor divino: {divinefavor}
- Reputación: {reputacion}
- Crianza: {crianza}
- Expresión: {expresion}
- Infamia: {infamia}
"""
    return await interaction.send(message)


@bot.slash_command(
    description="Cambia el Downtime de tu personaje", guild_ids=[CRI_GUILD_ID]
)
@gets_pj_data
async def downtime(
    interaction: nextcord.Interaction, amount: float, user: nextcord.Member = None
) -> Any:
    user_id: int = interaction.user.id if user is None else user.id
    try:
        pj_row = sh.get_pj_row(user_id)
        pj_name = sh.get_pj_data(pj_row, PJ_COL.Personaje)
    except sh.CharacterNotFoundError:
        return await interaction.send(
            "No se encontró un personaje con ID de discord correspondiente"
        )

    pj_dt = float(sh.get_pj_data(pj_row, PJ_COL.Downtime))

    if pj_dt + amount < 0:
        return await interaction.send(
            "No tienes suficiente downtime para esta transacción"
        )

    new_total = min(pj_dt + amount, 3)

    sh.update_pj_data_cell(pj_row, PJ_COL.Downtime, [[new_total]])

    return await interaction.send(
        f"{pj_name} {'gana' if amount>0 else 'gasta'} {amount:.2f} semanas de downtime. Ahora tiene {new_total:.2f}"
    )


@bot.slash_command(
    description="Resta dinero de tu cuenta. Puedes transferir a otra persona.",
    guild_ids=[CRI_GUILD_ID],
)
@gets_pj_data
async def pagar(
    interaction: nextcord.Interaction,
    amount_str: float,
    transfertarget: nextcord.Member = None,
) -> Any:
    try:
        amount: float = utils.parse_float_arg(amount_str)
    except ValueError as e:
        return await interaction.send(f"Error: {e}")
    user_id: int = interaction.user.id
    target_id: int = transfertarget.id if transfertarget is not None else None
    try:
        pj_row = sh.get_pj_row(user_id)
        pj_name = sh.get_pj_data(pj_row, PJ_COL.Personaje)
        target_pj_row = sh.get_pj_row(target_id) if transfertarget is not None else None
        target_pj_name = (
            sh.get_pj_data(target_pj_row, PJ_COL.Personaje)
            if transfertarget is not None
            else None
        )
    except sh.CharacterNotFoundError:
        return await interaction.send(
            "No se encontró un personaje con ID de discord correspondiente"
        )
    if amount < 0:
        return await interaction.send("Debes pagar una cantidad positiva de dinero")

    pj_coins = sh.get_pj_coins(pj_row)
    pp, gp, ep, sp, cp, total = pj_coins

    if total - amount < 0:
        return await interaction.send(
            "No tienes suficiente dinero para esta transacción"
        )

    paid_coins = utils.pay_priority(pj_coins, amount)
    ppp, pgp, pep, psp, pcp = paid_coins
    new_coins = [pj_coins[x] + paid_coins[x] for x in range(5)]

    new_total = total - amount

    pp, gp, ep, sp, cp = new_coins
    sh.update_pj_coins(pj_row, [new_coins])

    if transfertarget is not None:
        target_coins = sh.get_pj_coins(target_pj_row)
        pp, gp, ep, sp, cp, total = target_coins
        new_total_target = total + amount
        new_coins = [target_coins[x] - paid_coins[x] for x in range(5)]
        sh.update_pj_coins(target_pj_row, [new_coins])
        return await interaction.send(
            (
                f"{pj_name} le transfiere {amount}gp ({ppp}pp, {pgp}gp, {pep}ep, {psp}sp, {pcp}cp)"
                f" a {target_pj_name}. \n{pj_name} queda con {new_total:.2f}gp,"
                f" y {target_pj_name} queda con {new_total_target:.2f}gp."
            )
        )
    return await interaction.send(
        f"{pj_name} paga {amount}gp ({ppp}pp, {pgp}gp, {pep}ep, {psp}sp, {pcp}cp)."
        f"\nAhora tiene {pp}pp, {gp}gp, {ep}ep, {sp}sp, {cp}cp,"
        f" **Total: {new_total:.2f}gp**"
    )


@bot.slash_command(description="Suma dinero a tu cuenta.", guild_ids=[CRI_GUILD_ID])
@gets_pj_data
async def añadirdinero(
    interaction: nextcord.Interaction, amount_str: float, user: nextcord.Member = None
) -> Any:
    try:
        amount: float = utils.parse_float_arg(amount_str)
    except ValueError as e:
        return await interaction.send(f"Error: {e}")
    user_id: int = interaction.user.id if user is None else user.id

    try:
        pj_row = sh.get_pj_row(user_id)
        pj_name = sh.get_pj_data(pj_row, PJ_COL.Personaje)
    except sh.CharacterNotFoundError:
        return await interaction.send(
            "No se encontró un personaje con ID de discord correspondiente"
        )
    if amount < 0:
        return await interaction.send("Debes ganar una cantidad positiva de dinero")

    pj_coins = sh.get_pj_coins(pj_row)
    pp, gp, ep, sp, cp, total = pj_coins
    added_coins = utils.gp_to_coin_list(amount)
    new_total = total + amount
    new_coins = [pj_coins[x] + added_coins[x] for x in range(5)]
    pp, gp, ep, sp, cp = new_coins
    sh.update_pj_coins(pj_row, [new_coins])

    return await interaction.send(
        f"{pj_name} obtiene {amount}gp."
        f" Ahora tiene {pp}pp, {gp}gp, {ep}ep, {sp}sp, {cp}cp,"
        f" **Total: {new_total:.2f}gp**"
    )


def simple_value_update_command(value_row: str, value_name: str) -> Any:
    async def command(
        interaction: nextcord.Interaction, amount: int = 0, user: nextcord.Member = None
    ) -> Any:
        user_id: int = interaction.user.id if user is None else user.id

        try:
            pj_row = sh.get_pj_row(user_id)
            pj_name = sh.get_pj_data(pj_row, PJ_COL.Personaje)
        except sh.CharacterNotFoundError:
            return await interaction.send(
                "No se encontró un personaje con ID de discord correspondiente"
            )

        pj_value = sh.get_pj_data(pj_row, value_row)
        pj_value = 0 if pj_value == "" else int(pj_value)
        if amount == 0:
            return await interaction.send(f"{pj_name} tiene {amount} de {value_name}.")
        else:
            new_value = pj_value + amount
            sh.update_pj_data_cell(pj_row, value_row, [[new_value]])

            return await interaction.send(
                f"{pj_name} {'gana' if amount>0 else 'pierde'} {abs(amount)} de {value_name}. Ahora tiene {new_value}."
            )

    return command


@bot.slash_command(
    description="Revisa o actualiza tu renombre", guild_ids=[CRI_GUILD_ID]
)
@gets_pj_data
async def renombre(
    interaction: nextcord.Interaction, amount: int, user: nextcord.Member = None
) -> Any:
    command = simple_value_update_command(PJ_COL.Renombre, "renombre")
    return await command(interaction, amount, user)


@bot.slash_command(
    description="Revisa o actualiza tu favor divino", guild_ids=[CRI_GUILD_ID]
)
@gets_pj_data
async def favordivino(
    interaction: nextcord.Interaction, amount: int, user: nextcord.Member = None
) -> Any:
    command = simple_value_update_command(PJ_COL.DivineFavor, "favor divino")
    return await command(interaction, amount, user)


@bot.slash_command(
    description="Revisa o actualiza tu reputación", guild_ids=[CRI_GUILD_ID]
)
@gets_pj_data
async def reputacion(
    interaction: nextcord.Interaction, amount: int, user: nextcord.Member = None
) -> Any:
    command = simple_value_update_command(PJ_COL.Reputacion, "reputación")
    return await command(interaction, amount, user)


@bot.slash_command(
    description="Revisa o actualiza tu crianza", guild_ids=[CRI_GUILD_ID]
)
@gets_pj_data
async def crianza(
    interaction: nextcord.Interaction, amount: int, user: nextcord.Member = None
) -> Any:
    command = simple_value_update_command(PJ_COL.Crianza, "crianza")
    return await command(interaction, amount, user)


@bot.slash_command(
    description="Revisa o actualiza tu expresión", guild_ids=[CRI_GUILD_ID]
)
@gets_pj_data
async def expresion(
    interaction: nextcord.Interaction, amount: int, user: nextcord.Member = None
) -> Any:
    command = simple_value_update_command(PJ_COL.Expresion, "expresión")
    return await command(interaction, amount, user)


@bot.slash_command(
    description="Revisa o actualiza tu infamia", guild_ids=[CRI_GUILD_ID]
)
@gets_pj_data
async def infamia(
    interaction: nextcord.Interaction, amount: int, user: nextcord.Member = None
) -> Any:
    command = simple_value_update_command(PJ_COL.Infamia, "infamia")
    return await command(interaction, amount, user)


@bot.slash_command(
    description="Gana el downtime y dinero esperado de terminar una misión",
    guild_ids=[CRI_GUILD_ID],
)
@gets_pj_data
async def completarmision(
    interaction: nextcord.Interaction, level: int, user: nextcord.Member = None
) -> Any:
    user_id: int = interaction.user.id if user is None else user.id
    pass


bot.run(BOT_TOKEN)
