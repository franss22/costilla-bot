import json

RELIGIONS: list[str] = [
    "La Labor",
    "El Continuo",
    "El Camino",
    "La Prisión",
    "El Arquitecto",
    "El Potencial",
    "Ninguna",
    "Otro",
]

LANGUAGES: list[str] = [
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

CLASSES: list[str] = [
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
    "Wizard",
]

EARN_INCOME: dict[int, tuple[int, tuple[float, float, float, float, float]]] = {
    #   lvl, dc,   fail, trnd, exprt, mstr, lgdry
    0: (14, (0.01, 0.05, 0.05, 0.05, 0.05)),
    1: (15, (0.02, 0.2, 0.2, 0.2, 0.2)),
    2: (16, (0.04, 0.3, 0.3, 0.3, 0.3)),
    3: (18, (0.08, 0.5, 0.5, 0.5, 0.5)),
    4: (19, (0.1, 0.7, 0.8, 0.8, 0.8)),
    5: (20, (0.2, 0.9, 1, 1, 1)),
    6: (22, (0.3, 1.5, 2, 2, 2)),
    7: (23, (0.4, 2, 2.5, 2.5, 2.5)),
    8: (24, (0.5, 2.5, 3, 3, 3)),
    9: (26, (0.6, 3, 4, 4, 4)),
    10: (27, (0.7, 4, 5, 6, 6)),
    11: (28, (0.8, 5, 6, 8, 8)),
    12: (30, (0.9, 6, 8, 10, 10)),
    13: (31, (1, 7, 10, 15, 15)),
    14: (32, (1.5, 8, 15, 20, 20)),
    15: (34, (2, 10, 20, 28, 28)),
    16: (35, (2.5, 13, 25, 36, 40)),
    17: (36, (3, 15, 30, 45, 55)),
    18: (38, (4, 20, 45, 70, 90)),
    19: (39, (6, 30, 60, 100, 130)),
    20: (40, (8, 40, 75, 150, 200)),
    21: (50, (0, 50, 90, 175, 300)),
}

ANCESTRIES: list[str] = [
    "Anadi",
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

with open("Ancestries.json") as f:
    HERITAGES: dict[str, list[str]] = json.load(f)
