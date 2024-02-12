import gspread
import utils
from varenv import getVar
import json

PJ_SHEET_ID = 0
REPUTATION_SHEET_ID = 37818595

credentials = json.loads(getVar("GOOGLE"), strict=False)

gc = gspread.service_account_from_dict(credentials)

pj_sheet = gc.open("Megamarch").get_worksheet_by_id(PJ_SHEET_ID)


class PJ_COL:
    Name = "A"
    Discord_id = "B"
    Player = "C"
    Class = "D"
    Arquetypes = "E"
    Ancestry = "F"
    Heritage = "G"
    Downtime = "H"
    Money_pp = "I"
    Money_gp = "J"
    Money_sp = "K"
    Money_cp = "L"
    Money_total = "M"
    Languages = "N"
    Religion = "O"
   
    
    @classmethod
    def has_value(cls, value):
        return value in cls.__dict__.values()
    
def whole_column(column:str):
        return f"{column}:{column}"

class CharacterNotFoundError(Exception):
    pass

def get_pj_row(discord_id:int):
    try:
        column = pj_sheet.get(whole_column(PJ_COL.Discord_id))
        id_row = column.index([str(discord_id)])+1
        # index del primer valor con [discord_id] de todos los ids (+1 por 0 indexed)
        return id_row
    except ValueError:
        raise CharacterNotFoundError(f"Character with discord ID '{discord_id}' was not found")

def first_empty_PJ_row():
    column = pj_sheet.get(whole_column(PJ_COL.Discord_id))
    return len(column)+1

def update_range_PJ(pos:str, values):
    pj_sheet.update(values, pos)

def pj_cell(pj:str, col:str):

    if PJ_COL.has_value(col):
        return f"{col}{get_pj_row(pj)}"
    else:
        raise ValueError(f"Column {col} does not exist")

def simple_cell(row:str, col:str):
    if PJ_COL.has_value(col):
        return f"{col}{row}"
    else:
        raise ValueError(f"Column {col} does not exist")

def get_pj_data(pj_row:int, col:str):
    data_cell = f"{col}{pj_row}"
    resp = pj_sheet.get(data_cell, value_render_option = "UNFORMATTED_VALUE")

    return resp[0][0]

def update_pj_data_cell(pj_row:int, col:str, value):
    
    pj_sheet.update(value, f"{col}{pj_row}")


def get_pj_full(row:int, formula=False, single=True):
    render = "FORMULA" if formula else "FORMATTED_VALUE"
    data = pj_sheet.get(f"A{row}:O{row}", value_render_option=render)
    
    return data[0]

def get_pj_coins(row:int):
    coins = pj_sheet.get(f"{PJ_COL.Money_pp}{row}:{PJ_COL.Money_total}{row}", value_render_option = "UNFORMATTED_VALUE")[0]
    return [float(x) for x in coins]

def update_pj_coins(row:int, values):
    coins = pj_sheet.update(values, f"{PJ_COL.Money_pp}{row}:{PJ_COL.Money_total}{row}")

# def add_to_formula(formula, add):
#     formula = str(formula)
#     add = str(add)
#     if float(add) == 0:
#         return formula

#     if formula[0] != "=":
#         formula = "=" + formula
#     if add[0].isnumeric():
#         add = "+" + add
#     return formula + add

# def replace_value(_, new):
#     return new

# def clean_formula(old, _):
#     return old



# def get_data(range:str, formula=False, single=True):
#     render = "FORMULA" if formula else "FORMATTED_VALUE"
#     data = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
#                                 range=range, valueRenderOption=render).execute().get("values", [[0]])
    
#     return data[0][0] if single else data

# def get_batch_data(row:int, cols:list, formula=False, single=True):
#     render = "FORMULA" if formula else "FORMATTED_VALUE"
#     ranges = [simple_cell(row, col) for col in cols]
#     batch = sheet.values().batchGet(spreadsheetId=SPREADSHEET_ID, ranges=ranges, valueRenderOption=render).execute().get("valueRanges", [])
#     # print(batch)
#     data = [val.get("values", [[0]])[0][0] for val in batch] if single else [val.get("values") for val in batch]
#     return data

# def get_batch_data_anywhere(ranges, formula=False, single=True):
#     render = "FORMULA" if formula else "FORMATTED_VALUE"
#     batch = sheet.values().batchGet(spreadsheetId=SPREADSHEET_ID, ranges=ranges, valueRenderOption=render).execute().get("valueRanges", [])
#     data = [val.get("values", [[0]])[0][0] for val in batch] if single else [val.get("values") for val in batch]
#     return data



# def edit_data(range:str, data, formula = True, edit_func=add_to_formula, single=True):
#     old_data = get_data(range, formula, single)
#     new_data = edit_func(old_data, data)
    
#     sheet.values().update(spreadsheetId=SPREADSHEET_ID,
#                           range=range, 
#                           valueInputOption="USER_ENTERED", 
#                           body={'values': [[new_data]] if single else new_data}).execute()
#     return old_data

# def edit_batch_data(row:int, cols:list, data:list, formula = True, edit_func=add_to_formula):
#     #edit_func(old_data, data) must return (new_data, success_bool)
#     ranges = [simple_cell(row, col) for col in cols]
#     old_data = get_batch_data(row, cols, formula)
#     mapped_data = map(edit_func, old_data, data)
    
#     new_data = [{"range": range, "values":[[data]]} for (range, data) in zip(ranges, mapped_data)]
    
#     sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID,
#                           body={"valueInputOption":"USER_ENTERED", 'data': new_data}).execute()
#     return old_data

# def get_reward_info(tier: int, skull=False):
#     xp_gold = get_data(f'💰Rwrds!H{tier*2}:M{tier*2}', single=False)[0]
#     dt = float(get_data(f'💰Rwrds!O2'))
#     xp = int(xp_gold[1 if skull else 0])
#     gold = int(xp_gold[4 if skull else 3])
#     princ_bonus = int(xp_gold[5])
    
#     return (xp, gold, dt, princ_bonus)

# def pay(row:int, cost:float):

#     get_range = f"{PJ_SHEET}{COL.money_pp}{row}:{COL.money_total}{row}"
#     edit_range = f"{PJ_SHEET}{COL.money_pp}{row}:{COL.money_cp}{row}"
    
#     coin_values = get_data(get_range, single=False)[0]
    
#     total_gold = float(coin_values[5])
#     if total_gold < cost:
#         return f'''No tienes suficiente dinero para pagar esa cantidad:
#         Dinero actual: {total_gold}
#         Faltante: {cost-total_gold}
#         '''
#     else:
#         def edit_func(old_coin_amt, costo):
#             delta = utils.pay_priority(coin_values[:5], costo)
#             new_range_val = [add_to_formula(old_coin_amt[0][i], delta[i]) for i in range(5)]
#             return [new_range_val]
        
#         old_data = edit_data(edit_range, cost, edit_func=edit_func, single=False)
#         return True

# def add_money(row:int, add_amt:float):
    
#     adding_list = utils.gp_to_coin_list(add_amt)
#     edit_range = f"{PJ_SHEET}{COL.money_pp}{row}:{COL.money_cp}{row}"
#     def edit_func(old_money, add_list):
#         return [list(map(add_to_formula, old_money[0], add_list))]

#     return edit_data(edit_range, adding_list, edit_func=edit_func, single=False)

    



if __name__ == "__main__":
    # print(COL.name)
    # print(get_pj_data_with_name("test", COL.money_total))
    print(detect_other_PJ(15))