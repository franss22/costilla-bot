import SheetControl as Sheet
from SheetControl import COL
import dndice
import random

class GACHACOL:
    common_min = "A"
    uncommon_min = "B"
    rare_min = "C"
    very_rare_min = "D"
    legendary_min = "E"
    uncommon_maj = "F"
    rare_maj = "G"
    very_rare_maj = "H"
    legendary_maj = "I"

    common_min_name = "minor Common"
    uncommon_min_name = "minor Uncommon"
    rare_min_name = "minor Rare"
    very_rare_min_name = "minor Very Rare"
    legendary_min_name = "minor Legendary"
    uncommon_maj_name = "major Uncommon"
    rare_maj_name = "major Rare"
    very_rare_maj_name = "major Very Rare"
    legendary_maj_name = "major Legendary"

    @classmethod
    def col_to_name(cls, col: str):
        dic = {
            cls.common_min: cls.common_min_name,
            cls.uncommon_min: cls.uncommon_min_name,
            cls.rare_min: cls.rare_min_name,
            cls.very_rare_min: cls.very_rare_min_name,
            cls.legendary_min: cls.legendary_min_name,
            cls.uncommon_maj: cls.uncommon_maj_name,
            cls.rare_maj: cls.rare_maj_name,
            cls.very_rare_maj: cls.very_rare_maj_name,
            cls.legendary_maj: cls.legendary_maj_name,
        }
        return dic.get(col, None)


def check_to_DMG_able(check_num) -> str:
    tablas = {
        41: "I",
        36: "H",
        31: "G",
        26: "F",
        21: "E",
        16: "D",
        11: "C",
        6: "B",
        1: "A"
    }
    if check_num <= 0:
        return None
    for min_check in tablas.keys():
        if check_num >= min_check:
            return tablas[min_check]


def roll_rarity(DMG_table: str):
    roll = dndice.basic("1d100")

    tablas = {
        "A": {91: GACHACOL.uncommon_min,
              1: GACHACOL.common_min},
        "B": {1: GACHACOL.uncommon_min},
        "C": {5: GACHACOL.rare_min,
              1: GACHACOL.uncommon_min},
        "D": {2: GACHACOL.very_rare_min,
              1: GACHACOL.rare_min},
        "E": {36: GACHACOL.legendary_min,
              1: GACHACOL.very_rare_min},
        "F": {1: GACHACOL.uncommon_maj},
        "G": {3: GACHACOL.rare_maj,
              1: GACHACOL.uncommon_maj},
        "H": {9: GACHACOL.very_rare_maj,
              3: GACHACOL.rare_maj,
              1: GACHACOL.uncommon_maj},
        "I": {15: GACHACOL.legendary_maj,
              7: GACHACOL.very_rare_maj,
              1: GACHACOL.rare_maj},
    }
    for min_res in tablas[DMG_table].keys():
        if roll >= min_res:
            return tablas[DMG_table][min_res]


def gacha_cell(row: int, col: str) -> str:
    return f"'Gacha con Puerto'!{col}{row}"


def get_items_table(table_col: str):
    range = f"'Gacha con Puerto'!{table_col}3:{table_col}"
    items = Sheet.get_data(range, single=False)
    return [item[0] for item in items]


def roll_table_price(table_col: str, discount:float=0):
    common_price = "(1d6+1)*10"
    uncommon_price = "(1d4+2)*100"
    rare_price = "(4d6+1)*1000"
    very_rare_price = "(3d4+3)*5000"
    legendary_price = "(3d6+3)*20000"

    prices_per_table = {
        GACHACOL.common_min: common_price,
        GACHACOL.uncommon_min: uncommon_price,
        GACHACOL.uncommon_maj: uncommon_price,
        GACHACOL.rare_min: rare_price,
        GACHACOL.rare_maj: rare_price,
        GACHACOL.very_rare_min: very_rare_price,
        GACHACOL.very_rare_maj: very_rare_price,
        GACHACOL.legendary_min: legendary_price,
        GACHACOL.legendary_maj: legendary_price
    }
    
    price_formula = prices_per_table[table_col]
    price = dndice.basic(price_formula)
    return round(price*(1-discount), 2)


def gacha_info():
    discount = "'🏙️'!P23"
    compli = "'🏙️'!P22"
    bono = "'🏙️'!M4"
    ranges = [discount, compli, bono]

    return Sheet.get_batch_data_anywhere(ranges)


def downgrade_options(DMG_table: str) -> str:
    tables = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    return tables[:1+tables.index(DMG_table)]

def buy_item(row:int, item:dict):
    pass
    
def check_gacha_slots(row:int, item:dict):
    rarity = item['rarity']
    if rarity == GACHACOL.very_rare_min_name or rarity == GACHACOL.very_rare_maj_name:
        # Item Very Rare
        vr1, vr2 = Sheet.get_batch_data(row, [COL.very_rare_1, COL.very_rare_2], single=False)
        if vr1 is None:
            return (True, COL.very_rare_1)
        elif vr2 is None:
            return (True, COL.very_rare_2)
        else: return (False, None)
    elif rarity == GACHACOL.legendary_min_name or rarity == GACHACOL.legendary_maj_name:
        # Item legendary
        lg, = Sheet.get_batch_data(row, [COL.legendary], single=False)
        if lg is None:
            return (True, COL.legendary)
        else: return (False, None)
    else:
        return (True, None)

def set_gacha_slot(row:int, col:str, item:dict):
    txt = [[f"{item['name']}:{item['price']}gp"]]
    Sheet.edit_data(Sheet.simple_cell(row, col), txt, formula=False, edit_func=Sheet.replace_value, single=False)
    
class GachaController():
    def __init__(self, descuento, complicacion, row, user):
        self.descuento = float(descuento)
        self.complicacion_threshold = int(complicacion)
        self.row = row
        self.chosen_dmg_table = None
        self.table_options = []
        self.items = []
        self.user = user
        
    def DMG_table_options(self, check_result:int):
        rolled_table  = check_to_DMG_able(check_result)
        self.table_options = downgrade_options(rolled_table)
        return rolled_table
    
    def d4_amount(self, picked_table:str):
        return max(1, self.table_options[::-1].index(picked_table))
    
        
        
    def roll_items(self, amount:int, chosen_DMG_table:str):
        
        
        columns = {}
        
        for item in range(amount):
            rarity = roll_rarity(chosen_DMG_table)
            columns[rarity] = columns.setdefault(rarity, 0) + 1

        items = []
        for item_type, amt in columns.items():
            items_table = get_items_table(item_type)
            for i in range(amt):
                item = random.choice(items_table)
                price = roll_table_price(item_type, self.descuento)
                items.append({"name":item, "price":price, "bought":False, "rarity": GACHACOL.col_to_name(item_type)})
        for i, item in enumerate(items):
            item["letter"] = chr(65+i)
        self.items = items
    
    def items_for_sale_message(self):
        msg = ""
        for item in self.items:
            msg += f"{item['letter']} - {item['rarity']} - {item['name']}: {item['price']}gp.{' (COMPRADO)' if item['bought'] else ''}\n"
        return msg
    
    def items_for_sale(self):
        # ret = []
        # for item in self.items:
        #     if not item['bought']:
        #         ret.append(item)
        # return ret
        return self.items

    def buy(self, item:dict, consumable:bool):
        old_total_money = float(Sheet.get_pj_data(self.row, COL.money_total))
        price = item['price'] * (0.5 if consumable else 1)
        
        if price > old_total_money:
            return f"`Tus ahorros ({old_total_money}gp) no te alcanzan para comprar el objeto {item['letter']}.`*heh*\n"
        can_buy, slot = check_gacha_slots(self.row, item)
        
        if not can_buy and not consumable:
            return f'`No puedes comprar un objeto de rareza {item["rarity"]}, ya compraste el máximo. Si quieres, puedes devolver un item para liberar un espacio y comprar el objeto manualmente (no olvides anotarlo en el excel)`\n'
        slot_msg = ""
        if slot is not None and not consumable:
            set_gacha_slot(self.row, slot, item)
            slot_msg = " Se utilizó uno de tus slots de item de gacha."
        
        Sheet.pay(self.row, price)
        new_total_money = Sheet.get_pj_data(self.row, COL.money_total)
        complication_result = dndice.basic("1d100")
        if complication_result >= self.complicacion_threshold:
            compli_msg = f"No hay complicaciones ({complication_result})"
        else:
            compli_msg = f"Hay una complicación ({complication_result})"
        item["bought"] = True
            
        return f"`Compraste {item['name']} {'(consumible) ' if consumable else ''}for {price}gp. Te quedan {new_total_money}gp. {compli_msg}.{slot_msg}`\n"

    




if __name__ == "__main__":
    print(downgrade_options("G"))
    
    item = {"name":"holi", "price":123123, "rarity":GACHACOL.legendary_maj_name}
    succ, col = check_gacha_slots(4, item)
    set_gacha_slot(4, col, item)