import sheetTest as sht



def try_pj_row(pj_id):
    row = sht.search_pj_row(pj_id)
    if row is None:
        error = f"El personaje de código {pj_id} no existe"
        print(error)
    return row

def money(pj_id:str, value:float, force = None):
    
    row = try_pj_row(pj_id)
    if row is None: return

    old_val = sht.money_value(row)
    old_total_value = float(old_val[5])

    if force is None:
        if -value > old_total_value:
            error = f'Restarle {-value} a tu dinero total {old_total_value} te dejaría en numeros negativos, si quieres hacerlo igual, repite el comando añadiendo "force" al final'
            print(error)
            return
    old_form = sht.money_formula(row)
    success = sht.change_money(row, old_form, value)
    if success:
        new_val = sht.money_value(row)
        message = f"Dinero de {sht.get_pj_name(row)} actualizado: {new_val[0]}pp, {new_val[1]}gp, {new_val[2]}ep, {new_val[3]}sp, {new_val[4]}cp, {new_val[5]} gp totales (antes tenía {old_total_value}gp)"
        print(message)
        return
    else:
        error = "Hubo un error actualizando tu dinero, si persiste preguntale a Pancho"
        print(error)
        return

def pay(pj_id:str, value:float):
    
    row = try_pj_row(pj_id)
    if row is None: return

    old_val = sht.money_value(row)
    old_total_value = float(old_val[5])

    if value > old_total_value:
        error = f'No puedes pagar {value}gp con {old_total_value}gp en ahorros. Si deseas quedar en dinero negativo, usa el comando $money añadiendo "force" al final'
        print(error)
        return
    old_form = sht.money_formula(row)
    success = sht.pay_money(row, old_form, old_val, value)
    if success:
        new_val = sht.money_value(row)
        message = f"Dinero de {sht.get_pj_name(row)} actualizado: {new_val[0]}pp, {new_val[1]}gp, {new_val[2]}ep, {new_val[3]}sp, {new_val[4]}cp, {new_val[5]} gp totales (antes tenía {old_total_value}gp)."
        print(message)
        return
    else:
        error = "Hubo un error actualizando tu dinero, si persiste preguntale a Pancho"
        print(error)
        return

def dt(pj_id:str, value:float, force = None):
    
    row = try_pj_row(pj_id)
    if row is None: return

    old_val = sht.dt_value(row)
    old_total_value = float(old_val)

    if force is None:
        if -value > old_total_value:
            error = f'Restarle {-value} a tu downtime total {old_total_value} te dejaría en numeros negativos, si quieres hacerlo igual, repite el comando añadiendo "force" al final'
            print(error)
            return
    old_form = sht.dt_formula(row)
    success = sht.update_dt(row, old_form, value)
    if success:
        new_val = old_total_value + value
        message = f"Downtime de {sht.get_pj_name(row)} actualizado: {old_total_value} -> {new_val}"
        print(message)
        return
    else:
        error = "Hubo un error actualizando tu dinero, si persiste preguntale a Pancho"
        print(error)
        return

