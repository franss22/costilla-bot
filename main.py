from math import ceil
from msilib.schema import tables
from nextcord.ext import commands
from nextcord.ui import Button, View
from nextcord import ButtonStyle
import dndice
import dice
import sqlite3
import random
from downtime_activities import downtimeCog

from varenv import getVar

import SheetControl as Sheet
from SheetControl import COL, get_pj_row
from utils import FACTION
import utils


from functools import wraps
import nextcord 
intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


def pj_wrap(func):
    @wraps(func)
    async def wrapped_func(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except Sheet.CharacterNameError as e:
            ctx = args[0]
            await ctx.send(str(e))
    return wrapped_func


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))
    print("Generating downtime commands")
    try:
        bot.add_cog(downtimeCog(bot))
        print("Finished generating downtime commands")
    except Exception as e:
        print(e)


@bot.command()
@commands.has_role("Mod")
async def massrenombre(ctx, faccion, amt):
    await ctx.send(f"Aumentando en {amt} el renombre de todos los PJs de la facción: {faccion}")
    return


@bot.command()
@pj_wrap
async def missioncomplete(ctx, pj_id: str, tier: int, type=None):
    # type 0 -> estrella, 1 -> calavera
    if tier > 10 or tier < 1:
        await ctx.send(f"No existen misiones de tier {tier}")
        return
    row = get_pj_row(pj_id)
    type = 0 if type is None else 1

    xp_add, gold_add, dt_add = Sheet.get_reward_info(tier, skull=(type == 1))

    renown, faction = Sheet.get_batch_data(
        row, [COL.renown, COL.renown_faction])

    principado_tier = utils.renown_tier(
        renown) if faction == FACTION.principado_short else 0

    principado_message = ""
    if principado_tier >= 1:
        dt_add += 1
        principado_message = "Dado que eres tier 1 del Principado, se aumentó tu recompensa de DT en 1"
    if principado_tier >= 2:
        gold_add *= 2
        principado_message = f"Dado que eres tier {principado_tier} del Principado, se aumentó tu recompensa de DT en 1 y se duplicó tu recompensa de oro"

    Sheet.add_money(row, gold_add)

    old_data = Sheet.edit_batch_data(
        row, [COL.xp, COL.downtime, COL.piety, COL.renown, COL.money_total], [xp_add, dt_add, 1, 1, 0])

    message = f"""Misión de tier {tier} {"estrellas" if type == 0 else "calaveras"}: {Sheet.get_pj_data(row, COL.name)}
    {xp_add}xp, {gold_add}gp, {dt_add}dt, 1 de piedad, 1 de renombre.
    Si haces el informe, ganas {int(xp_add*0.1)}xp extra ($xp {pj_id} {int(xp_add*0.1)})
    """+principado_message
    await ctx.send(message)


@bot.command()
async def reward(ctx, tier: int, type=None):
    type = 0 if type is None else 1

    def tier_message(tier: int, type: int):
        # type 0 = estrella, 1 = calavera
        if tier > 10 or tier < 1:
            return f"No existen misiones de tier {tier}"
        else:
            xp, gold, dt = Sheet.get_reward_info(tier, skull=(type == 1))
            message = f"""La recompensa de una misión de tier {tier} {"estrellas" if type == 0 else "calaveras"} es:
            {xp}xp, {gold}gp, {dt}dt, 1 de piedad, 1 de renombre. 
            El que hace el informe gana {int(xp*1.1)}xp.
            La gente del principado, dependiendo de su renombre, gana {dt+1}dt y {gold*2}gp."""
            return message
    await ctx.send(tier_message(tier, type))


@bot.command()
@pj_wrap
async def status(ctx, pj_id: str):
    row = Sheet.get_pj_row(pj_id)

    batch = Sheet.get_batch_data(row, [COL.name, COL.money_pp, COL.money_gp, COL.money_ep, COL.money_sp,
                                 COL.money_cp, COL.money_total, COL.downtime, COL.xp, COL.renown, COL.piety, COL.piety_god])
    name, pp, gp, ep, sp, cp, m_total, dt, xp, ren, piety, god = batch

    message = f"""Resumen de {name}:
        {pp}pp, {gp}gp, {ep}ep, {sp}sp, {cp}cp, **{m_total}gp** totales.
        XP: {xp}, DT: {dt}, Renombre: {ren}, Piedad: {piety} con {god}."""
    await ctx.send(message)


@bot.command()
async def state(ctx, pj_id: str):
    await status(ctx, pj_id)


@bot.command()
@pj_wrap
async def addmoney(ctx, pj_id: str, value: float):

    row = Sheet.get_pj_row(pj_id)

    old_total = Sheet.get_pj_data(row, COL.money_total)

    Sheet.add_money(row, value)

    try:
        new_val = Sheet.get_batch_data(
            row, [COL.money_pp, COL.money_gp, COL.money_ep, COL.money_sp, COL.money_cp, COL.money_total])
        message = f"Dinero de {Sheet.get_pj_data(row, COL.name)} actualizado: {new_val[0]}pp, {new_val[1]}gp, {new_val[2]}ep, {new_val[3]}sp, {new_val[4]}cp, {new_val[5]} gp totales (antes tenía {old_total}gp)"
        await ctx.send(message)

    except Exception as e:
        error = "Hubo un error actualizando tu dinero, si persiste preguntale a Pancho"
        await ctx.send(error)



@bot.command()
@pj_wrap
async def spend(ctx, pj_id: str, value: float):
    row = Sheet.get_pj_row(pj_id)
    old_total = Sheet.get_pj_data(row, COL.money_total)

    success = Sheet.pay(row, value)

    if success is True:
        new_val = Sheet.get_batch_data(
            row, [COL.money_pp, COL.money_gp, COL.money_ep, COL.money_sp, COL.money_cp, COL.money_total])
        message = f"Dinero de {Sheet.get_pj_data(row, COL.name)} actualizado: {new_val[0]}pp, {new_val[1]}gp, {new_val[2]}ep, {new_val[3]}sp, {new_val[4]}cp, {new_val[5]} gp totales (antes tenía {old_total}gp)."
        await ctx.send(message)
    else:
        await ctx.send(success)


@pj_wrap
async def change_single_value(ctx, pj_id: str, value: float, val_name: str, col: str):

    name, prev_val, row = Sheet.get_pj_data_with_name(pj_id, col)
    cell = Sheet.simple_cell(row, col)

    try:
        Sheet.edit_data(cell, value)
        await ctx.send(f"`{val_name} de {name} actualizado: {prev_val} -> {float(prev_val)+value}`")
    except Exception as e:
        await ctx.send(f"`Hubo un error actualizando el {val_name.lower()} de {name}: Error Detail: {str(e)}`")


@bot.command()
async def dt(ctx, pj_id: str, value: float):
    val_name = "Downtime"
    col = COL.downtime
    await change_single_value(ctx, pj_id, value, val_name, col)


@bot.command()
async def renombre(ctx, pj_id: str, value: float):
    val_name = "Renombre"
    col = COL.renown
    await change_single_value(ctx, pj_id, value, val_name, col)


@bot.command()
async def piedad(ctx, pj_id: str, value: int):
    val_name = "Piedad"
    col = COL.piety
    await change_single_value(ctx, pj_id, value, val_name, col)


@bot.command()
async def xp(ctx, pj_id: str, value: int):
    val_name = "XP"
    col = COL.xp
    await change_single_value(ctx, pj_id, value, val_name, col)


@bot.command()
@pj_wrap
async def cleanmoney(ctx, pj_id: str):
    row = Sheet.get_pj_row(pj_id)
    edit_range = f"{Sheet.PJ_SHEET}{COL.money_pp}{row}:{COL.money_cp}{row}"
    try:
        Sheet.edit_data(
            edit_range, 0, edit_func=Sheet.clean_formula, formula=False, single=False)
        message = f"Dinero de {Sheet.get_pj_data(row, COL.name)} limpiado"
        await ctx.send(message)
    except Exception as e:
        error = f"Hubo un error actualizando tu dinero, si persiste preguntale a Pancho. Detalle del error: {str(e)}"
        await ctx.send(error)


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

import gachaControl as Gacha
from gachaControl import GACHACOL

@bot.command()
@pj_wrap
async def gacharoll(ctx:commands.Context, pj_id:str, pers_check:int):
    
    user = ctx.author
    row = Sheet.get_pj_row(pj_id)
    money, dt = Sheet.get_batch_data(row, [COL.money_total, COL.downtime])
    if float(money)<100 or float(dt) < 1:
        return await ctx.send("No tienes suficiente oro o dt praa el coste base de la subasta.")
    
    descuento, complicacion, bono = Gacha.gacha_info()
    
    total_roll= pers_check+int(bono)
    
    controller = Gacha.GachaController(descuento, complicacion, row, user)
    
    rolled_table = controller.DMG_table_options(total_roll)
    
    view = View()
    
    for table in controller.table_options:
        b = Button(label=table)
        b.callback = button_choose_table(controller, table)
        view.add_item(b)
        
    msg = f'''**Casa de Subastas**
Con una tirada de {total_roll}, puedes acceder a la tabla {rolled_table}.
Puedes elegir una tabla menor, tirando 1d4 por cada tabla que bajes. La cantidad de objetos para elegir es el mayor d4 entre los que tiraste.
Tienes {money}gp disponibles.

*Elige el botón con la tabla en la que quieres tirar.*
    '''
    await ctx.send(msg, view=view)        

def button_choose_table(controller:Gacha.GachaController, chosen_table:str):
    async def callback(interaction):
        if interaction.user != controller.user:
            return
        
        d4_amount = controller.d4_amount(chosen_table)
        item_amount = dndice.basic(f'{d4_amount}d4h1')
        controller.roll_items(item_amount, chosen_table)
        msg = f'''**Casa de Subastas**
Lanzando {d4_amount}d4, obtienes {item_amount} ofertas de objeto de la tabla {chosen_table}:
```{controller.items_for_sale_message()}```

*Apreta los botones de los items que desees comprar. Azul si es un item normal, verde si es consumible.*
'''
        view = View()
        for item in controller.items_for_sale():
            butt_norm = Button(label=item['letter'], style=ButtonStyle.blurple, row=0, disabled=item['bought'])
            butt_cons = Button(label=item['letter'], style=ButtonStyle.green,   row=1, disabled=item['bought'])
            
            butt_norm.callback = button_choose_item(controller, item, False, chosen_table, item_amount, d4_amount, "")
            butt_cons.callback = button_choose_item(controller, item, True, chosen_table, item_amount, d4_amount, "")

            view.add_item(butt_norm)
            view.add_item(butt_cons)
        await interaction.response.edit_message(content=msg, view=view)
    return callback

def button_choose_item(controller:Gacha.GachaController, chosen_item:dict, consumable:bool, chosen_table:str, item_amount:int, d4_amount:int, logs:str):
    async def callback(interaction:nextcord.Interaction):
        if interaction.user != controller.user:
            return
        
        await interaction.response.defer()
        
        
        activity = logs + controller.buy(chosen_item, consumable)
        
        
        msg = f'''**Casa de Subastas**
Lanzando {d4_amount}d4, obtienes {item_amount} ofertas de objeto de la tabla {chosen_table}:
```{controller.items_for_sale_message()}```

*Apreta los botones de los items que desees comprar. Azul si es un item normal, verde si es consumible.*
{activity}
'''
        view = View(timeout=180)
        for item in controller.items_for_sale():
            butt_norm = Button(label=item['letter'], style=ButtonStyle.blurple, row=0, disabled=item['bought'])
            butt_cons = Button(label=item['letter'], style=ButtonStyle.green,   row=1, disabled=item['bought'])
            
            butt_norm.callback = button_choose_item(controller, item, False, chosen_table, item_amount, d4_amount, activity)
            butt_cons.callback = button_choose_item(controller, item, True, chosen_table, item_amount, d4_amount, activity)
            
            view.add_item(butt_norm)
            view.add_item(butt_cons)
        
        await interaction.followup.edit_message(content=msg, view=view, message_id=interaction.message.id)
    return callback
        
@bot.command()
async def playmission(ctx, pj:str):
    if pj == "Samsir":
        await ctx.send("Samsir murió.")
    else:
        await ctx.send(f"{pj} ganó.")



token = getVar("TOKEN")
bot.run(token)
