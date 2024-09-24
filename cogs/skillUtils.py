import nextcord
from PF2eData import PROF, PROF_BONUSES, Ability
import SheetControlSkills as sh_skills
from icecream import ic

ALTERNATE = True

def nat_20_1_message(dice_result: int):
    if dice_result == 20:
        return "**Nat 20!** "
    elif dice_result == 1:
        return "**Nat 1!** "
    else:
        return ""


def skill_description(
    pj_mod_bonus: int,
    pj_level: int,
    mod_type: Ability,
    skill_name: str,
    pj_skill: None | dict[str, str | int],
    extra_info: bool,
) -> str:
    global ALTERNATE
    ALTERNATE = not ALTERNATE
    just_char = "·" if ALTERNATE else " "
    if pj_skill is None:
        skill_title = f"{skill_name} (Untrained?):"
        submsg: str = (
            f"\n- {skill_title.ljust(28, just_char)} "
            f"{pj_mod_bonus:+} "
            f"([{mod_type.name}: {pj_mod_bonus:+}])"
        )
    else:
        prof_level: str = pj_skill["prof_level"]
        level_bonus: int = 0 if prof_level == PROF.Untrained else pj_level
        prof_bonus: int = PROF_BONUSES[prof_level]
        extra_bonus: int = pj_skill["extra_bonus"]
        extra_descripcion: str = pj_skill["extra_descripcion"]
        skill_title = f"{skill_name} ({prof_level})"

        extra_msg = (
            ""
            if (extra_bonus == 0 and extra_descripcion == "")
            else f"[Other: {extra_bonus:+}{f' ({extra_descripcion})' if extra_info else ''}]"
        )
        submsg: str = (
            f"\n- {skill_title.ljust(28, just_char)} "
            f'{f"{(prof_bonus + pj_mod_bonus + extra_bonus + level_bonus):+} ".ljust(4)}'
            f"([{mod_type.name}: {pj_mod_bonus:+}]"
            f"[{f'{prof_level}:'.ljust(10)} {f'{(prof_bonus + level_bonus):+}]'.rjust(4)}"
            f"{extra_msg})"
        )
    return submsg


def ability_param(ability_name: str):
    ability_name = ability_name.lower()
    return nextcord.SlashOption(
        name=ability_name,
        description=f"El nivel de proficiencia de {ability_name.capitalize()}",
        required=True,
        choices=PROF.profs_list,
    )


def filter_lores(lore_subname: str, user_id: int | None) -> list[str]:
    ic(lore_subname)
    if len(lore_subname) == 0:
        sh_skills._update_skill_data()
        ic("Updated skill data once")
    filtered_lores = sh_skills.get_all_existing_lore_subnames(user_id)
    filtered_lores = [
        a for a in filtered_lores if a.lower().startswith(lore_subname.lower())
    ]
    return filtered_lores
