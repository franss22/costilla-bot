from googleapiclient.discovery import build
from google.oauth2 import service_account
import utils
import varenv
import json

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = "google-credentials.json"
SPREADSHEET_ID = '1gPknOWaAWmaeUAs6UTG6yC_ad8f5RT85Y72-hWHbuqM'

keyEnvVar = varenv.getVar("GOOGLE_CREDENTIALS")
print(keyEnvVar)
keys = json.loads(keyEnvVar, strict=False)

creds = service_account.Credentials.from_service_account_info(keys, scopes=SCOPES) #from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

PJ_SHEET = "👨‍👨‍👧‍👧PJs!"

class COL:
    name = "A"
    pj_id = "B"
    player = "C"
    tier = "D"
    xp = "E"
    levels = "F"
    race = "G"
    subrace = "H"
    alignment = "I"
    height = "J"
    weight = "K"
    age = "L"
    money_pp = "M"
    money_gp = "N"
    money_ep = "O"
    money_sp = "P"
    money_cp = "Q"
    money_total = "R"
    downtime = "S"
    renown_faction = "T"
    renown = "U"
    piety_god = "V"
    piety = "W"
    very_rare_1 = "X"
    very_rare_2 = "Y"
    legendary = "Z"
    slaves = "AA"
    employees = "AB"
    
    
    @classmethod
    def has_value(cls, value):
        return value in cls.__dict__.values()

class CharacterNameError(Exception):
    pass

def get_pj_row(pj_id:str):
    try:
        # index del primer valor con [pj_id] de todos los ids (+1 por 0 indexed)
        id_row = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range='👨‍👨‍👧‍👧PJs!B:B').execute().get('values').index([pj_id])+1
        return id_row
    except ValueError:
        raise CharacterNameError(f"Character with ID '{pj_id}' was not found")

def pj_cell(pj:str, col:str):

    if COL.has_value(col):
        return f"{PJ_SHEET}{col}{get_pj_row(pj)}"
    else:
        raise ValueError(f"Column {col} does not exist")

def simple_cell(row:str, col:str):
    if COL.has_value(col):
        return f"{PJ_SHEET}{col}{row}"
    else:
        raise ValueError(f"Column {col} does not exist")
    

def add_to_formula(formula, add):
    formula = str(formula)
    add = str(add)
    if float(add) == 0:
        return formula

    if formula[0] != "=":
        formula = "=" + formula
    if add[0].isnumeric():
        add = "+" + add
    return formula + add

def replace_value(_, new):
    return new

def clean_formula(old, _):
    return old

def get_pj_data(row:int, col:str, formula=False, single=True):
    render = "FORMULA" if formula else "FORMATTED_VALUE"
    data = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=simple_cell(row, col), valueRenderOption=render).execute().get("values", [[0]])
    
    return data[0][0] if single else data

def get_data(range:str, formula=False, single=True):
    render = "FORMULA" if formula else "FORMATTED_VALUE"
    data = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=range, valueRenderOption=render).execute().get("values", [[0]])
    
    return data[0][0] if single else data

def get_batch_data(row:int, cols:list, formula=False, single=True):
    render = "FORMULA" if formula else "FORMATTED_VALUE"
    ranges = [simple_cell(row, col) for col in cols]
    batch = sheet.values().batchGet(spreadsheetId=SPREADSHEET_ID, ranges=ranges, valueRenderOption=render).execute().get("valueRanges", [])
    print(batch)
    data = [val.get("values", [[0]])[0][0] for val in batch] if single else [val.get("values") for val in batch]
    return data

def get_batch_data_anywhere(ranges, formula=False, single=True):
    render = "FORMULA" if formula else "FORMATTED_VALUE"
    batch = sheet.values().batchGet(spreadsheetId=SPREADSHEET_ID, ranges=ranges, valueRenderOption=render).execute().get("valueRanges", [])
    data = [val.get("values", [[0]])[0][0] for val in batch] if single else [val.get("values") for val in batch]
    return data

def get_pj_data_with_name(pj_id:str, col:str, formula=False):
    render = "FORMULA" if formula else "FORMATTED_VALUE"
    row = get_pj_row(pj_id)
    name_cell = f"{PJ_SHEET}{COL.name}{row}"
    data_cell = f"{PJ_SHEET}{col}{row}"
    resp = sheet.values().batchGet(spreadsheetId=SPREADSHEET_ID, ranges=[name_cell, data_cell], valueRenderOption=render).execute().get("valueRanges", [])
    name = resp[0].get("values", [[0]])[0][0]
    data = resp[1].get("values", [[0]])[0][0]

    return (name, data, row)

def edit_data(range:str, data, formula = True, edit_func=add_to_formula, single=True):
    old_data = get_data(range, formula, single)
    new_data = edit_func(old_data, data)
    
    sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                          range=range, 
                          valueInputOption="USER_ENTERED", 
                          body={'values': [[new_data]] if single else new_data}).execute()
    return old_data

def edit_batch_data(row:int, cols:list, data:list, formula = True, edit_func=add_to_formula):
    #edit_func(old_data, data) must return (new_data, success_bool)
    ranges = [simple_cell(row, col) for col in cols]
    old_data = get_batch_data(row, cols, formula)
    mapped_data = map(edit_func, old_data, data)
    
    new_data = [{"range": range, "values":[[data]]} for (range, data) in zip(ranges, mapped_data)]
    
    sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                          body={"valueInputOption":"USER_ENTERED", 'data': new_data}).execute()
    return old_data

def get_reward_info(tier: int, skull=False):
    xp_gold = get_data(f'💰Rwrds!H{tier*2}:M{tier*2}', single=False)[0]
    dt = float(get_data(f'💰Rwrds!O2'))
    xp = int(xp_gold[1 if skull else 0])
    gold = int(xp_gold[4 if skull else 3])
    princ_bonus = int(xp_gold[5])
    
    return (xp, gold, dt, princ_bonus)

def pay(row:int, cost:float):

    get_range = f"{PJ_SHEET}{COL.money_pp}{row}:{COL.money_total}{row}"
    edit_range = f"{PJ_SHEET}{COL.money_pp}{row}:{COL.money_cp}{row}"
    
    coin_values = get_data(get_range, single=False)[0]
    
    total_gold = float(coin_values[5])
    if total_gold < cost:
        return f'''No tienes suficiente dinero para pagar esa cantidad:
        Dinero actual: {total_gold}
        Faltante: {cost-total_gold}
        '''
    else:
        def edit_func(old_coin_amt, costo):
            delta = utils.pay_priority(coin_values[:5], costo)
            new_range_val = [add_to_formula(old_coin_amt[0][i], delta[i]) for i in range(5)]
            return [new_range_val]
        
        old_data = edit_data(edit_range, cost, edit_func=edit_func, single=False)
        return True

def add_money(row:int, add_amt:float):
    
    adding_list = utils.gp_to_coin_list(add_amt)
    edit_range = f"{PJ_SHEET}{COL.money_pp}{row}:{COL.money_cp}{row}"
    def edit_func(old_money, add_list):
        return [list(map(add_to_formula, old_money[0], add_list))]

    return edit_data(edit_range, adding_list, edit_func=edit_func, single=False)


def detect_other_PJ(row:int):

    player, all_players, all_names, all_IDs = get_batch_data_anywhere([f"{PJ_SHEET}{COL.player}{row}", f"{PJ_SHEET}{COL.player}:{COL.player}", f"{PJ_SHEET}{COL.name}:{COL.name}", f"{PJ_SHEET}{COL.pj_id}:{COL.pj_id}"], single=False)
    # print(player, players, PJs, IDs)
    indexes = [i for i, val in enumerate(all_players) if val == player[0]]
    if len(indexes) > 2:
        raise ValueError("Este jugador tiene mas de 2 PJs activos")
    if len(indexes) == 1:
        return None
    
    PJs = [{"name":all_names[i][0], "ID":all_IDs[i][0], "row":i+1} for i in indexes]
    
    other_PJ = [pj for pj in PJs if pj["row"] != row][0]
    
    return other_PJ

    



if __name__ == "__main__":
    # print(COL.name)
    # print(get_pj_data_with_name("test", COL.money_total))
    print(detect_other_PJ(15))