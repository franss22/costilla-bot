from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from urllib.error import HTTPError
from math import ceil
import decimal as dec
import os
import json
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = "keys.json"
creds = None


print("generating config vars")

if os.path.exists(SERVICE_ACCOUNT_FILE):
    print("generating creds from file")
    creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
else:
    print("generating creds from config vars")
    info = json.loads({ 
    "type": "service_account",
    "project_id": "sheets-333321",
    "private_key_id": os.environ.get('private_key_id'),
    "private_key": os.environ.get('private_key'),
    "client_email": "costillabot@sheets-333321.iam.gserviceaccount.com",
    "client_id": os.environ.get('client_id'),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/costillabot%40sheets-333321.iam.gserviceaccount.com"
    })
    print(info)
    creds = service_account.Credentials.from_service_account_info(info)







SPREADSHEET_ID = '1gPknOWaAWmaeUAs6UTG6yC_ad8f5RT85Y72-hWHbuqM'

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()


def search_pj_row(pj_id):
    item = [pj_id]
    id_row = None
    try:
        id_row = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range='👨‍👨‍👧‍👧PJs!B:B').execute().get('values').index(item)+1
    except ValueError as e:
        pass
    return id_row


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


def valid_num(appnd):
    try:
        float(appnd)
        return True
    except:
        return False


def sign(num):
    return 1 if num >= 0 else -1


def num_to_coin_list(num):

    anum = int(round(abs(float(num))*100))
    # #print(anum)
    pp = sign(num)*anum//1000
    gp = sign(num)*anum % 1000//100
    sp = sign(num)*anum % 100//10
    cp = sign(num)*anum % 10

    return [pp, gp, 0, sp, cp]


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
    separate_price = num_to_coin_list(paid_amt)
    # pagamos de las monedas mas caras a las mas baratas
    oldpp = int(coins[0])
    oldgp = int(coins[1])
    oldep = int(coins[2])
    oldsp = int(coins[3])
    oldcp = int(coins[4])

    pp = separate_price[0]
    gp = separate_price[1]
    ep = abs(separate_price[3])//5*sign(separate_price[3])
    sp = abs(separate_price[3]) % 5*sign(separate_price[3])
    cp = separate_price[4]
    # print(separate_price)

    # rpp = max(0, oldpp-pp)
    # rgp = max(0, oldgp-gp) + min(0, (oldpp-pp)*10)
    # rep = max(0, oldep-ep) + min(0, (oldgp-gp)*2)
    # rsp = max(0, oldsp-sp) + min(0, (oldep-ep)*5)
    # rcp = oldcp-cp + min(0, (oldsp-sp)*10)

    rpp = oldpp-pp
    rgp = oldgp-gp
    rep = oldep-ep
    rsp = oldsp-sp
    rcp = oldcp-cp
    #print([rpp, rgp, rep, rsp, rcp])

    if rpp < 0:
        rgp += rpp*10
        #print("changed rgp to", rgp)
        rpp = 0
    if rgp < 0:
        rep += rgp*2
        #print("changed rep to", rep)
        rgp = 0
    if rep < 0:
        rsp += rep*5
        #print("changed rsp to", rsp)
        rep = 0
    if rsp < 0:
        rcp += rsp*10
        #print("changed rcp to", rcp)
        rsp = 0

    #print([rpp, rgp, rep, rsp, rcp])

    if rcp < 0:
        cambio = ceil(-rcp/10)
        #print("cambio de cp a sp)", cambio)
        rcp += cambio*10
        rsp -= cambio
        #print(rcp, rsp)

    if rsp < 0:
        cambio = ceil(-rsp/5)
        #print("cambio de sp a ep)", cambio)
        rsp += cambio*5
        rep -= cambio
        #print(rsp, rep)

    if rep < 0:
        cambio = ceil(-rep/2)
        #print("cambio de ep a gp)", cambio)
        rep += cambio*2
        rgp -= cambio
        #print(rep, rgp)

    if rgp < 0:
        cambio = ceil(-rgp/10)
        #print("cambio de gp a pp)", cambio)
        rgp += cambio*10
        rpp -= cambio
        #print(rgp, rpp)

    return [rpp-oldpp, rgp-oldgp, rep-oldep, rsp-oldsp, rcp-oldcp]


# print("dinero al final", pay_priority([1,0,0,0,0], 0.01))

# #print(num_to_coin_list(9.12))


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
        old_money_list, num_to_coin_list(new_money_amount))
    return update_money(row, new_money)


def pay_money(row, old_money_formulas, old_money_values, new_money_amount):
    new_money = new_money_list(old_money_formulas, pay_priority(
        old_money_values, new_money_amount))
    return update_money(row, new_money)


def get_pj_name(row):
    try:
        return sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'👨‍👨‍👧‍👧PJs!A{row}', valueRenderOption="FORMATTED_VALUE").execute().get('values', [])[0][0]
    except HttpError:
        return "ERROR recuperando nombre"


# #print(get_dt(5))
# #print(get_pj_name(5))


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
