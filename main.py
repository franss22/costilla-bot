from math import ceil
from discord.ext import commands
import discord
import dndice
import dice
import os
import sqlite3
import datetime
import sheetTest as sht

bot = commands.Bot(command_prefix='$')


async def try_pj_row(ctx, pj_id):
    row = None
    try:
        row = sht.search_pj_row(pj_id)
    except:
        pass
    if row is None:
        error = f"El personaje de código {pj_id} no existe"
        await ctx.send(error)
    return row

@bot.command()
async def missioncomplete(ctx, pj_id:str, tier:int, type = None):
    #type: 0 = estrella, 1 = calavera
    if tier >10 or tier <1:
        await ctx.send(f"No existen misiones de tier {tier}")
        return
    row = await try_pj_row(ctx, pj_id)
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
        principado_message = f"Dado que eres tier {principado_tier} del Principado, se aumentó tu recompensa de DT en 1 y se duplicó tu recompensa de oro"
    success_xp = sht.add_experience(row, xp)
    # old_money_val = sht.money_value(row)
    old_money_form = sht.money_formula(row)
    success_gold = sht.change_money(row, old_money_form, gold)
    success_dt = sht.add_dt(row, dt)
    success_piety = sht.add_piety(row, 1)
    success_renown = sht.add_renown(row, 1)
    if not (success_dt and success_gold and success_piety and success_renown and success_xp):
        await ctx.send(f"Hubo un error actualizando tus stats:\n Actualizados: DT: {success_dt}, Gold: {success_gold}, Piedad: {success_piety}, Renombre: {success_renown}, XP: {success_xp}.")
        return
    message = f"""Misión de tier {tier} {"estrellas" if type == 0 else "calaveras"}: {sht.get_pj_name(row)}
    {xp}xp, {gold}gp, {dt}dt, 1 de piedad, 1 de renombre.
    Si haces el informe, ganas {int(xp*0.1)}xp extra ($xp {pj_id} {int(xp*0.1)})
    """+principado_message
    await ctx.send(message)


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

@bot.command()
async def reward(ctx, tier:int, type = None):
    type = 0 if type is None else 1
    await ctx.send(tier_message(tier, type))


@bot.command()
async def status(ctx, pj_id:str):
    row = await try_pj_row(ctx, pj_id)
    if row is None:
        return
    
    money_val = sht.money_value(row)
    dt_val = sht.dt_value(row)
    xp_val = sht.experience_value(row)
    ren_val = sht.renown_value(row)
    piety_val = sht.piety_value(row)
    name = sht.get_pj_name(row)

    message = f"""Resumen de {name}:
        {money_val[0]}pp, {money_val[1]}gp, {money_val[2]}ep, {money_val[3]}sp, {money_val[4]}cp, **{money_val[5]}gp** totales.
        XP: {xp_val}, DT: {dt_val}, Renombre: {ren_val}, Piedad: {piety_val}."""
    await ctx.send(message)
@bot.command()
async def state(ctx, pj_id:str):
    await status(ctx, pj_id)

@bot.command()
async def addmoney(ctx, pj_id: str, value: float, force=None):

    row = await try_pj_row(ctx, pj_id)
    if row is None:
        return

    old_val = sht.money_value(row)
    old_total_value = float(old_val[5])

    if force is None:
        if -value > old_total_value:
            error = f'Restarle {-value} a tu dinero total {old_total_value} te dejaría en numeros negativos, si quieres hacerlo igual, repite el comando añadiendo "force" al final'
            await ctx.send(error)
            return
    old_form = sht.money_formula(row)
    success = sht.change_money(row, old_form, value)
    if success:
        new_val = sht.money_value(row)
        message = f"Dinero de {sht.get_pj_name(row)} actualizado: {new_val[0]}pp, {new_val[1]}gp, {new_val[2]}ep, {new_val[3]}sp, {new_val[4]}cp, {new_val[5]} gp totales (antes tenía {old_total_value}gp)"
        await ctx.send(message)
        return
    else:
        error = "Hubo un error actualizando tu dinero, si persiste preguntale a Pancho"
        await ctx.send(error)
        return


@bot.command()
async def spend(ctx, pj_id: str, value: float):

    row = await try_pj_row(ctx, pj_id)
    if row is None:
        return

    old_val = sht.money_value(row)
    old_total_value = float(old_val[5])

    if value > old_total_value:
        error = f'No puedes pagar {value}gp con {old_total_value}gp en ahorros. Si deseas quedar en dinero negativo, usa el comando $money añadiendo "force" al final'
        await ctx.send(error)
        return
    old_form = sht.money_formula(row)
    success = sht.pay_money(row, old_form, old_val, value)
    if success:
        new_val = sht.money_value(row)
        message = f"Dinero de {sht.get_pj_name(row)} actualizado: {new_val[0]}pp, {new_val[1]}gp, {new_val[2]}ep, {new_val[3]}sp, {new_val[4]}cp, {new_val[5]} gp totales (antes tenía {old_total_value}gp)."
        await ctx.send(message)
        return
    else:
        error = "Hubo un error actualizando tu dinero, si persiste preguntale a Pancho"
        await ctx.send(error)
        return


@bot.command()
async def dt(ctx, pj_id: str, value: float, force=None):

    row = await try_pj_row(ctx, pj_id)
    if row is None:
        return

    old_val = sht.dt_value(row)
    old_total_value = float(old_val)

    if force is None:
        if -value > old_total_value:
            error = f'Restarle {-value} a tu downtime total {old_total_value} te dejaría en numeros negativos, si quieres hacerlo igual, repite el comando añadiendo "force" al final'
            await ctx.send(error)
            return
    old_form = sht.dt_formula(row)
    success = sht.update_dt(row, old_form, value)
    if success:
        new_val = old_total_value + value
        message = f"Downtime de {sht.get_pj_name(row)} actualizado: {old_total_value} -> {new_val}"
        await ctx.send(message)
        return
    else:
        error = "Hubo un error actualizando tu downtime, si persiste preguntale a Pancho"
        await ctx.send(error)
        return



def numToColumn(column_int):
    start_index = 1   #  it can start either at 0 or at 1
    letter = ''
    while column_int > 25 + start_index:   
        letter += chr(65 + int((column_int-start_index)/26) - 1)
        column_int = column_int - (int((column_int-start_index)/26))*26
    letter += chr(65 - start_index + (int(column_int)))
    return letter


@bot.command()
async def turnDT(ctx, pj_id: str, value: float, turn: int, force= None):
    row = await try_pj_row(ctx, pj_id)
    if row is None:
        print("No PJ")
        return
    col = numToColumn(40+turn)

    old_val = sht.get_single_val(col, row, "FORMATTED_VALUE")
    old_total_value = float(old_val)

    if force is None:
        if -value > old_total_value:
            error = f'Restarle {-value} a tu downtime total {old_total_value} te dejaría en numeros negativos, si quieres hacerlo igual, repite el comando añadiendo "force" al final'
            await ctx.send(error)
            return
    old_form = sht.get_single_val(col, row, "FORMULA")
    success = sht.update_single_val(col, row, old_form, value)
    if success:
        if turn < 3:
            range = [1, 5]
        else:
            range = [turn-3, turn +2]

        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=f'👨‍👨‍👧‍👧PJs!{range[0]}{row}:{range[1]}{row}', valueRenderOption="FORMATTED_VALUE").execute()
        print(resultS)

        new_val = old_total_value + value
        message = f"Downtime de {sht.get_pj_name(row)} actualizado: {old_total_value} -> {new_val}"
        await ctx.send(message)
        return
    else:
        error = "Hubo un error actualizando tu downtime, si persiste preguntale a Pancho"
        await ctx.send(error)
        return



    



@bot.command()
async def renombre(ctx, pj_id: str, value: int):

    row = await try_pj_row(ctx, pj_id)
    if row is None:
        return

    old_val = sht.renown_value(row)
    success = sht.add_renown(row, value)

    old_total_value = int(old_val)

    if success:
        new_val = old_total_value + value
        message = f"Renombre de {sht.get_pj_name(row)} actualizado: {old_total_value} -> {new_val}"
        await ctx.send(message)
        return
    else:
        error = "Hubo un error actualizando tu renombre, si persiste preguntale a Pancho"
        await ctx.send(error)
        return


@bot.command()
async def piedad(ctx, pj_id: str, value: int):

    row = await try_pj_row(ctx, pj_id)
    if row is None:
        return

    old_val = sht.piety_value(row)
    success = sht.add_piety(row, value)

    old_total_value = int(old_val)

    if success:
        new_val = old_total_value + value
        message = f"Piedad de {sht.get_pj_name(row)} actualizado: {old_total_value} -> {new_val}"
        await ctx.send(message)
        return
    else:
        error = "Hubo un error actualizando tu renombre, si persiste preguntale a Pancho"
        await ctx.send(error)
        return


@bot.command()
async def xp(ctx, pj_id: str, value: int):

    row = await try_pj_row(ctx, pj_id)
    if row is None:
        return

    old_val = sht.experience_value(row)
    success = sht.add_experience(row, value)

    old_total_value = int(old_val)

    if success:
        new_val = old_total_value + value
        message = f"XP de {sht.get_pj_name(row)} actualizado: {old_total_value} -> {new_val}"
        await ctx.send(message)
        return
    else:
        error = "Hubo un error actualizando tu XP, si persiste preguntale a Pancho"
        await ctx.send(error)
        return


@bot.command()
async def cleanmoney(ctx, pj_id: str):
    row = await try_pj_row(ctx, pj_id)
    if row is None:
        return
    success = sht.clean_money(row)
    if success:
        message = f"Dinero de {sht.get_pj_name(row)} limpiado"
        await ctx.send(message)
        return
    else:
        error = "Hubo un error actualizando tu dinero, si persiste preguntale a Pancho"
        await ctx.send(error)
        return


downtime_images = {
    "Trabajar un Oficio": "https://cdn.discordapp.com/attachments/763955185679597580/913226000014389298/unknown.png",
    "Comprar un Objeto Magico": "https://cdn.discordapp.com/attachments/763955185679597580/913225616835375114/unknown.png",
    "Irse de Juerga": "https://cdn.discordapp.com/attachments/763955185679597580/913220637458329600/unknown.png",
    "Construir un Objeto Mundano": "https://cdn.discordapp.com/attachments/763955185679597580/913220888911028234/unknown.png",
    "Crear un Plano de Objeto Magico": "https://cdn.discordapp.com/attachments/763955185679597580/913220985396797460/unknown.png",
    "Crear un Objeto Magico": "https://cdn.discordapp.com/attachments/763955185679597580/913221095224659988/unknown.png",
    "Fermentar Pociones": "https://cdn.discordapp.com/attachments/763955185679597580/913225171928768512/unknown.png",
    "Replicar Pocion": "https://cdn.discordapp.com/attachments/763955185679597580/913221315459182642/unknown.png",
    "Crimen": "https://cdn.discordapp.com/attachments/763955185679597580/913221558686863370/unknown.png",
    "Apostar": "https://cdn.discordapp.com/attachments/763955185679597580/913221964007624734/unknown.png",
    "Pelear por dinero": "https://cdn.discordapp.com/attachments/763955185679597580/913222037047222272/unknown.png",
    "Servicio Religioso": "https://cdn.discordapp.com/attachments/763955185679597580/913224919398088744/unknown.png",
    "Fijacion de Hechizo Preparado": "https://cdn.discordapp.com/attachments/763955185679597580/913222207038177340/unknown.png",
    "Aprender Hechizo": "https://cdn.discordapp.com/attachments/763955185679597580/913222207038177340/unknown.png",
    "Buscar Hechizo": "https://cdn.discordapp.com/attachments/763955185679597580/913222840730402846/unknown.png",
    "Investigar": "https://cdn.discordapp.com/attachments/763955185679597580/913223055545880617/unknown.png",
    "Entrenar": "https://cdn.discordapp.com/attachments/763955185679597580/913235361797378128/unknown.png",
    "Cuidado de Animales": "https://cdn.discordapp.com/attachments/763955185679597580/913223352255131668/unknown.png",
    "Rito Tribu Kaeglashita": "https://cdn.discordapp.com/attachments/763955185679597580/913223546715660348/unknown.png",
    "Construcción de un Edificio": "https://cdn.discordapp.com/attachments/763955185679597580/913223949419167825/unknown.png",
    "Llevar el Negocio": "https://cdn.discordapp.com/attachments/763955185679597580/913224128088145920/unknown.png",
    "Contruir una Casa": "https://cdn.discordapp.com/attachments/763955185679597580/913224444338647090/unknown.png",
    "Aportar a la Construccion de la Peninsula": "https://cdn.discordapp.com/attachments/763955185679597580/913224564698411068/unknown.png",
    "Reaprender Hechizos": "https://cdn.discordapp.com/attachments/763955185679597580/913224522394652682/unknown.png"
}


@bot.command()
async def reaprender(ctx):
    name = "Reaprender Hechizos"
    await genDowntime(ctx, name)


@bot.command()
async def pc(ctx):
    name = "Aportar a la Construccion de la Peninsula"
    await genDowntime(ctx, name)


@bot.command()
async def casa(ctx):
    name = "Contruir una Casa"
    await genDowntime(ctx, name)
    
@bot.command()
async def entrenar(ctx):
    name = "Entrenar"
    await genDowntime(ctx, name)

@bot.command()
async def negocio(ctx):
    name = "Llevar el Negocio"
    await genDowntime(ctx, name)


@bot.command()
async def construir(ctx):
    name = "Construcción de un Edificio"
    await genDowntime(ctx, name)


@bot.command()
async def rito(ctx):
    name = "Rito Tribu Kaeglashita"
    await genDowntime(ctx, name)


@bot.command()
async def cuidar(ctx):
    name = "Cuidado de Animales"
    await genDowntime(ctx, name)


@bot.command()
async def investigar(ctx):
    name = "Investigar"
    await genDowntime(ctx, name)


@bot.command()
async def buscar(ctx):
    name = "Buscar Hechizo"
    await genDowntime(ctx, name)


@bot.command()
async def aprender(ctx):
    name = "Aprender Hechizo"
    await genDowntime(ctx, name)


@bot.command()
async def fijar(ctx):
    name = "Fijacion de Hechizo Preparado"
    await genDowntime(ctx, name)


@bot.command()
async def rezar(ctx):
    name = "Servicio Religioso"
    await genDowntime(ctx, name)


@bot.command()
async def pelear(ctx):
    name = "Pelear por dinero"
    await genDowntime(ctx, name)


@bot.command()
async def apostar(ctx):
    name = "Apostar"
    await genDowntime(ctx, name)


@bot.command()
async def crimen(ctx):
    name = "Crimen"
    await genDowntime(ctx, name)


@bot.command()
async def replicar(ctx):
    name = "Replicar Pocion"
    await genDowntime(ctx, name)


@bot.command()
async def pociones(ctx):
    name = "Fermentar Pociones"
    await genDowntime(ctx, name)


@bot.command()
async def craftear(ctx):
    name = "Crear un Objeto Magico"
    await genDowntime(ctx, name)


@bot.command()
async def plano(ctx):
    name = "Crear un Plano de Objeto Magico"
    await genDowntime(ctx, name)


@bot.command()
async def fabricar(ctx):
    name = "Construir un Objeto Mundano"
    await genDowntime(ctx, name)


@bot.command()
async def juerga(ctx):
    name = "Irse de Juerga"
    await genDowntime(ctx, name)


@bot.command()
async def gacha(ctx):
    name = "Comprar un Objeto Magico"
    await genDowntime(ctx, name)


@bot.command()
async def trabajar(ctx):
    name = "Trabajar un Oficio"
    await genDowntime(ctx, name)


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))


@bot.command()
async def test(ctx, *args):
    await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))


@bot.command()
async def massroll(ctx, amt: int, atk: str, dmg: str = '0', ac: int = 0, short: str = ''):
    text = f'''```Massroll: {amt} rolls against AC {ac}'''
    textEnd = ''
    #emb = discord.Embed(title=f'Mass roll: {amt} rolls against AC {ac}')
    sumNum = 0
    sumCrits = 0
    try:
        dndice.basic(atk)
    except:
        ctx.send(f'{atk} is not valid roll syntax')
    try:
        dndice.basic(dmg)
    except:
        ctx.send(f'{dmg} is not valid roll syntax')

    for x in range(amt):
        atkRoll = dndice.basic(atk)
        dmgRoll = dndice.basic(dmg)

        if atkRoll == dice.roll_max(atk):
            critical = ', Critical!'
            sumCrits += 1
            dmgRoll = dndice.basic(dmg.replace('d', 'dc'))
        else:
            critical = ''

        if dmg != '0':
            textEnd += f"Attack n°{x}: {atkRoll}, damage: {dmgRoll}{critical}\n"
            #emb.add_field(name=f'Attack {x}', value=f'{critical}{atkRoll}, damage: {dmgRoll}')
        else:
            textEnd += f"Attack {x}: {critical}{atkRoll}\n"
            #emb.add_field(name=f'Attack {x}', value=f'{critical}{atkRoll}')

        if (atkRoll >= ac or critical == 'Critical Attack!: '):
            sumNum += dmgRoll
    text += f'''\n Sum of the Damage: {sumNum} damage'''
    text += f"\n Amount of critical attacks: {sumCrits}\n\n"
    if short == "short":
        pass
    elif (len(text)+len(textEnd) <= 1997):
        text += textEnd
    else:
        text += "Text is too long, detail doesnt fit."
    #emb.add_field(name=f'Sum of the Damage', value=f'{sumNum} damage')

    text += "```"
    await ctx.send(text)


@bot.command()
async def downtime(ctx):
    emb = discord.Embed(title='Actividades de Downtime:')
    text = '''
    Trabajar un Oficio: $trabajar
    Comprar un Objeto Magico: $gacha
    Irse de Juerga: $juerga
    Construir un Objeto Mundano: $fabricar
    Crear un Plano de Objeto Magico: $plano
    Crear un Objeto Magico: $craftear
    Replicar Pocion: $replicar
    Crimen: $crimen
    Apostar: $apostar
    Pelear por dinero: $pelear
    Servicio Religioso: $rezar
    Fijacion de Hechizo Preparado: $fijar
    Investigar: $investigar
    Cuidado de Animales: $cuidar
    Rito Tribu Kaeglashita: $rito
    Construcción de un Edificio: $construir
    Llevar el Negocio: $negocio
    Contruir una Casa: $casa
    Aportar a la Construccion de la Peninsula: $pc
    Reaprender Hechizos: $reaprender
    '''
    emb.add_field(name='Comandos', value=text)
    await ctx.send(embed=emb)


async def genDowntime(ctx, name):
    emb = discord.Embed(title=f'Downtime Activities: {name}')
    emb.set_image(url=downtime_images[name])
    await ctx.send(embed=emb)


def saveFish(fishName: str, fisherName: str):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("insert into fish(pez, pescador) values (?, ?)",
                (fishName, fisherName))
    con.commit()
    con.close()


@bot.command()
async def personajePescaPez(ctx, nombrePJ: str, nombrePez: str):
    saveFish(nombrePez, nombrePJ)
    await ctx.send(f"`{nombrePJ} pescó un {nombrePez}!`")


@bot.command()
async def tablonPesca(ctx, amt: int = 1):
    if amt < 1:
        await ctx.senc("la página debe ser un entero partiendo en 1")
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    fish = cur.execute("select * from fish").fetchall()
    con.close()
    msg = "```**Tablón de Pesca:**\n"
    totalRow = len(fish)
    pageTotal = ceil(totalRow / 20)

    for row in fish[20*(amt-1):20*amt]:
        id = row[0]
        fisherman = row[2]
        fishName = row[1]
        add = f"{id}-{fisherman} pescó un {fishName}\n"
        if (len(msg) < (2000-len(add)-3)):
            msg += add
        else:
            await ctx.send("La cantidad de pescado en el anuncio sobrepasa el limite de caracteres de Discord, diganel al Pancho que arregle el bot xd.")
            break
    msg += f"\n Pag {amt} de {pageTotal}```"
    await ctx.send(msg)


@bot.command()
async def deletePez(ctx, id: int):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("DELETE FROM fish WHERE id= ?", (id,))
    con.commit()
    con.close()
    await ctx.send(f"Elemento id {id} eliminado.")

# @bot.command()
# async def help(ctx):
#     emb = discord.Embed(title= 'Help')
#     st = '''$downtime: comandos de downtime
#     $personajePescaPez: pescar
#     $tablonPesca:
#     '''
#     emb.add_field("Commands", st, inline=True)
#     await ctx.send(emb)
token = os.environ.get('TOKEN')
bot.run(token)
