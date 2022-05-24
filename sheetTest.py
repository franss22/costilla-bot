from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from math import ceil
import os
import json
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = "google-credentials.json"
SPREADSHEET_ID = '1gPknOWaAWmaeUAs6UTG6yC_ad8f5RT85Y72-hWHbuqM'

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()






# def get_big_range(range, row):
#     result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
#                                 range=f'👨‍👨‍👧‍👧PJs!{range[0]}{row}:{range[1]}{row}', valueRenderOption="FORMATTED_VALUE").execute()
#     return result



# def search_pj_row(pj_id):
#     item = [pj_id]
#     id_row = None
#     try:
#         id_row = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
#                                     range='👨‍👨‍👧‍👧PJs!B:B').execute().get('values').index(item)+1
#     except ValueError as e:
#         pass
#     return id_row


def append_to_formula(formula, appnd):
    formula = str(formula)
    appnd = str(appnd)
    if float(appnd) == 0:
        return formula

    if formula[0] != "=":
        formula = "=" + formula
    if appnd[0].isnumeric():
        appnd = "+"+appnd
    return formula+appnd


# def valid_num(appnd):
#     try:
#         float(appnd)
#         return True
#     except:
#         return False


def sign(num):
    return 1 if num >= 0 else -1


def gp_to_coin_list(num:float, with_electrum=False):

    num = sign(num)*int(round(abs(float(num))*100))

    pp = num//1000
    gp = num % 1000//100
    ep = 0
    sp = num % 100//10
    cp = num % 10
    if with_electrum:
        ep = sp//5
        sp = sp%5

    return [pp, gp, ep, sp, cp]


def new_money_list(old_money, add_list):
    return list(map(append_to_formula, old_money, add_list))


def update_money(row, new_money):
    try:
        result2 = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                        range=f'👨‍👨‍👧‍👧PJs!M{row}', valueInputOption="USER_ENTERED", body={'values': [new_money]}).execute()
        return True
    except:
        return False


def pay_priority(coins, paid_amt):
    # calcula la diferencia (lo que hay que restarle al dinero original) para pagar paid_amt
    price = gp_to_coin_list(paid_amt)
    # pagamos de las monedas mas caras a las mas baratas

    old = [int(x) for x in coins]

    pp = price[0]
    gp = price[1]
    ep = abs(price[3])//5*sign(price[3])
    sp = abs(price[3]) % 5*sign(price[3])
    cp = price[4]

    rpp = old[0]-pp
    rgp = old[1]-gp
    rep = old[2]-ep
    rsp = old[3]-sp
    rcp = old[4]-cp

    if rpp < 0:
        rgp += rpp*10
        rpp = 0
    if rgp < 0:
        rep += rgp*2
        rgp = 0
    if rep < 0:
        rsp += rep*5
        rep = 0
    if rsp < 0:
        rcp += rsp*10
        rsp = 0


    if rcp < 0:
        cambio = ceil(-rcp/10)
        rcp += cambio*10
        rsp -= cambio

    if rsp < 0:
        cambio = ceil(-rsp/5)
        rsp += cambio*5
        rep -= cambio

    if rep < 0:
        cambio = ceil(-rep/2)
        rep += cambio*2
        rgp -= cambio


    if rgp < 0:
        cambio = ceil(-rgp/10)
        rgp += cambio*10
        rpp -= cambio


    return [rpp-old[0], rgp-old[1], rep-old[2], rsp-old[3], rcp-old[4]]

def pay_priority2(coins, paid_amt):
    # calcula la diferencia (lo que hay que restarle al dinero original) para pagar paid_amt
    price = gp_to_coin_list(paid_amt, with_electrum=True)
    # pagamos de las monedas mas caras a las mas baratas

    old = [int(x) for x in coins]



    rpp = old[0]-price[0]
    rgp = old[1]-price[1]
    rep = old[2]-price[2]
    rsp = old[3]-price[3]
    rcp = old[4]-price[4]

    if rpp < 0:
        rgp += rpp*10
        rpp = 0
    if rgp < 0:
        rep += rgp*2
        rgp = 0
    if rep < 0:
        rsp += rep*5
        rep = 0
    if rsp < 0:
        rcp += rsp*10
        rsp = 0


    if rcp < 0:
        cambio = ceil(-rcp/10)
        rcp += cambio*10
        rsp -= cambio

    if rsp < 0:
        cambio = ceil(-rsp/5)
        rsp += cambio*5
        rep -= cambio

    if rep < 0:
        cambio = ceil(-rep/2)
        rep += cambio*2
        rgp -= cambio


    if rgp < 0:
        cambio = ceil(-rgp/10)
        rgp += cambio*10
        rpp -= cambio


    return [rpp-old[0], rgp-old[1], rep-old[2], rsp-old[3], rcp-old[4]]





def money_formula(row):
    return sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'👨‍👨‍👧‍👧PJs!M{row}:Q{row}', valueRenderOption="FORMULA").execute().get('values', [])[0]


def money_value(row):
    return sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'👨‍👨‍👧‍👧PJs!M{row}:R{row}', valueRenderOption="FORMATTED_VALUE").execute().get('values', [])[0]


def get_single_val(col, row, valOption):
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=f'👨‍👨‍👧‍👧PJs!{col}{row}', valueRenderOption=valOption).execute()
    # print("result", result)
    return result.get('values', [[]])[0][0]


def update_single_val(col, row, old_value, value):
    new_value = append_to_formula(old_value, value)
    try:
        result2 = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                        range=f'👨‍👨‍👧‍👧PJs!{col}{row}', valueInputOption="USER_ENTERED", body={'values': [[new_value]]}).execute()
        return True
    except:
        return False


def add_single_val(col, row, value):
    old_value = get_single_val(col, row, "FORMULA")
    return update_single_val(col, row, old_value, value)


def dt_formula(row):
    return get_single_val("S", row, "FORMULA")


def dt_value(row):
    return get_single_val("S", row, "FORMATTED_VALUE")


def update_dt(row, old_value, value):
    return update_single_val("S", row, old_value, value)


def add_dt(row, value):
    return add_single_val("S", row, value)


def renown_formula(row):
    return get_single_val("U", row, "FORMULA")


def renown_value(row):
    return get_single_val("U", row, "FORMATTED_VALUE")


def update_renown(row, old_value, value):
    return update_single_val("U", row, old_value, value)


def add_renown(row, value):
    return add_single_val("U", row, value)


def piety_formula(row):
    return get_single_val("W", row, "FORMULA")


def piety_value(row):
    return get_single_val("W", row, "FORMATTED_VALUE")


def update_piety(row, old_value, value):
    return update_single_val("W", row, old_value, value)


def add_piety(row, value):
    return add_single_val("W", row, value)


def experience_formula(row):
    return get_single_val("E", row, "FORMULA")


def experience_value(row):
    return get_single_val("E", row, "FORMATTED_VALUE")


def update_experience(row, old_value, value):
    return update_single_val("E", row, old_value, value)


def add_experience(row, value):
    return add_single_val("E", row, value)


def change_money(row, old_money_list, new_money_amount):
    new_money = new_money_list(
        old_money_list, gp_to_coin_list(new_money_amount))
    return update_money(row, new_money)


def pay_money(row, old_money_formulas, old_money_values, new_money_amount):
    new_money = new_money_list(old_money_formulas, pay_priority(
        old_money_values, new_money_amount))
    return update_money(row, new_money)


def get_pj_name(row):
    try:
        return sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'👨‍👨‍👧‍👧PJs!A{row}', valueRenderOption="FORMATTED_VALUE").execute().get('values', [])[0][0]
    except Exception as e:
        print(e)
        return "ERROR recuperando nombre"




def clean_money(row):
    new_money = money_value(row)[:5]
    return update_money(row, new_money)


def get_reward_info(tier: int):
    xp_gold = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                 range=f'💰Rwrds!H{tier*2}:L{tier*2}', valueRenderOption="FORMATTED_VALUE").execute().get('values', [])[0]
    dt = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'💰Rwrds!O2',
                            valueRenderOption="FORMATTED_VALUE").execute().get('values', [[]])[0][0]

    return (xp_gold, dt)


def check_principado_level(row):
    ren_val = int(renown_value(row))
    principado = "Principado Infernal"
    faction = get_single_val("T", row, "FORMATTED_VALUE")
    if faction == principado:
        if ren_val >= 50:
            return 4
        elif ren_val >= 25:
            return 3
        elif ren_val >= 10:
            return 2
        elif ren_val >= 3:
            return 1

    return 0

def check_is_faction(row, faction_type):
    faction_full_names = {
        "principado":"Principado Infernal",
        "dinastia":"Dinastía Li Hei",
        "conclave":"Conclave de la Raiz",
        "corona":"Corona de la Orden"
    }
    if faction_type not in faction_full_names.keys():
        return False


    row_faction = get_single_val("T", row, "FORMATTED_VALUE")
    return row_faction == faction_full_names(faction_type)

