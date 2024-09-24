from typing import Any, Callable, Self

import nextcord  # type: ignore
from nextcord.ext import commands

import SheetControl as sh
from PF2eData import ANCESTRIES, CLASSES, HERITAGES, RELIGIONS, ARCHETYPES
from SheetControl import PJ_COL, gets_pj_data
from utils import CharacterNotFoundError
from varenv import getVar

CRI_GUILD_ID = int(getVar("GUILD_ID"))


class HeritageDropdown(nextcord.ui.Select):  # type: ignore
    Update_func: Callable[[nextcord.Interaction, str], Any]
    

    def __init__(
        self: Self,
        ancestry: str,
        update_func: Callable[[nextcord.Interaction, str], Any],
    ) -> None:
        heritages: list[str] = HERITAGES[ancestry]
        self.Update_func: Callable[[nextcord.Interaction, str], Any] = update_func

        options = [nextcord.SelectOption(label=h) for h in heritages]
        options += [
            nextcord.SelectOption(label=h, description="(Heritage versátil)")
            for h in HERITAGES["Versatile"]
        ]
        super().__init__(
            placeholder="Opciones de heritage",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self: Self, interaction: nextcord.Interaction) -> None:
        selected: str = self.values[0]
        try:
            assert self.view is not None
        except AssertionError:
            return
        self.view.stop()
        await self.Update_func(interaction, selected)


class RegisterDropdownView(nextcord.ui.View):
    def __init__(self: Self, heritage_dropdown: HeritageDropdown) -> None:
        super().__init__()
        self.add_item(heritage_dropdown)


class Register(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:  # type: ignore
        self.client = client

    @nextcord.slash_command(
        description="Registra un nuevo personaje de Megamarch.",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_pj_data
    async def register(
        self: Self,
        interaction: nextcord.Interaction,
        nombre_pj: str,
        nombre_jugador: str,
        clase: str = nextcord.SlashOption(
            name="clase",
            description="La clase de tu personaje",
            required=True,
            choices=CLASSES,
        ),
        ascendencia: str = nextcord.SlashOption(
            name="ascendencia",
            description="La ascendencia de tu personaje (escribe para el autocomplete)",
            required=True,
        ),
        religion: str = nextcord.SlashOption(
            name="religión",
            description="La religión de tu personaje",
            required=True,
            choices=RELIGIONS,
        ),
    ) -> Any:
        await interaction.response.defer()
        # Conseguir el ID del usuario
        try:
            assert interaction.user is not None
        except AssertionError:
            return await interaction.followup.send("Error: Null user")

        user_id: int = interaction.user.id
        # Revisar que no tenga otro PJ
        already_has_character = True
        try:
            pj_row = sh.get_pj_row(user_id)
        except CharacterNotFoundError:
            already_has_character = False
        if already_has_character:
            return await interaction.followup.send(
                (
                    f"Ya tienes un personaje en la fila {pj_row}"
                    f", muevelo al cementerio para registrar uno nuevo."
                )
            )
        ascendencia = ascendencia.capitalize()
        if ascendencia not in ANCESTRIES:
            return await interaction.followup.send(
                f"'{ascendencia}' no es una ascendencia válida."
            )

        # Generar stats base (0 de dt, 15 de gp)
        # [nombre, id, jugador, clase, Arquetipos, ascendencia, heritage, dt, pp, gp, sp, cp, total, lenguajes, religión] # noqa: E501
        async def update_func(
            interaction: nextcord.Interaction, selected_heritage: str
        ) -> Any:
            values = [
                nombre_pj,
                str(user_id),
                nombre_jugador,
                clase,
                "",
                ascendencia,
                selected_heritage,
                0,
                0,
                15,
                0,
                0,
            ]
            pj_row = sh.first_empty_PJ_row()
            sh.update_range_PJ(
                [values], f"{PJ_COL.Name}{pj_row}:{PJ_COL.Money_cp}{pj_row}"
            )
            sh.update_range_PJ([[religion]], f"{PJ_COL.Religion}{pj_row}")
            await interaction.followup.send(f"Registrado {nombre_pj} en la fila {pj_row}")

        heritage_dropdown = HeritageDropdown(ascendencia, update_func)

        view = RegisterDropdownView(heritage_dropdown)
        await interaction.followup.send("Selecciona un heritage para tu personaje", view=view)

    @nextcord.slash_command(
        description="Registra un nuevo arquetipo para tu personaje. Si seleccionas uno que ya tienes se elimina.",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_pj_data
    async def register_archetype(
        self: Self,
        interaction: nextcord.Interaction,
        archetype: str = nextcord.SlashOption(
            name="archetype",
            description="El nuevo arquetipo de tu personaje, o uno que ya tuviera para eliminarlo.",
            required=True,
            choices=CLASSES,
        )
    ) -> Any:
        await interaction.response.defer()
        # Conseguir el ID del usuario
        try:
            assert interaction.user is not None
        except AssertionError:
            return await interaction.followup.send("Error: Null user")

        user_id: int = interaction.user.id
        # Revisar que no tenga otro PJ
        try:
            pj_row = sh.get_pj_row(user_id)
        except CharacterNotFoundError:
            return await interaction.followup.send(
                "No se encontró un personaje con ID de discord correspondiente"
            )
        archs = sh.get_pj_data(pj_row, PJ_COL.Arquetypes)
        archs_list = archs.split(", ")
        if archetype in archs_list:
            archs_list.remove(archetype)
            message = f"Eliminado {archetype} de tu lista de arquetipos"
        else:
            archs_list.append(archetype)
            message = f"Añadido {archetype} a tu lista de arquetipos"
        new_archetypes = ", ".join(archs_list)
        sh.update_pj_data_cell(pj_row, PJ_COL.Arquetypes, [[new_archetypes]])

        await interaction.followup.send(message)

    @register.on_autocomplete("ascendencia")
    async def autocomplete_ancestry(
        self, interaction: nextcord.Interaction, ancestry: str
    ) -> Any:
        filtered_ancestries = []
        if ancestry:
            filtered_ancestries = [
                a for a in ANCESTRIES if a.lower().startswith(ancestry.lower())
            ]
        await interaction.response.send_autocomplete(filtered_ancestries)

    @register_archetype.on_autocomplete("archetype")
    async def autocomplete_archetype(
        self, interaction: nextcord.Interaction, archetype: str
    ) -> Any:
        filtered_archetypes = []
        if archetype:
            filtered_archetypes = [
                a for a in ARCHETYPES if a.lower().startswith(archetype.lower())
            ]
        await interaction.response.send_autocomplete(filtered_archetypes)


def setup(client: commands.Bot) -> None:
    client.add_cog(Register(client))
