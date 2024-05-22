from typing import Any, Self

import nextcord  # type: ignore
from nextcord.ext import commands  # type: ignore

import SheetControl as sh
from PF2eData import Recipe
from SheetControl import PJ_COL, gets_pj_data
from SheetControlRecipes import add_recipe, get_all_existing_recipes, gets_recipe_data
from utils import CharacterNotFoundError, default_user_option
from varenv import getVar

CRI_GUILD_ID = int(getVar("GUILD_ID"))


class Recipes(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:
        self.client = client

    @nextcord.slash_command(
        description="Muestra la lista de recipes disponibles", guild_ids=[CRI_GUILD_ID]
    )
    @gets_recipe_data
    async def global_recipes(
        self: Self,
        interaction: nextcord.Interaction,
        level: int = nextcord.SlashOption(
            "item_level", "Nivel de los items de las recipes", False, min_value=0, max_value=25
        ),
    ) -> Any:
        await interaction.response.defer()
        recipes: list[Recipe] = get_all_existing_recipes()
        if len(recipes) == 0:
            await interaction.followup.send("No hay recipes globales")
        message = f"**Todas las recetas públicas{f" de nivel {level}" if level is not None else ""}:**"
        if level is not None:
            recipes = [r for r in recipes if r["level"] == level]
        recipes - recipes.sort(key=(lambda r: r["name"])).sort(key=(lambda r: r["level"]))
        for r in recipes:
            message += f'\n- (Lvl {r["level"]}) {r["name"]}'
        return await interaction.followup.send(message)

    @nextcord.slash_command(
        description="Añade una recipe a la lista de recipes globales", guild_ids=[CRI_GUILD_ID]
    )
    @gets_recipe_data
    async def add_recipe(
        self: Self,
        interaction: nextcord.Interaction,
        item_name: str = nextcord.SlashOption(
            "item", "Nombre del item de la recipe", True
        ),
        item_level: int = nextcord.SlashOption(
            "level", "Nivel del item de la recipe", True, min_value=0, max_value=25
        ),
    ) -> Any:
        await interaction.response.defer()
        recipes: list[Recipe] = get_all_existing_recipes()
        recipe_names = [r["name"] for r in recipes]
        if item_name in recipe_names:
            await interaction.followup.send(f"*{item_name}* ya está registrado en la lista de recipes globales")
        else:
            add_recipe(item_name, item_level)
            await interaction.followup.send(f"*{item_name}* se registró en la lista de recipes globales")


def setup(client: commands.Bot) -> None:
    client.add_cog(Recipes(client))
