import nextcord
from nextcord.ext import commands
from varenv import getVar
import SheetControl as sh
from SheetControl import PJ_COL
import utils
import json
import dndice

CRI_GUILD_ID = int(getVar("GUILD_ID"))
PANCHO_ID = getVar("PANCHO_ID")
BOT_TOKEN = getVar("TOKEN")

bot = commands.Bot()
with open("Ancestries.json") as f:
    HERITAGES : dict[str, str]= json.load(f)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

"""
register done
status done

lenguajes
    setlenguajes

dt done
pay (pay transfer) done
addmoney done

earn_income

reputationstatus
updatereputation

missioncomplete
"""

RELIGIONS : list[str]= ["La Labor", "El Continuo", "El Camino", "La Prisión", "El Arquitecto", "El Potencial", "Ateo", "Otro"]

LANGUAGES : list[str]= [
    "Nemer", 
    "Sval", 
    "Derani", 
    "Asthenial", 
    "Àárâk", 
    "Originario", 
    "Jovian", 
    "Lingua Franca", 
    "Bíblico", 
    "Ætérico", 
    "Grimm", 
    "Cthonico", 
    "Assembly", 
]

CLASSES : list[str]= [
    "Alchemist",
    "Barbarian",
    "Bard",
    "Champion",
    "Cleric",
    "Druid",
    "Fighter",
    "Gunslinger",
    "Inventor",
    "Investigator",
    "Kineticist",
    "Magus",
    "Monk",
    "Oracle",
    "Psychic",
    "Ranger",
    "Rogue",
    "Sorcerer",
    "Summoner",
    "Swashbuckler",
    "Thaumaturge",
    "Witch",
    "Wizard"
]

EARN_INCOME : dict = {
#   lvl, dc,   fail, trnd, exprt, mstr, lgdry
    0:  (14, [ 0.01, 0.05, 0.05, 0.05, 0.05]),
    1:  (15, [ 0.02, 0.2,  0.2,  0.2,  0.2]),
    2:  (16, [ 0.04, 0.3,  0.3,  0.3,  0.3]),
    3:  (18, [ 0.08, 0.5,  0.5,  0.5,  0.5]),
    4:  (19, [ 0.1,  0.7,  0.8,  0.8,  0.8]),
    5:  (20, [ 0.2,  0.9,  1,    1,    1]),
    6:  (22, [ 0.3,  1.5,  2,    2,    2]),
    7:  (23, [ 0.4,  2,    2.5,  2.5,  2.5]),
    8:  (24, [ 0.5,  2.5,  3,    3,    3]),
    9:  (26, [ 0.6,  3,    4,    4,    4]),
    10: (27, [ 0.7,  4,    5,    6,    6]),
    11: (28, [ 0.8,  5,    6,    8,    8]),
    12: (30, [ 0.9,  6,    8,    10,   10]),
    13: (31, [ 1,    7,    10,   15,   15]),
    14: (32, [ 1.5,  8,    15,   20,   20]),
    15: (34, [ 2,    10,   20,   28,   28]),
    16: (35, [ 2.5,  13,   25,   36,   40]),
    17: (36, [ 3,    15,   30,   45,   55]),
    18: (38, [ 4,    20,   45,   70,   90]),
    19: (39, [ 6,    30,   60,   100,  130]),
    20: (40, [ 8,    40,   75,   150,  200]),
    21: (50, [ 0,    50,   90,   175,  300]),
}

ANCESTRIES : list[str]= ["Anadi",
    "Android",
    "Automaton",
    "Azarketi",
    "Catfolk",
    "Conrasu",
    "Dwarf",
    "Elf",
    "Fetchling",
    "Fleshwarp",
    "Ghoran",
    "Gnoll",
    "Gnome",
    "Goblin",
    "Goloma",
    "Grippli",
    "Halfling",
    "Hobgoblin",
    "Human",
    "Kashrishi",
    "Kitsune",
    "Kobold",
    "Leshy",
    "Lizardfolk",
    "Nagaji",
    "Orc",
    "Poppet",
    "Ratfolk",
    "Shisk",
    "Shoony",
    "Skeleton",
    "Sprite",
    "Strix",
    "Tengu",
    "Vanara",
    "Vishkanya",
    ]

class HeritageDropdown(nextcord.ui.Select):
    Update_func = None
    def __init__(self, ancestry:str, update_func):
        heritages = HERITAGES[ancestry]
        self.Update_func = update_func
        options = [nextcord.SelectOption(label=h) for h in heritages]
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
async def register(interaction: nextcord.Interaction, nombre_pj:str, nombre_jugador:str,
                   clase:str = nextcord.SlashOption(name="clase", required=True, choices=CLASSES), 
                   ascendencia:str = nextcord.SlashOption(name="ascendencia", required=True), 
                   religion:str = nextcord.SlashOption(name="religión", required=True, choices=RELIGIONS)):
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
async def status(interaction: nextcord.Interaction, user:nextcord.Member = None):
    user_id:int = interaction.user.id if user is None else user.id
    try:
        pj_row = sh.get_pj_row(user_id)
    except sh.CharacterNotFoundError:
        return await interaction.send("No se encontró un personaje con ID de discord correspondiente")
    data = sh.get_pj_full(pj_row)
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
async def pay(interaction: nextcord.Interaction, amount: float, transfertarget:nextcord.Member= None):
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
async def addmoney(interaction: nextcord.Interaction, amount: float, target:nextcord.Member= None):
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
Trabajas {final_dt_usage} dias y obtienes {income} gp al día, por un total de {income*final_dt_usage} gp.
(Por ahora, debes updatearlos manualmente)
"""
    await interaction.send(message)

@bot.slash_command(description="Muestra la lista de tus lenguajes", guild_ids=[CRI_GUILD_ID])
async def lenguajes(interaction: nextcord.Interaction):
    pass


@bot.slash_command(description="Cambia la lista de tus lenguajes", guild_ids=[CRI_GUILD_ID])
async def setlenguajes(interaction: nextcord.Interaction, lenguajes:str):
    pass


@bot.slash_command(description="Revisa tu reputación", guild_ids=[CRI_GUILD_ID])
async def reputation(interaction: nextcord.Interaction, user:nextcord.Member=None):
    pass


@bot.slash_command(description="Actualiza tu reputación con una facción o NPC", guild_ids=[CRI_GUILD_ID])
async def updatereputation(interaction: nextcord.Interaction, amount:int, faction:str, user:nextcord.Member=None):
    pass

@bot.slash_command(description="Gana el downtime y dinero esperado de terminar una misión", guild_ids=[CRI_GUILD_ID])
async def missioncomplete(interaction: nextcord.Interaction, level:int, user:nextcord.Member=None):
    pass

bot.run(BOT_TOKEN)