import sheetTest as sht


print(sht.check_principado_level(77))

def mission_reward(tier, pj_id, type = None):
    #type: 0 = estrella, 1 = calavera
    if tier >10 or tier <1:
        print(f"No existen misiones de tier {tier}")
        return
    row = sht.search_pj_row(pj_id)
    if row is None:
        return
    type = 0 if type is None else 1
    xp_gold, dt = sht.get_reward_info(tier)
    xp = int(xp_gold[type])
    gold = float(xp_gold[3+type])
    dt = float(dt)
    principado_tier = sht.check_principado_level(row)
    principado_message = ""
    if principado_tier >= 1:
        dt += 1
        principado_message = "Dado que eres tier 1 del Principado, se aumentó tu recompensa de DT en 1"
    if principado_tier >= 2:
        gold *= 2
        principado_message = f"Dado que eres tier {principado_tier} del Principado, se aumentó tu recompensa de DT en 1 y se duplicó tu reompensa de oro"
    success_xp = sht.add_experience(row, xp)
    # old_money_val = sht.money_value(row)
    old_money_form = sht.money_formula(row)
    success_gold = sht.change_money(row, old_money_form, gold)
    success_dt = sht.add_dt(row, dt)
    success_piety = sht.add_piety(row, 1)
    success_renown = sht.add_renown(row, 1)
    if not (success_dt and success_gold and success_piety and success_renown and success_xp):
        print(f"Hubo un error actualizando tus stats:\n Actualizados: DT: {success_dt}, Gold: {success_gold}, Piedad: {success_piety}, Renombre: {success_renown}, XP: {success_xp}.")
        return
    message = f"""Misión de tier {tier} {"estrellas" if type == 0 else "calaveras"}: {sht.get_pj_name(row)}
    {xp}xp, {gold}gp, {dt}dt, 1 de piedad, 1 de renombre.
    Si haces el informe, ganas {int(xp*0.1)}xp extra ($xp {pj_id} {int(xp*0.1)})
    """+principado_message
    print(message)


mission_reward(3, "test")
mission_reward(3, "test", 1)


    
    






def tier_message(tier:int, type:int):
    #type: 0 = estrella, 1 = calavera
    if tier >10 or tier <1:
        return f"No existen misiones de tier {tier}"
    else:
        xp_gold, dt = sht.get_reward_info(tier)
        xp = int(xp_gold[type])
        gold = float(xp_gold[3+type])
        dt = float(dt)
        message = f"""La recompensa de una misión de tier {tier} {"estrellas" if type == 0 else "calaveras"} es:
        {xp}xp, {gold}gp, {dt}dt, 1 de piedad, 1 de renombre. 
        El que hace el informe gana {int(xp*1.1)}xp.
        La gente del principado, dependiendo de su renombre, gana {dt+1}dt y {gold*2}gp."""
        return message