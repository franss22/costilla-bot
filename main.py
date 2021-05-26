from discord.ext import commands
import discord
import dndice
import dice
import os
import sqlite3
import datetime

bot = commands.Bot(command_prefix='$')


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))


@bot.command()
async def test(ctx, *args):
    await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))


@bot.command()
async def massroll(ctx, amt: int, atk: str, dmg: str = '0', ac: int = 0):
    emb = discord.Embed(title=f'Mass roll: {amt} rolls against AC {ac}')
    sumNum = 0
    try:
        dndice.basic(atk)
    except:
        ctx.send(f'{atk} is not valid roll syntax')
    try:
        dndice.basic(dmg)
    except:
        ctx.send(f'{atk} is not valid roll syntax')

    for x in range(amt):
        atkRoll = dndice.basic(atk)
        dmgRoll = dndice.basic(dmg)

        if atkRoll == dice.roll_max(atk):
            critical = 'Critical Attack!: '
            dmgRoll = dndice.basic(dmg.replace('d', 'dc'))
        else:
            critical = 'Attack: '

        if dmg != '0':
            emb.add_field(
                name=f'Attack {x}', value=f'{critical}{atkRoll}, damage: {dmgRoll}')
        else:
            emb.add_field(name=f'Attack {x}', value=f'{critical}{atkRoll}')

        if (atkRoll >= ac or critical == 'Critical Attack!: '):
            sumNum += dmgRoll

    emb.add_field(name=f'Sum of the Damage', value=f'{sumNum} damage')
    await ctx.send(embed=emb)


@bot.command()
async def downtime(ctx):
    emb = discord.Embed(title='Actividades de Downtime:')
    text = '''
    Construir un Objeto Mundano: $mundano 
    Crear Plano de Objeto Mágico: $plano
    Crimen: $crimen
    Fermentar Pociones: $fermentar
    Fijar Hechizo: $fijar
    Investigar: $investigar
    Irse de Juerga: $juerga
    Pelear por Dinero: $pelear
    Replicar Poción: $replicar
    Servicio Religioso: $religioso
    Apostar: $apostar
    Trabajar un Oficio: $trabajar
    Aprender Hechizo: $aprender
    Buscar Hechizo: $buscar
    Comprar Objeto mágico: $compra
    Construir un objeto mágico: $artificiar
    '''
    emb.add_field(name='Comandos', value=text)
    await ctx.send(embed=emb)


@bot.command()
async def artificiar(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323160400887848/ConstObjetoMagico.png'
    await genDowntime(ctx, 'Construir un Objeto Mágico', url)


@bot.command()
async def compra(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323157191983126/ComprarObjetoMagico.png'
    await genDowntime(ctx, 'Comprar Objeto Mágico', url)


@bot.command()
async def buscar(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323152468541450/BuscarHechizo.png?width=550&height=675'
    await genDowntime(ctx, 'Buscar Hechizo', url)


@bot.command()
async def aprender(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323148229017620/AprenderHechizo.png'
    await genDowntime(ctx, 'Aprender Hechizo', url)


@bot.command()
async def trabajar(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323140683857930/TrabajarUnOficio.png'
    await genDowntime(ctx, 'Trabajar un Oficio', url)


@bot.command()
async def apostar(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323138489319444/Apostar.png?width=245&height=675'
    await genDowntime(ctx, 'Apostar', url)


@bot.command()
async def religioso(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323114205216778/ServicioReligioso.png?width=592&height=675'
    await genDowntime(ctx, 'Servicio Religioso', url)


@bot.command()
async def replicar(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323110073303090/ReplicarPocion.png'
    await genDowntime(ctx, 'Replicar Poción', url)


@bot.command()
async def pelear(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323107565764648/PelearPorDinero.png?width=333&height=675'
    await genDowntime(ctx, 'Pelear por Dinero', url)


@bot.command()
async def juerga(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323105694842910/IrseDeJuerga.png?width=279&height=676'
    await genDowntime(ctx, 'Irse de Juerga', url)


@bot.command()
async def investigar(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323103114559518/Investigar.png'
    await genDowntime(ctx, 'Investigar', url)


@bot.command()
async def fijar(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323099650981909/FijarHechizo.png'
    await genDowntime(ctx, 'Fijar Hechizo', url)


@bot.command()
async def fermentar(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323096672763914/Fermentar.png'
    await genDowntime(ctx, 'Fermentar Pociones', url)


@bot.command()
async def crimen(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323096055808050/Crimen.png'
    await genDowntime(ctx, 'Crimen', url)


@bot.command()
async def plano(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323093182578728/ConsturirPLano.png'
    await genDowntime(ctx, 'Crear Plano de Objeto Mágico', url)


@bot.command()
async def mundano(ctx):
    url = 'https://media.discordapp.net/attachments/763955185679597580/843323092402962492/ConstruirObjetoMundano.png'
    await genDowntime(ctx, 'Construir un Objeto Mundano', url)


async def genDowntime(ctx, name, imageUrl):
    emb = discord.Embed(title=f'Downtime Activities: {name}')
    emb.set_image(url=imageUrl)
    await ctx.send(embed=emb)


def saveFish(fishName:str, fisherName:str):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    date = str(datetime.datetime.now())
    cur.execute("insert into fish values (?, ?, ?)", (date, fishName, fisherName))
    con.commit()
    con.close()

@bot.command()
async def personajePescaPez(ctx, nombrePJ:str, nombrePez:str):
    saveFish(nombrePez, nombrePJ)
    await ctx.send(f"`{nombrePJ} pescó un {nombrePez}!`");

@bot.command()
async def tablonPesca(ctx):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    fish = cur.execute("select * from fish").fetchall()
    msg = "```**Tablón de Pesca:\n"
    fishers = {}
    for row in fish:
        date = row[0]
        fisherman = row[1]
        fishName = row[2]
        add = f"-{fisherman} pescó un {fishName}\n"
        if (len(msg) <(2000-len(add)-3)):
            msg.append()
        else:
            await ctx.send("La cantidad de pescado en el anuncio sobrepasa el limite de caracteres de Discord, diganel al Pancho que arregle el bot xd.")
            break
    msg.append("```")
    ctx.send(msg)

    

    


# @bot.command()
# async def help(ctx):
#     emb = discord.Embed(title= 'Help')
#     st = '''$downtime: comandos de downtime
#     $personajePescaPez: pescar
#     $tablonPesca: 
#     '''
#     emb.add_field("Commands", st, inline=True)
#     await ctx.send(emb)


bot.run(os.environ.get('TOKEN'))
