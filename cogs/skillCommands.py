from typing import Any, Self

import dndice
import nextcord  # type: ignore
from nextcord.ext import commands  # type: ignore

import SheetControl as sh_pj
import SheetControlSkills as sh_skills
from PF2eData import ABILITIES, PROF, PROF_BONUSES, SKILLS, Ability
from SheetControl import PJ_COL, gets_pj_data
from SheetControlSkills import gets_skill_data
from cogs.skillUtils import filter_lores
from utils import CharacterNotFoundError
from varenv import getVar

from .skillUtils import *

CRI_GUILD_ID = int(getVar("GUILD_ID"))


class Skills(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:
        self.client = client

    @nextcord.slash_command(
        description="Muestra la información de todas las skills de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_skill_data
    async def all_skills(
        self: Self, interaction: nextcord.Interaction, extra_info: bool = False
    ) -> Any:
        user_id: int = interaction.user.id
        pj_mods: dict[Ability, int]
        name_mods, row, pj_mods = sh_skills.get_pj_abilities(user_id)

        if name_mods is None:
            return await interaction.send(
                "Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            )
        pj_skills: dict[str, dict[str, str | int]]
        # {skill_name: {prof_level: str, extra_bonus: int, extra_descripcion: str}}
        name, pj_skills = sh_skills.get_pj_skills(user_id)

        message: str = f"# Skills de {name_mods if name is None else name}:"

        pj_level = sh_pj.get_level_global()

        for skill_name, mod_type in SKILLS:
            if skill_name == "Lore":
                continue
            message += skill_description(
                pj_mods[mod_type],
                pj_level,
                mod_type,
                skill_name,
                pj_skills.get(skill_name, None),
                extra_info,
            )

        lores = [
            (skill_name, values)
            for skill_name, values in pj_skills.items()
            if skill_name.startswith("Lore")
        ]
        for lore_name, lore in lores:
            pj_mod_bonus: int = pj_mods[ABILITIES.Int]
            message += skill_description(
                pj_mod_bonus,
                pj_level,
                ABILITIES.Int,
                lore_name,
                lore,
                extra_info,
            )
        return await interaction.send(message)

    @nextcord.slash_command(
        description="Muestra la información de todas las lore skills de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_skill_data
    async def all_lores(
        self: Self, interaction: nextcord.Interaction, extra_info: bool = False
    ) -> Any:
        user_id: int = interaction.user.id
        pj_mods: dict[Ability, int]
        name_mods, row, pj_mods = sh_skills.get_pj_abilities(user_id)

        if name_mods is None:
            return await interaction.send(
                "Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            )
        pj_skills: dict[str, dict[str, str | int]]
        # {skill_name: {prof_level: str, extra_bonus: int, extra_descripcion: str}}
        name, pj_skills = sh_skills.get_pj_skills(user_id)

        message: str = f"# Skills de {name_mods if name is None else name}:"

        pj_level = sh_pj.get_level_global()

        lores = [
            (skill_name, values)
            for skill_name, values in pj_skills.items()
            if skill_name.startswith("Lore")
        ]
        for lore_name, lore in lores:
            pj_mod_bonus: int = pj_mods[ABILITIES.Int]
            message += skill_description(
                pj_mod_bonus,
                pj_level,
                ABILITIES.Int,
                lore_name,
                lore,
                extra_info,
            )
        return await interaction.send(message)

    @nextcord.slash_command(
        description="Muestra la información de una skill de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_skill_data
    async def skill(
        self: Self,
        interaction: nextcord.Interaction,
        skill: str = nextcord.SlashOption(
            name="skill",
            description="La skill de tu personaje",
            required=True,
            choices=[skill[0] for skill in SKILLS if skill[0] != "Lore"],
        ),
        extra_info: bool = False,
    ) -> Any:
        user_id: int = interaction.user.id
        pj_mods: dict[Ability, int]
        name_mods, row, pj_mods = sh_skills.get_pj_abilities(user_id)

        if name_mods is None:
            return await interaction.send(
                "Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            )
        pj_skills: dict[str, dict[str, str | int]]
        # {skill_name: {prof_level: str, extra_bonus: int, extra_descripcion: str}}
        name, pj_skills = sh_skills.get_pj_skills(user_id)

        message: str = f"## {skill} de {name_mods if name is None else name}:"

        pj_level = sh_pj.get_level_global()
        mod_type: Ability = [ab for skill_nm, ab in SKILLS if skill_nm == skill][0]

        message += skill_description(
            pj_mods[mod_type],
            pj_level,
            mod_type,
            skill,
            pj_skills.get(skill, None),
            extra_info,
        )

        return await interaction.send(message)

    @nextcord.slash_command(
        description="Muestra la información de una skill de lore de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_skill_data
    async def lore(
        self: Self,
        interaction: nextcord.Interaction,
        lore_subname: str = nextcord.SlashOption(
            name="lore",
            description="El lore de tu personaje (sin 'Lore ')",
            required=True,
        ),
        extra_info: bool = False,
    ) -> Any:
        user_id: int = interaction.user.id
        pj_mods: dict[Ability, int]
        name_mods, row, pj_mods = sh_skills.get_pj_abilities(user_id)

        if name_mods is None:
            return await interaction.send(
                "Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            )
        pj_skills: dict[str, dict[str, str | int]]
        # {skill_name: {prof_level: str, extra_bonus: int, extra_descripcion: str}}
        name, pj_skills = sh_skills.get_pj_skills(user_id)

        lore_full_name = f"Lore ({lore_subname})"

        message: str = f"## {lore_full_name} de {name_mods if name is None else name}:"

        pj_level = sh_pj.get_level_global()
        mod_type: Ability = ABILITIES.Int

        message += skill_description(
            pj_mods[mod_type],
            pj_level,
            mod_type,
            lore_full_name,
            pj_skills.get(lore_full_name, None),
            extra_info,
        )

        return await interaction.send(message)

    @nextcord.slash_command(
        description="Define la proficiencia de una skill de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_skill_data
    @gets_pj_data
    async def set_skill(
        self: Self,
        interaction: nextcord.Interaction,
        skill: str = nextcord.SlashOption(
            name="skill",
            description="La skill de tu personaje a definir",
            required=True,
            choices=[skill[0] for skill in SKILLS if skill[0] != "Lore"],
        ),
        proficiency: str = nextcord.SlashOption(
            name="proficiency",
            description="El nivel de proficiencia de la skill",
            required=True,
            choices=PROF.profs_list,
        ),
        other_bonuses: int = nextcord.SlashOption(
            name="other_bonuses",
            description="La suma de otros bonos (ni profi ni ability)  (default 0)",
            required=False,
            default=0,
        ),
        other_bonuses_description: str = nextcord.SlashOption(
            name="other_bonuses_description",
            description="Detalle de los otros bonos",
            required=False,
            default="",
        ),
    ) -> Any:
        user_id: int = interaction.user.id

        pj_skills: dict[str, dict[str, str | int]]
        pj_name, pj_skills = sh_skills.get_pj_skills(user_id)

        pj_skill = pj_skills.get(skill, None)

        if pj_skill is None:
            # Create new skill entry
            try:
                pj_name = sh_pj.get_pj_data(sh_pj.get_pj_row(user_id), PJ_COL.Name)
            except CharacterNotFoundError as e:
                return await interaction.send(e)
            row: int = sh_skills.first_empty_skill_row()
            msg = f"Se definió la proficiencia de {pj_name} en {skill}"
        else:
            # update existing skill entry
            row = pj_skill["row"]
            msg = f"Se actualizó la proficiencia de {pj_name} en {skill}"

        data = (
            pj_name,
            str(user_id),
            skill,
            proficiency,
            other_bonuses,
            other_bonuses_description,
        )
        sh_skills.update_skill_row(row, data)
        return await interaction.send(msg)

    @nextcord.slash_command(
        description="Define las proficiencias de todas las skills de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_skill_data
    @gets_pj_data
    async def set_all_skills(
        self: Self,
        interaction: nextcord.Interaction,
        perception: str = ability_param("perception"),
        acrobatics: str = ability_param("acrobatics"),
        arcana: str = ability_param("arcana"),
        athletics: str = ability_param("athletics"),
        crafting: str = ability_param("crafting"),
        deception: str = ability_param("deception"),
        diplomacy: str = ability_param("diplomacy"),
        intimidation: str = ability_param("intimidation"),
        medicine: str = ability_param("medicine"),
        nature: str = ability_param("nature"),
        occultism: str = ability_param("occultism"),
        performance: str = ability_param("performance"),
        religion: str = ability_param("religion"),
        society: str = ability_param("society"),
        stealth: str = ability_param("stealth"),
        survival: str = ability_param("survival"),
        thievery: str = ability_param("thievery"),
    ) -> Any:
        user_id: int = interaction.user.id

        pj_skills: dict[str, dict[str, str | int]]
        pj_name, pj_skills = sh_skills.get_pj_skills(user_id)

        try:
            pj_name = sh_pj.get_pj_data(sh_pj.get_pj_row(user_id), PJ_COL.Name)
        except CharacterNotFoundError as e:
            return await interaction.send(e)

        better_args = [
            ("Perception", perception),
            ("Acrobatics", acrobatics),
            ("Arcana", arcana),
            ("Athletics", athletics),
            ("Crafting", crafting),
            ("Deception", deception),
            ("Diplomacy", diplomacy),
            ("Intimidation", intimidation),
            ("Medicine", medicine),
            ("Nature", nature),
            ("Occultism", occultism),
            ("Performance", performance),
            ("Religion", religion),
            ("Society", society),
            ("Stealth", stealth),
            ("Survival", survival),
            ("Thievery", thievery),
        ]

        msg = ""
        rows_and_data = []
        first_empty_row = sh_skills.first_empty_skill_row()
        for skill_name, prof_value in better_args:
            pj_skill = pj_skills.get(skill_name, None)

            if pj_skill is None:
                # Create new skill entry
                row: int = first_empty_row
                msg += f"\nSe definió la proficiencia de {pj_name} en {skill_name}"
                first_empty_row += 1

            else:
                # update existing skill entry
                row = pj_skill["row"]
                msg += f"\nSe actualizó la proficiencia de {pj_name} en {skill_name}"

            data = (
                pj_name,
                str(user_id),
                skill_name,
                prof_value,
                0,
                "",
            )
            rows_and_data.append((row, data))
        sh_skills.multi_update_skill_row(rows_and_data)
        return await interaction.send(msg)

    @nextcord.slash_command(
        description="Define la proficiencia de una skill de lore de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_skill_data
    @gets_pj_data
    async def set_lore(
        self: Self,
        interaction: nextcord.Interaction,
        lore_subname: str = nextcord.SlashOption(
            name="lore_name",
            description="El nombre del lore (sin 'Lore')",
            required=True,
        ),
        proficiency: str = nextcord.SlashOption(
            name="proficiency",
            description="El nivel de proficiencia de la skill",
            required=True,
            choices=PROF.profs_list,
        ),
        other_bonuses: int = nextcord.SlashOption(
            name="other_bonuses",
            description="La suma de otros bonos (ni profi ni ability) (default 0)",
            required=False,
            default=0,
        ),
        other_bonuses_description: str = nextcord.SlashOption(
            name="other_bonuses_description",
            description="Detalle de los otros bonos",
            required=False,
            default="",
        ),
    ) -> Any:
        user_id: int = interaction.user.id

        pj_skills: dict[str, dict[str, str | int]]
        pj_name, pj_skills = sh_skills.get_pj_skills(user_id)

        skill = f"Lore ({lore_subname})"

        pj_skill = pj_skills.get(skill, None)

        if pj_skill is None:
            # Create new skill entry
            try:
                pj_name = sh_pj.get_pj_data(sh_pj.get_pj_row(user_id), PJ_COL.Name)
            except CharacterNotFoundError as e:
                return await interaction.send(e)
            row: int = sh_skills.first_empty_skill_row()
            msg = f"Se definió la proficiencia de {pj_name} en {skill}"
        else:
            # update existing skill entry
            row = pj_skill["row"]
            msg = f"Se actualizó la proficiencia de {pj_name} en {skill}"

        data = (
            pj_name,
            str(user_id),
            skill,
            proficiency,
            other_bonuses,
            other_bonuses_description,
        )
        sh_skills.update_skill_row(row, data)
        return await interaction.send(msg)

    @nextcord.slash_command(
        description="Define los modificadores de habilidad de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_skill_data
    @gets_pj_data
    async def set_modifiers(
        self: Self,
        interaction: nextcord.Interaction,
        strength: int,
        dexterity: int,
        constitution: int,
        intelligence: int,
        wisdom: int,
        charisma: int,
    ) -> Any:
        user_id: int = interaction.user.id

        pj_name, row, _ = sh_skills.get_pj_abilities(user_id)

        if pj_name is None:
            # Crear nueva row
            row = sh_skills.first_empty_ability_row()
            try:
                pj_name = sh_pj.get_pj_data(sh_pj.get_pj_row(user_id), PJ_COL.Name)
            except CharacterNotFoundError as e:
                return await interaction.send(e)
        data = (
            pj_name,
            str(user_id),
            strength,
            dexterity,
            constitution,
            intelligence,
            wisdom,
            charisma,
        )
        sh_skills.update_ability_row(row, data)
        return await interaction.send(
            f"Actualizados los modificadores de habilidad de {pj_name}"
        )

    @nextcord.slash_command(
        description="Tira un skill check con el skill seleccionado",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_skill_data
    async def roll_skill(
        self: Self,
        interaction: nextcord.Interaction,
        skill: str = nextcord.SlashOption(
            name="skill",
            description="La skill de tu personaje que quieres usar",
            required=True,
            choices=[skill[0] for skill in SKILLS if skill[0] != "Lore"],
        ),
        extra_modifiers: int = nextcord.SlashOption(
            name="extra_modifiers",
            description="Cualquier bono o penalización adicional para esta tirada",
            required=False,
            default=0,
        ),
        extra_info: bool = False,
    ) -> Any:
        user_id: int = interaction.user.id

        pj_mods: dict[Ability, int]
        name_mods, row, pj_mods = sh_skills.get_pj_abilities(user_id)

        if name_mods is None:
            return await interaction.send(
                "Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            )

        # {skill_name: {prof_level: str, extra_bonus: int, extra_descripcion: str}}
        pj_skills: dict[str, dict[str, str | int]]
        name, pj_skills = sh_skills.get_pj_skills(user_id)

        dice = int(dndice.basic("1d20"))
        nat_20_1: str = nat_20_1_message(dice)

        # ABILITY
        mod_type: Ability = [ab for skill_nm, ab in SKILLS if skill_nm == skill][0]
        ability_bonus = pj_mods[mod_type]
        ability_msg = f"[{mod_type.name}: {signed_bonus(ability_bonus)}]"

        # EXTRA
        extra_msg = (
            "" if extra_modifiers == 0 else f"[Extra: {signed_bonus(extra_modifiers)}]"
        )

        # PROFICIENCY
        pj_skill = pj_skills.get(skill, None)
        if pj_skill is None:
            prof_bonus = 0
            prof_msg = "[Untrained?: +0]"
        else:
            prof_level: str = pj_skill["prof_level"]
            pj_level = sh_pj.get_level_global()
            level_bonus: int = 0 if prof_level == PROF.Untrained else pj_level
            prof_bonus: int = PROF_BONUSES[prof_level] + level_bonus
            prof_msg = f"[{prof_level}: +{prof_bonus}]"

        # OTHER
        if pj_skill is None:
            other_msg = ""
            other_bonus = 0
        else:
            other_bonus: int = pj_skill["extra_bonus"]
            other_descripcion: str = pj_skill["extra_descripcion"]
            other_msg = (
                ""
                if (other_bonus == 0 and other_descripcion == "")
                else f"[Other: {signed_bonus(other_bonus)}{f' ({other_descripcion})' if extra_info else ''}])*"
            )

        result = dice + ability_bonus + prof_bonus + other_bonus + extra_modifiers

        message = f"{name_mods} {skill} roll: `{result}` {nat_20_1}\n[Dice: {dice}]{ability_msg}{prof_msg}{other_msg}{extra_msg}"
        return await interaction.send(message)

    @nextcord.slash_command(
        description="Tira un lore skill check con el lore skill seleccionado",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_skill_data
    async def roll_lore(
        self: Self,
        interaction: nextcord.Interaction,
        lore_subname: str = nextcord.SlashOption(
            name="lore",
            description="El lore de tu personaje (sin 'Lore ')",
            required=True,
        ),
        extra_modifiers: int = nextcord.SlashOption(
            name="extra_modifiers",
            description="Cualquier bono o penalización adicional para esta tirada",
            required=False,
            default=0,
        ),
        extra_info: bool = False,
    ) -> Any:
        user_id: int = interaction.user.id

        pj_mods: dict[Ability, int]
        name_mods, row, pj_mods = sh_skills.get_pj_abilities(user_id)

        if name_mods is None:
            return await interaction.send(
                "Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            )

        # {skill_name: {prof_level: str, extra_bonus: int, extra_descripcion: str}}
        pj_skills: dict[str, dict[str, str | int]]
        name, pj_skills = sh_skills.get_pj_skills(user_id)

        dice = int(dndice.basic("1d20"))
        nat_20_1: str = nat_20_1_message(dice)

        # ABILITY
        mod_type: Ability = ABILITIES.Int
        ability_bonus = pj_mods[mod_type]
        ability_msg = f"[{mod_type.name}: {signed_bonus(ability_bonus)}]"

        # EXTRA
        extra_msg = (
            "" if extra_modifiers == 0 else f"[Extra: {signed_bonus(extra_modifiers)}]"
        )

        lore_full_name = f"Lore ({lore_subname})"
        # PROFICIENCY
        pj_skill = pj_skills.get(lore_full_name, None)
        if pj_skill is None:
            prof_bonus = 0
            prof_msg = "[Untrained?: +0]"
        else:
            prof_level: str = pj_skill["prof_level"]
            pj_level = sh_pj.get_level_global()
            level_bonus: int = 0 if prof_level == PROF.Untrained else pj_level
            prof_bonus: int = PROF_BONUSES[prof_level] + level_bonus
            prof_msg = f"[{prof_level}: +{prof_bonus}]"

        # OTHER
        if pj_skill is None:
            other_msg = ""
            other_bonus = 0
        else:
            other_bonus: int = pj_skill["extra_bonus"]
            other_descripcion: str = pj_skill["extra_descripcion"]
            other_msg = (
                ""
                if (other_bonus == 0 and other_descripcion == "")
                else f"[Other: {signed_bonus(other_bonus)}{f' ({other_descripcion})' if extra_info else ''}])*"
            )

        result = dice + ability_bonus + prof_bonus + other_bonus + extra_modifiers

        message = f"{name_mods} {lore_full_name} roll: `{result}` {nat_20_1}\n[Dice: {dice}]{ability_msg}{prof_msg}{other_msg}{extra_msg}"
        return await interaction.send(message)

    @set_lore.on_autocomplete("lore_subname")
    async def autocomplete_set_lore_subname(
        self: Self, interaction: nextcord.Interaction, lore_subname: str
    ) -> Any:
        filtered_lores: list[str] = filter_lores(lore_subname, None)
        await interaction.response.send_autocomplete(filtered_lores)

    @lore.on_autocomplete("lore_subname")
    @roll_lore.on_autocomplete("lore_subname")
    async def autocomplete_lore_subname(
        self: Self, interaction: nextcord.Interaction, lore_subname: str
    ) -> Any:
        user_id: int = interaction.user.id

        filtered_lores: list[str] = filter_lores(lore_subname, user_id)
        await interaction.response.send_autocomplete(filtered_lores)


def setup(client: commands.Bot) -> None:
    client.add_cog(Skills(client))
