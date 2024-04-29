from typing import Any, Self, Tuple

import nextcord  # type: ignore
from nextcord.ext import commands  # type: ignore

import SheetControl as sh
import utils
from SheetControl import PJ_COL, gets_pj_data
from utils import CharacterNotFoundError
from varenv import getVar

CRI_GUILD_ID = int(getVar("GUILD_ID"))


class Money(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:
        self.client = client

    @nextcord.slash_command(
        description="Resta dinero de tu cuenta. Puedes transferir a otra persona.",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_pj_data
    async def pay(
        self: Self,
        interaction: nextcord.Interaction,
        amount_str: str = nextcord.SlashOption(
            "money-gp", "Dinero restado a tu cuenta, en gp", True
        ),
        transfertarget: nextcord.Member = nextcord.SlashOption(
            "target-transferencia",
            "Usuario al que se le transfiere el dinero",
            False,
            default=None,
        ),
    ) -> Any:
        try:
            amount: float = utils.parse_float_arg(amount_str)
            if amount < 0:
                raise ValueError("La cantidad debe ser mayor o igual a 0")
        except ValueError as e:
            return await interaction.send(f"Error: {e}")
        user_id: int = interaction.user.id

        try:
            pj_row: int = sh.get_pj_row(user_id)
            pj_name: str = sh.get_pj_data(pj_row, PJ_COL.Name)
            if transfertarget is not None:
                target_id: int = transfertarget.id
                target_pj_row: int = sh.get_pj_row(target_id)
                target_pj_name: str = sh.get_pj_data(target_pj_row, PJ_COL.Name)
            else:
                target_pj_row = target_pj_name = None

        except CharacterNotFoundError:
            return await interaction.send(
                "No se encontró un personaje con ID de discord correspondiente"
            )
        if amount < 0:
            return await interaction.send("Debes pagar una cantidad positiva de dinero")

        pj_coins: list[float] = sh.get_pj_coins(pj_row)
        pp, gp, sp, cp, total = pj_coins
        if total - amount < 0:
            return await interaction.send(
                "No tienes suficiente dinero para esta transacción"
            )

        new_total = total - amount
        new_coins: list[int] = utils.gp_to_coin_list(new_total)
        pp, gp, sp, cp = new_coins
        sh.update_pj_coins(pj_row, [new_coins])

        if transfertarget is not None and target_pj_row is not None:
            target_coins = sh.get_pj_coins(target_pj_row)
            pp, gp, sp, cp, total = target_coins
            new_total_target = total + amount
            new_coins = utils.gp_to_coin_list(new_total_target)
            sh.update_pj_coins(target_pj_row, [new_coins])
            return await interaction.send(
                (
                    f"{pj_name} le transfiere {amount}gp a {target_pj_name}."
                    f" \n{pj_name} queda con {new_total:.2f}gp,"
                    f" y {target_pj_name} queda con {new_total_target:.2f}gp."
                )
            )
        else:
            return await interaction.send(
                (
                    f"{pj_name} paga {amount}gp. Ahora tiene {pp}pp,"
                    f" {gp}gp, {sp}sp, {cp}cp, **Total: {new_total:.2f}gp**"
                )
            )

    @nextcord.slash_command(
        description="Suma dinero a tu cuenta.", guild_ids=[CRI_GUILD_ID]
    )
    @gets_pj_data
    async def addmoney(
        self: Self,
        interaction: nextcord.Interaction,
        amount_str: str = nextcord.SlashOption(
            "money-gp", "Dinero añadido a tu cuenta, en gp", True
        ),
        target: nextcord.Member = nextcord.SlashOption(
            "usuario-target",
            "Usuario al que se le añade el dinero",
            False,
            default=None,
        ),
    ) -> Any:
        try:
            amount: float = utils.parse_float_arg(amount_str)
            if amount < 0:
                raise ValueError("La cantidad debe ser mayor o igual a 0")
        except ValueError as e:
            return await interaction.send(f"Error: {e}")
        user_id: int = target.id if target is not None else interaction.user.id
        try:
            pj_row = sh.get_pj_row(user_id)
            pj_name = sh.get_pj_data(pj_row, PJ_COL.Name)
        except CharacterNotFoundError:
            return await interaction.send(
                "No se encontró un personaje con ID de discord correspondiente"
            )
        if amount < 0:
            return await interaction.send("Debes ganar una cantidad positiva de dinero")

        pp, gp, sp, cp, new_total = add_money_helper(amount, pj_row)

        return await interaction.send(
            (
                f"{pj_name} obtiene {amount}gp. Ahora tiene {pp}pp,"
                f" {gp}gp, {sp}sp, {cp}cp, **Total: {new_total:.2f}gp**"
            )
        )


def add_money_helper(amount, pj_row) -> Tuple[int, int, int, int, int]:
    """
    return pp, gp, sp, cp, new_total
    """
    pj_coins = sh.get_pj_coins(pj_row)
    pp, gp, sp, cp, total = pj_coins

    new_total = total + amount
    new_coins = utils.gp_to_coin_list(new_total)
    pp, gp, sp, cp = new_coins
    sh.update_pj_coins(pj_row, [new_coins])
    return pp, gp, sp, cp, new_total


def setup(client: commands.Bot) -> None:
    client.add_cog(Money(client))
