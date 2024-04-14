from typing import Any, Self

import dndice
import nextcord  # type: ignore
from nextcord.ext import commands  # type: ignore

import SheetControl as sh_pj
import SheetControlSkills as sh_skills
from PF2eData import ABILITIES, PROF, PROF_BONUSES, SKILLS, Ability
from SheetControl import PJ_COL, gets_pj_data
from SheetControlSkills import gets_skill_data
from utils import CharacterNotFoundError
from varenv import getVar

CRI_GUILD_ID = int(getVar("GUILD_ID"))


def longest_skill_name_length(skills_dict: dict[str, Any]) -> int:
    skill_name_lens = (
        [0] if len(skills_dict) == 0 else [len(name) for name in skills_dict.keys()]
    )

    return max(
        max(skill_name_lens),
        max([len(skill[0]) for skill in SKILLS]),
    )


def skill_description(
    pj_mod_bonus: int,
    pj_level: int,
    mod_type: Ability,
    skill_name: str,
    pj_skill: None | dict[str, str | int],
    extra_info: bool,
    justify: int,
) -> str:
    if pj_skill is None:
        bonus_str: str = signed_bonus(pj_mod_bonus)
        skill_title = f"**{skill_name}** *(Untrained?)*:`"
        submsg: str = (
            f"\n- {skill_title.ljust(35)} `"
            f"{bonus_str} "
            f"([{mod_type.name}: {bonus_str}])"
        )
    else:
        prof_level: str = pj_skill["prof_level"]
        level_bonus: int = 0 if prof_level == PROF.Untrained else pj_level
        prof_bonus: int = PROF_BONUSES[prof_level]
        extra_bonus: int = pj_skill["extra_bonus"]
        extra_descripcion: str = pj_skill["extra_descripcion"]
        skill_title = f"**{skill_name}** *({prof_level})*:`"

        extra_msg = (
            ""
            if (extra_bonus == 0 and extra_descripcion == "")
            else f"[Other: {signed_bonus(extra_bonus)}{f' ({extra_descripcion})' if extra_info else ''}])*"
        )
        submsg: str = (
            f"\n- {skill_title.ljust(35)} `"
            f'{f"{signed_bonus(prof_bonus + pj_mod_bonus +
                               extra_bonus + level_bonus)} ".ljust(4)}'
            f"*([{mod_type.name}: {signed_bonus(pj_mod_bonus)}]"
            f"[{prof_level}: {signed_bonus(prof_bonus + level_bonus)}]"
            f"{extra_msg}"
        )
    return submsg


def signed_bonus(bonus: int) -> str:
    return f"+{bonus}" if bonus >= 0 else str(bonus)


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

        justify: int = longest_skill_name_length(pj_skills) + PROF.max_length + 1
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
                justify,
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
                justify,
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

        justify: int = longest_skill_name_length(pj_skills) + PROF.max_length + 1
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
                justify,
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

        justify: int = longest_skill_name_length(pj_skills) + PROF.max_length + 1
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
            justify,
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

        justify: int = longest_skill_name_length(pj_skills) + PROF.max_length + 1
        message: str = f"## {lore_full_name} de {name_mods if name is None else name}:"

        pj_level = sh_pj.get_level_global()
        mod_type: Ability = [
            ab for skill_nm, ab in SKILLS if skill_nm == lore_full_name
        ][0]

        message += skill_description(
            pj_mods[mod_type],
            pj_level,
            mod_type,
            lore_full_name,
            pj_skills.get(lore_full_name, None),
            extra_info,
            justify,
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
        perception: str = nextcord.SlashOption(
            name="perception",
            description="El nivel de proficiencia de Perception",
            required=True,
            choices=PROF.profs_list,
        ),
        acrobatics: str = nextcord.SlashOption(
            name="acrobatics",
            description="El nivel de proficiencia de Acrobatics",
            required=True,
            choices=PROF.profs_list,
        ),
        arcana: str = nextcord.SlashOption(
            name="arcana",
            description="El nivel de proficiencia de Arcana",
            required=True,
            choices=PROF.profs_list,
        ),
        athletics: str = nextcord.SlashOption(
            name="athletics",
            description="El nivel de proficiencia de Athletics",
            required=True,
            choices=PROF.profs_list,
        ),
        crafting: str = nextcord.SlashOption(
            name="crafting",
            description="El nivel de proficiencia de Crafting",
            required=True,
            choices=PROF.profs_list,
        ),
        deception: str = nextcord.SlashOption(
            name="deception",
            description="El nivel de proficiencia de Deception",
            required=True,
            choices=PROF.profs_list,
        ),
        diplomacy: str = nextcord.SlashOption(
            name="diplomacy",
            description="El nivel de proficiencia de Diplomacy",
            required=True,
            choices=PROF.profs_list,
        ),
        intimidation: str = nextcord.SlashOption(
            name="intimidation",
            description="El nivel de proficiencia de Intimidation",
            required=True,
            choices=PROF.profs_list,
        ),
        medicine: str = nextcord.SlashOption(
            name="medicine",
            description="El nivel de proficiencia de Medicine",
            required=True,
            choices=PROF.profs_list,
        ),
        nature: str = nextcord.SlashOption(
            name="nature",
            description="El nivel de proficiencia de Nature",
            required=True,
            choices=PROF.profs_list,
        ),
        occultism: str = nextcord.SlashOption(
            name="occultism",
            description="El nivel de proficiencia de Occultism",
            required=True,
            choices=PROF.profs_list,
        ),
        performance: str = nextcord.SlashOption(
            name="performance",
            description="El nivel de proficiencia de Performance",
            required=True,
            choices=PROF.profs_list,
        ),
        religion: str = nextcord.SlashOption(
            name="religion",
            description="El nivel de proficiencia de Religion",
            required=True,
            choices=PROF.profs_list,
        ),
        society: str = nextcord.SlashOption(
            name="society",
            description="El nivel de proficiencia de Society",
            required=True,
            choices=PROF.profs_list,
        ),
        stealth: str = nextcord.SlashOption(
            name="stealth",
            description="El nivel de proficiencia de Stealth",
            required=True,
            choices=PROF.profs_list,
        ),
        survival: str = nextcord.SlashOption(
            name="survival",
            description="El nivel de proficiencia de Survival",
            required=True,
            choices=PROF.profs_list,
        ),
        thievery: str = nextcord.SlashOption(
            name="thievery",
            description="El nivel de proficiencia de Thievery",
            required=True,
            choices=PROF.profs_list,
        ),
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
            first_empty_row += 1
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

        pj_abilites: dict[Ability, int]
        pj_name, row, pj_abilites = sh_skills.get_pj_abilities(user_id)

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

    # @nextcord.slash_command(
    #     description="Tira un skill check con el skill seleccionado",
    #     guild_ids=[CRI_GUILD_ID],
    # )
    # @gets_skill_data
    # async def roll_skill(
    #     self: Self,
    #     interaction: nextcord.Interaction,
    #     skill: str = nextcord.SlashOption(
    #         name="skill",
    #         description="La skill de tu personaje",
    #         required=True,
    #         choices=[skill[0] for skill in SKILLS if skill[0] != "Lore"],
    #     ),
    #     extra_modifiers: int = nextcord.SlashOption(
    #         name="extra_modifiers",
    #         description="Cualquier bono o penalización adicional para esta tirada",
    #         required=False,
    #         default=0
    #     ),
    #     extra_info: bool = False,
    # ) -> Any:
    #     user_id: int = interaction.user.id
    #     pj_mods: dict[Ability, int]
    #     name_mods, row, pj_mods = sh_skills.get_pj_abilities(user_id)

    #     if name_mods is None:
    #         return await interaction.send(
    #             "Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
    #         )

    #     pj_skills: dict[str, dict[str, str | int]]
    #     # {skill_name: {prof_level: str, extra_bonus: int, extra_descripcion: str}}
    #     name, pj_skills = sh_skills.get_pj_skills(user_id)
    #     mod_type: Ability = [ab for skill_nm, ab in SKILLS if skill_nm == skill][0]

    #     pj_skill = pj_skills.get(skill, None)
    #     if pj_skill is None:
    #         dice = dndice.basic('1d20')

    #     prof_level: str = pj_skill["prof_level"]
    #     level_bonus: int = 0 if prof_level == PROF.Untrained else pj_level
    #     prof_bonus: int = PROF_BONUSES[prof_level]
    #     extra_bonus: int = pj_skill["extra_bonus"]
    #     extra_descripcion: str = pj_skill["extra_descripcion"]
    #     skill_title = f"**{skill}** *({prof_level})*:`"

    #     extra_msg = (
    #         ""
    #         if (extra_bonus == 0 and extra_descripcion == "")
    #         else f"[Other: {signed_bonus(extra_bonus)}{f' ({extra_descripcion})' if extra_info else ''}])*"
    #     )

    #     pj_level = sh_pj.get_level_global()

    #     return await interaction.send(message)

    @set_lore.on_autocomplete("lore_subname")
    async def autocomplete_set_lore_subname(
        interaction: nextcord.Interaction, lore_subname: str
    ) -> Any:
        filtered_lores = []
        if lore_subname:
            if len(lore_subname) == 1:
                sh_skills._update_skill_data()
                print("Updated skill data once")
            filtered_lores = [
                a
                for a in sh_skills.get_all_existing_lore_subnames()
                if a.lower().startswith(lore_subname.lower())
            ]
        await interaction.response.send_autocomplete(filtered_lores)

    @lore.on_autocomplete("lore_subname")
    async def autocomplete_lore_subname(
        interaction: nextcord.Interaction, lore_subname: str
    ) -> Any:
        filtered_lores = []
        user_id: int = interaction.user.id

        if lore_subname:
            if len(lore_subname) == 1:
                sh_skills._update_skill_data()
                print("Updated skill data once")
            filtered_lores = [
                a
                for a in sh_skills.get_all_existing_lore_subnames(user_id)
                if a.lower().startswith(lore_subname.lower())
            ]
        await interaction.response.send_autocomplete(filtered_lores)


def setup(client: commands.Bot) -> None:
    client.add_cog(Skills(client))
