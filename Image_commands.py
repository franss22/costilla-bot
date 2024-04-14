from typing import Any

import nextcord
from nextcord.ext import commands

downtime = [
    # [command_name           dt_name                                          image_url]
    [
        "trabajar",
        "Trabajar un Oficio",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817188611117086/Trabajar.png",
    ],
    ["gacha", "Comprar un Objeto Magico", "https://i.imgur.com/nsZPCRA.png"],
    [
        "juerga",
        "Irse de Juerga",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817284065071104/Irse_de_Juerga.png",
    ],
    [
        "fabricar",
        "Construir un Objeto Mundano",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817190150406154/Fabricar_Objeto.png",
    ],
    [
        "plano",
        "Crear un Plano de Objeto Magico",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817360896327740/Crear_Plano.png",
    ],
    [
        "craftear",
        "Crear un Objeto Magico",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817284526465054/Fabricar_Artefacto.png",
    ],
    [
        "pociones",
        "Fermentar Pociones",
        "https://cdn.discordapp.com/attachments/763955185679597580/913225171928768512/unknown.png",
    ],
    [
        "replicar",
        "Replicar Pocion",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817283238817812/Replicar_Pocion.png",
    ],
    [
        "crimen",
        "Crimen",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817360384647168/Crimen.png",
    ],
    [
        "apostar",
        "Apostar",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817282295078962/Apostar.png",
    ],
    [
        "pelear",
        "Pelear por dinero",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817283624673340/Pelear.png",
    ],
    [
        "rezar",
        "Servicio Religioso",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817188908892230/Servicio_Religioso.png",
    ],
    [
        "fijar",
        "Fijacion de Hechizo Preparado",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817284329308181/Fijar_Hechizo.png",
    ],
    [
        "aprender",
        "Aprender Hechizo",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817361336750090/Aprender_Hechizo.png",
    ],
    [
        "buscar",
        "Buscar Hechizo",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817281972134029/Buscar_Hechizo.png",
    ],
    [
        "investigar",
        "Investigar",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817189877796884/Investigar.png",
    ],
    [
        "entrenar",
        "Entrenar",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817285835071518/Entrenar.png",
    ],
    [
        "cuidar",
        "Cuidado de Animales",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817190469189662/Cuidar_Animales.png",
    ],
    [
        "rito",
        "Rito Tribu Kaeglashita",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817189265436702/Rito_Kaeglashita.png",
    ],
    [
        "construir",
        "Construcción de un Edificio",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817190813126677/Construir_Edificio.png",
    ],
    [
        "negocio",
        "Llevar el Negocio",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817282580295740/Llevar_Negocio.png",
    ],
    [
        "casa",
        "Contruir una Casa",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817191136100402/Comprar_Casa.png",
    ],
    [
        "pc",
        "Aportar a la Construccion de la Peninsula",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817361684865034/Aportar_a_la_construccion.png",
    ],
    [
        "reaprender",
        "Reaprender Hechizos",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817189584199710/Reaprender_Hechizos.png",
    ],
    [
        "transcribirscroll",
        "Transcribir Pergaminos",
        "https://cdn.discordapp.com/attachments/841351175735476277/970817282987130940/Transcribir_Pergamino.png",
    ],
]


def genDowntime(command_name: str, dt_name: str, image_url: str) -> Any:
    @commands.command(name=command_name, brief=dt_name)
    async def f(self, ctx):
        f"""{dt_name}"""
        emb = nextcord.Embed(title=f"Downtime Activities: {dt_name}")
        emb.set_image(url=image_url)
        await ctx.send(embed=emb)

    return f


def generateDowntimeCommands(bot: commands.Bot) -> None: # type: ignore
    for i in downtime:
        command_name = i[0]
        dt_name = i[1]
        image_url = i[2]
        comm = genDowntime(command_name, dt_name, image_url)
        print(comm)
        bot.add_command(comm)


class downtimeCog(commands.Cog, name="Actividades de Downtime"):
    #
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        commands = []
        for i in downtime:
            command_name, dt_name, image_url = i
            comm = genDowntime(command_name, dt_name, image_url)
            commands.append(comm)
            setattr(self, command_name, comm)

        # Sobreescribo a la mala la lista de comandos
        self.__cog_commands__ = tuple(commands)
        for command in self.__cog_commands__:
            setattr(self, command.callback.__name__, command)


if __name__ == "__main__":
    a = downtimeCog(1)
    commands = a.get_commands()
    print(type(a.trabajar))
    print([c.name for c in commands])
