import nextcord
from nextcord.ext import commands
from varenv import getVar
import SheetControl as sh
from SheetControl import PJ_COL, REP_COL, gets_pj_data, gets_rep_data
from PF2eData import *
import utils
import json
import dndice
import logging

logging.basicConfig(level=logging.INFO)

CRI_GUILD_ID = int(getVar("GUILD_ID"))
PANCHO_ID = getVar("PANCHO_ID")
BOT_TOKEN = getVar("TOKEN")

bot = commands.Bot()
with open("Ancestries.json") as f:
    HERITAGES : dict[str, str]= json.load(f)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')



class HeritageDropdown(nextcord.ui.Select):
    Update_func = None
    def __init__(self, ancestry:str, update_func):
        heritages = HERITAGES[ancestry]
        self.Update_func = update_func
        options = [nextcord.SelectOption(label=h) for h in heritages]
        options += [nextcord.SelectOption(label=h, description="(Heritage versátil)") for h in HERITAGES["Versatile"]]
        super().__init__(placeholder="Opciones de heritage", min_values=1, max_values=1, options=options)

    async def callback(self, interaction:nextcord.Interaction):
        selected = self.values[0]
        self.view.stop()
        await self.Update_func(interaction, selected)

class RegisterDropdownView(nextcord.ui.View):
    def __init__(self, heritage_dropdown:HeritageDropdown):
        super().__init__()
        self.add_item(heritage_dropdown)

@bot.slash_command(description="Registra un nuevo personaje de Megamarch.", guild_ids=[CRI_GUILD_ID])
@gets_pj_data
async def register(interaction: nextcord.Interaction, nombre_pj:str, nombre_jugador:str,
                   clase:str = nextcord.SlashOption(name="clase", description="La clase de tu personaje", required=True, choices=CLASSES), 
                   ascendencia:str = nextcord.SlashOption(name="ascendencia", description="La ascendencia de tu personaje (escribe para el autocomplete)", required=True), 
                   religion:str = nextcord.SlashOption(name="religión", description="La religión de tu personaje", required=True, choices=RELIGIONS)):
    # Conseguir el ID del usuario
    user_id:int = interaction.user.id
    print(user_id)
    # Revisar que no tenga otro PJ
    already_has_character = True
    try:
        pj_row = sh.get_pj_row(user_id)
    except sh.CharacterNotFoundError:
        already_has_character = False
    if already_has_character:
        return await interaction.send(f"Ya tienes un personaje en la fila {pj_row}, muevelo al cementario para registrar uno nuevo.")
    ascendencia = ascendencia.capitalize()
    if ascendencia not in ANCESTRIES:
        return await interaction.send(f"'{ascendencia}' no es una ascendencia válida.")
    


    # Generar stats base (0 de dt, 15 de gp)
    #[nombre, id, jugador, clase, Arquetipos, ascendencia, heritage, dt, pp, gp, sp, cp, total, lenguajes, religión]
    async def update_func(interaction:nextcord.Interaction, selected_heritage:str):
        values = [nombre_pj, str(user_id), nombre_jugador, clase, "", ascendencia, selected_heritage, 0, 0, 15, 0, 0]
        pj_row = sh.first_empty_PJ_row()
        sh.update_range_PJ([values], f"{PJ_COL.Name}{pj_row}:{PJ_COL.Money_cp}{pj_row}")
        sh.update_range_PJ([[religion]], f"{PJ_COL.Religion}{pj_row}")
        await interaction.send(f"Registrado {nombre_pj} en la fila {pj_row}")
    heritage_dropdown = HeritageDropdown(ascendencia, update_func)

    view = RegisterDropdownView(heritage_dropdown)
    await interaction.send("Selecciona un heritage para tu personaje", view=view)


@register.on_autocomplete("ascendencia")
async def autocomplete_ancestry(interaction: nextcord.Interaction, ancestry: str):
    filtered_ancestries = []
    if ancestry:
        filtered_ancestries = [a for a in ANCESTRIES if a.lower().startswith(ancestry.lower())]
    await interaction.response.send_autocomplete(filtered_ancestries)

@bot.slash_command(description="Entrega la info de tu personaje", guild_ids=[CRI_GUILD_ID])
@gets_pj_data
async def status(interaction: nextcord.Interaction, user:nextcord.Member = None):
    user_id:int = interaction.user.id if user is None else user.id
    try:
        pj_row = sh.get_pj_row(user_id)
    except sh.CharacterNotFoundError:
        return await interaction.send("No se encontró un personaje con ID de discord correspondiente")
    data = sh.get_pj_full(pj_row)
    print(data)
    Name, Id, Player, Class, Arquetypes, Ancestry, Heritage, Dt, pp, gp, sp, cp, total, languages, religion = data
    Dt = int(Dt)
    message = f"""# Status de {Name}
- Jugador: {Player}
- Clase: {Class}{", " if Arquetypes else ""}{Arquetypes}
- Ascendencia: {Ancestry}, {Heritage}
- Dinero: {pp}pp, {gp}gp, {sp}sp, {cp}cp, **Total: {total}gp**
- Downtime: {Dt//7} semanas y { Dt%7} dias ({Dt} dias)
"""
    return await interaction.send(message)

@bot.slash_command(description="Cambia el Downtime de tu personaje", guild_ids=[CRI_GUILD_ID])
@gets_pj_data
async def dt(interaction: nextcord.Interaction, amount:int):
    user_id:int = interaction.user.id
    try:
        pj_row = sh.get_pj_row(user_id)
        pj_name = sh.get_pj_data(pj_row, PJ_COL.Name)
    except sh.CharacterNotFoundError:
        return await interaction.send("No se encontró un personaje con ID de discord correspondiente")


    pj_dt = sh.get_pj_data(pj_row, PJ_COL.Downtime)

    if pj_dt+amount<0:
        return await interaction.send("No tienes suficiente downtime para esta transacción")
    
    new_total = pj_dt+amount

    sh.update_pj_data_cell(pj_row, PJ_COL.Downtime, [[new_total]])

    return await interaction.send(f"{pj_name} {"gana" if amount>0 else "gasta"} {amount} dias de downtime. Ahora tiene {new_total//7} semanas y { new_total%7} dias ({new_total} dias)")

@bot.slash_command(description="Resta dinero de tu cuenta. Puedes transferir a otra persona.", guild_ids=[CRI_GUILD_ID])
@gets_pj_data
async def pay(interaction: nextcord.Interaction, 
              amount: float = nextcord.SlashOption("money-gp", "Dinero restado a tu cuenta, en gp", True, min_value=0), 
              transfertarget:nextcord.Member= nextcord.SlashOption("target-trasnferencia", "Usuario al que se le transfiere el dinero", False, default=None)):
    user_id:int = interaction.user.id
    target_id:int = transfertarget.id if transfertarget is not None else None
    try:
        pj_row = sh.get_pj_row(user_id)
        pj_name = sh.get_pj_data(pj_row, PJ_COL.Name)
        target_pj_row = sh.get_pj_row(target_id) if transfertarget is not None else None
        target_pj_name = sh.get_pj_data(target_pj_row, PJ_COL.Name) if transfertarget is not None else None
    except sh.CharacterNotFoundError:
        return await interaction.send("No se encontró un personaje con ID de discord correspondiente")
    if amount<0:
        return await interaction.send("Debes pagar una cantidad positiva de dinero")

    pj_coins = sh.get_pj_coins(pj_row)
    pp, gp, sp, cp, total = pj_coins
    if total-amount<0:
        return await interaction.send("No tienes suficiente dinero para esta transacción")
    
    new_total = total-amount
    new_coins = utils.gp_to_coin_list(new_total)
    pp, gp, sp, cp = new_coins
    sh.update_pj_coins(pj_row, [new_coins])

    if transfertarget is not None:
        target_coins = sh.get_pj_coins(target_pj_row)
        pp, gp, sp, cp, total = target_coins
        new_total_target = total+amount
        new_coins = utils.gp_to_coin_list(new_total_target)
        sh.update_pj_coins(target_pj_row, [new_coins])
        return await interaction.send(f"{pj_name} le transfiere {amount}gp a {target_pj_name}. \n{pj_name} queda con {new_total:.2f}gp, y {target_pj_name} queda con {new_total_target:.2f}gp.")
    return await interaction.send(f"{pj_name} paga {amount}gp. Ahora tiene {pp}pp, {gp}gp, {sp}sp, {cp}cp, **Total: {new_total:.2f}gp**")

@bot.slash_command(description="Suma dinero a tu cuenta.", guild_ids=[CRI_GUILD_ID])
@gets_pj_data
async def addmoney(interaction: nextcord.Interaction, 
                   amount: float = nextcord.SlashOption("money-gp", "Dinero añadido a tu cuenta, en gp", True, min_value=0), 
                   target:nextcord.Member= nextcord.SlashOption("target", "Usuario al que se le añade el dinero", False, default=None)):
    user_id:int = target.id if target is not None else interaction.user.id
    try:
        pj_row = sh.get_pj_row(user_id)
        pj_name = sh.get_pj_data(pj_row, PJ_COL.Name)
    except sh.CharacterNotFoundError:
        return await interaction.send("No se encontró un personaje con ID de discord correspondiente")
    if amount<0:
        return await interaction.send("Debes ganar una cantidad positiva de dinero")

    pj_coins = sh.get_pj_coins(pj_row)
    pp, gp, sp, cp, total = pj_coins
    
    new_total = total + amount
    new_coins = utils.gp_to_coin_list(new_total)
    pp, gp, sp, cp = new_coins
    sh.update_pj_coins(pj_row, [new_coins])

    return await interaction.send(f"{pj_name} obtiene {amount}gp. Ahora tiene {pp}pp, {gp}gp, {sp}sp, {cp}cp, **Total: {new_total:.2f}gp**")


@bot.slash_command(description="Calcula las ganancias de Earn Income", guild_ids=[CRI_GUILD_ID])
async def earnincome(interaction: nextcord.Interaction,
                     taskLevel:int = nextcord.SlashOption("task-level", "Nivel del trabajo", True, min_value=0, max_value=20),
                     profLevel:str = nextcord.SlashOption("proficiency-level", "Nivel de proficiencia de la skill usada", True, choices=["Trained", "Expert", "Master", "Legendary"]),
                     downtimeUsed:int = nextcord.SlashOption("downtime-used", "Dias de downtime usados en trabajar", True, min_value=1, default=1),
                     checkBonus:int = nextcord.SlashOption("check-bonus", "Bono al check utilizado", True),
                     dcChange:int = nextcord.SlashOption("dc-adjustment", "Cambios al DC impuestos por el DM", False, default=0),
                     ):
    dice = dndice.basic("1d20")
    check_value = dice+checkBonus
    DC = EARN_INCOME[taskLevel][0]+dcChange
    check_result = utils.check_results(DC, check_value, dice)
    prof_column = ["Trained", "Expert", "Master", "Legendary"].index(profLevel)+1

    if check_result==0:
        # crit failure
        income = 0
        final_dt_usage = 1
    if check_result==1:
        # failure
        income = EARN_INCOME[taskLevel][1][0]
        final_dt_usage = min(7, downtimeUsed)
    if check_result==2:
        # success
        income = EARN_INCOME[taskLevel][1][prof_column]
        final_dt_usage = downtimeUsed
    if check_result==3:
        # Critical success
        income = EARN_INCOME[taskLevel+1][1][prof_column]
        final_dt_usage = downtimeUsed

    message = f"""Con un {check_value} ({dice}+{checkBonus}) vs DC {DC} , obtienes un {utils.result_name(check_result)}.
Trabajas {final_dt_usage} dias y obtienes {income} gp al día, por un total de {income*final_dt_usage:.2f} gp.
(Por ahora, debes updatearlos manualmente)
"""
    await interaction.send(message)

@bot.slash_command(description="Muestra la lista de tus lenguajes", guild_ids=[CRI_GUILD_ID])
@gets_pj_data
async def languages(interaction: nextcord.Interaction, target:nextcord.Member=None):
    user_id:int = target.id if target is not None else interaction.user.id
    try:
        pj_row:int = sh.get_pj_row(user_id)
        pj_name:str = sh.get_pj_data(pj_row, PJ_COL.Name)
        pj_languages:str = sh.get_pj_data(pj_row, PJ_COL.Languages)
    except sh.CharacterNotFoundError:
        return await interaction.send("No se encontró un personaje con ID de discord correspondiente")
    if pj_languages is not None:
        languages = pj_languages.split(", ")
        message = f"""**Lenguajes de {pj_name}:**
- {'\n- '.join(languages)}"""
    else:
        message = f"{pj_name} no sabe ningún lenguaje."
    return await interaction.send(message)

@bot.slash_command(description="Añade un lenguaje a la lista de tu PJ", guild_ids=[CRI_GUILD_ID])
@gets_pj_data
async def addlanguage(interaction: nextcord.Interaction, addedlanguage= nextcord.SlashOption("lenguaje", "Lenguaje que quieres añadir a tu PJ", True, choices=LANGUAGES), target:nextcord.Member=None):
    user_id:int = target.id if target is not None else interaction.user.id
    try:
        pj_row:int = sh.get_pj_row(user_id)
        pj_name:str = sh.get_pj_data(pj_row, PJ_COL.Name)
        pj_languages:str = sh.get_pj_data(pj_row, PJ_COL.Languages)
    except sh.CharacterNotFoundError:
        return await interaction.send("No se encontró un personaje con ID de discord correspondiente")
    languages = [] if pj_languages in [None, ""] else pj_languages.split(", ")
    if addedlanguage not in languages:
        languages.append(addedlanguage)
        sh.update_pj_data_cell(pj_row, PJ_COL.Languages, [[", ".join(languages)]])
        return await interaction.send(f"{addedlanguage} ha sido añadido a la lista de {pj_name}.")
    else:
        return await interaction.send(f"{addedlanguage} ya está en la lista de {pj_name}.")


@bot.slash_command(description="Revisa tu reputación", guild_ids=[CRI_GUILD_ID])
@gets_rep_data
async def reputation(interaction: nextcord.Interaction, target:nextcord.Member=None):
    user_id:int = target.id if target is not None else interaction.user.id
    reps:list = sh.get_pj_reps(user_id)
    message = ""
    print(reps)
    if len(reps)>0:
        message = f"# Reputación de {reps[0][REP_COL.num(REP_COL.Name)]}"
        reps.sort(reverse=True, key=lambda r: r[REP_COL.num(REP_COL.Reputation)])
        print(reps)

        for rep in reps:
            row_pj_name, row_discord_id, row_faction, row_reputation, row_index = rep
            message += f"\n- {row_faction}: {row_reputation}"
    else:
        message = "Tu personaje no tiene reputación con ningún NPC ni facción."
    return await interaction.send(message)


@bot.slash_command(description="Actualiza tu reputación con una facción o NPC", guild_ids=[CRI_GUILD_ID])
@gets_rep_data
@gets_pj_data
async def updatereputation(interaction: nextcord.Interaction, amount:int, faction:str, target:nextcord.Member=None):
    
    user_id:int = target.id if target is not None else interaction.user.id

    reps:list = sh.get_pj_reps(user_id)
    rep_row = [row for row in reps if row[REP_COL.num(REP_COL.Faction)] == faction]

    if len(rep_row):
        # Add reptuation
        row_pj_name, row_discord_id, row_faction, row_reputation, row_index = rep_row[0]
        new_rep = row_reputation+amount
        new_row = [row_pj_name, row_discord_id, row_faction, new_rep]
        sh.update_rep_row(row_index, new_row)
        await interaction.send(f"Actualizada la reputación de {row_pj_name} con {faction}: {row_reputation} -> {new_rep}")

    else:
        # Create new line
        try:
            pj_row = sh.get_pj_row(user_id)
            pj_name = sh.get_pj_data(pj_row, PJ_COL.Name)
        except sh.CharacterNotFoundError:
            return await interaction.send("No se encontró un personaje con ID de discord correspondiente")
        row_index = sh.first_empty_rep_row()
        new_row = [pj_name, str(user_id), faction, amount]
        print(new_row)
        sh.update_rep_row(row_index, new_row)
        await interaction.send(f"Creada la reputación de {pj_name} con {faction}: {amount}")
        


@updatereputation.on_autocomplete("faction")
async def autocomplete_faction(interaction: nextcord.Interaction, faction: str):
    filtered_ancestries = []
    if faction:
        if len(faction)==1:
            sh.update_rep_data()
            print("Updated rep data once")
        filtered_ancestries = [a for a in sh.get_all_existing_factions() if a.lower().startswith(faction.lower())]
    await interaction.response.send_autocomplete(filtered_ancestries)


@bot.slash_command(description="Gana el downtime y dinero esperado de terminar una misión", guild_ids=[CRI_GUILD_ID])
@gets_pj_data
async def salary(interaction: nextcord.Interaction, level:int, target:nextcord.Member=None):
    user_id:int = target.id if target is not None else interaction.user.id
    try:
        pj_row = sh.get_pj_row(user_id)
        pj_name = sh.get_pj_data(pj_row, PJ_COL.Name)
    except sh.CharacterNotFoundError:
        return await interaction.send("No se encontró un personaje con ID de discord correspondiente")
    

    sueldo_gp, sueldo_dt = sh.get_sueldo(level)

    pj_coins = sh.get_pj_coins(pj_row)
    pp, gp, sp, cp, total = pj_coins
    
    new_total_gp = total + sueldo_gp
    new_coins = utils.gp_to_coin_list(new_total_gp)
    pp, gp, sp, cp = new_coins

    pj_dt = sh.get_pj_data(pj_row, PJ_COL.Downtime)
    new_total_dt = pj_dt+sueldo_dt

    sh.update_pj_data_cell(pj_row, PJ_COL.Downtime, [[new_total_dt, pp, gp, sp, cp]])

    return await interaction.send(f"{pj_name}: Nivel {level} completado!\n Se te suma el sueldo del nivel: {sueldo}gp (ahora tienes {new_total_gp}gp)\n Se te suman {sueldo_dt} días de dt (ahora tienes {new_total_dt} dias de dt)")

bot.run(BOT_TOKEN)