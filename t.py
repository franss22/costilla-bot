from PF2eData import ABILITIES, PROF, PROF_BONUSES, SKILLS, Ability


def signed_bonus(bonus: int) -> str:
    return f"+{bonus}" if bonus >= 0 else str(bonus)


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
        skill_title = f"**{skill_name}** *(untrained?)*:"
        submsg: str = (
            f"\n- {skill_title.ljust(justify)} "
            f"{bonus_str} "
            f"([{mod_type.name}: {bonus_str}])"
        )
    else:
        prof_level: str = pj_skill["prof_level"]
        level_bonus: int = 0 if prof_level == PROF.Untrained else pj_level
        prof_bonus: int = PROF_BONUSES[prof_level]
        extra_bonus: int = pj_skill["extra_bonus"]
        extra_descripcion: str = pj_skill["extra_descripcion"]
        skill_title = f"**{skill_name}** *({prof_level})*:"
        submsg: str = (
            f"\n- {skill_title.ljust(justify)} "
            f'{f"{signed_bonus(prof_bonus+pj_mod_bonus+extra_bonus+level_bonus)} ".ljust(4)}'
            f"*([{mod_type.name}: {signed_bonus(pj_mod_bonus)}]"
            f"[{prof_level}: {prof_bonus+level_bonus}]"
            f"[Other: {signed_bonus(extra_bonus)}{f' ({extra_descripcion})' if extra_info else ''}])*"
        )
    return submsg


pj_mod_bonus = 1
pj_level = 1
mod_type = ABILITIES.Str
skill_name = "Acrobatics"
pj_skill = None
extra_info = False
justify = 40

# for skill, mod in SKILLS:

#     print(
#         skill_description(
#             pj_mod_bonus, pj_level, mod, skill, pj_skill, extra_info, justify
#         )
#     )


skills = {
    "Medicine": {
        "prof_level": "Trained",
        "extra_bonus": 0,
        "extra_descripcion": "",
        "row": 2,
    }
}
for name, val in skills:
    print(name)
