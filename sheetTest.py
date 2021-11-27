from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from urllib.error import HTTPError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = "keys.json"

creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SPREADSHEET_ID = '1VvS-iQVp_Udi3cwv3kbJ0a2dNEfKLoJhMbklXv9WkiU'

service = build('sheets', 'v4', credentials= creds)
sheet = service.spreadsheets()


def search_pj_row(pj_id):
    item = [pj_id]
    id_row = None
    try:
        id_row = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='👨‍👨‍👧‍👧PJs!B:B').execute().get('values').index(item)+1
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
    return 1 if num>= 0 else -1

def num_to_coin_list(num):
    anum = abs(float(num))

    return [int(anum)//10*sign(num), int(anum)//1%10*sign(num), 0, int(anum*10)//1%10*sign(num), int(anum*100)//1%10*sign(num)]


def new_money_list(old_money, add_list):
    return list(map(append_to_formula, old_money, add_list))

def update_money(row, new_money):
    try:
        result2= sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f'👨‍👨‍👧‍👧PJs!M{row}', valueInputOption="USER_ENTERED", body={'values':[new_money]}).execute()
        return True
    except:
        return False

    

def pay_priority(coins, paid_amt):
    separate_price = num_to_coin_list(paid_amt)
    #pagamos de las monedas mas caras a las mas baratas
    oldpp= int(coins[0])
    oldgp= int(coins[1])
    oldep= int(coins[3])
    oldsp= int(coins[3])
    oldcp= int(coins[4])

    pp= separate_price[0]
    gp= separate_price[1]
    ep= separate_price[3]//5
    sp= separate_price[3]%5
    cp= separate_price[4]
    fpp= 0
    fgp= 0
    fep= 0
    fsp= 0
    fcp= 0
    #vemos que nos alcanzen las monedas mas caras, y vamos bajando
    
    fpp = max(0, oldpp-pp)-oldpp
    pp = max(0, pp-oldpp)
    gp += pp*10

    fgp = max(0, oldgp-gp)-oldgp
    gp = max(0, gp-oldgp)
    ep += gp*2

    fep = max(0, oldep-ep)-oldep
    ep = max(0, ep-oldep)
    sp += ep*5

    fsp = max(0, oldsp-sp)-oldsp
    sp = max(0, sp-oldsp)
    cp += sp*10

    fcp = max(0, oldcp-cp)-oldcp

    return [fpp, fgp, fep, fsp, fcp]





def money_formula(row):
    return sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'👨‍👨‍👧‍👧PJs!M{row}:Q{row}', valueRenderOption="FORMULA").execute().get('values', [])[0]
def money_value(row):
    return sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'👨‍👨‍👧‍👧PJs!M{row}:R{row}', valueRenderOption="FORMATTED_VALUE").execute().get('values', [])[0]



def dt_formula(row):
    return sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'👨‍👨‍👧‍👧PJs!S{row}', valueRenderOption="FORMULA").execute().get('values', [])[0][0]
def dt_value(row):
    return sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'👨‍👨‍👧‍👧PJs!S{row}', valueRenderOption="FORMATTED_VALUE").execute().get('values', [])[0][0]


def update_dt(row, old_value, value):
    new_value = append_to_formula(old_value, value)
    try:
        result2= sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f'👨‍👨‍👧‍👧PJs!S{row}', valueInputOption="USER_ENTERED", body={'values':[[new_value]]}).execute()
        return True
    except:
        return False

def change_money(row, old_money_list, new_money_amount):
    new_money = new_money_list(old_money_list, num_to_coin_list(new_money_amount))
    return update_money(row, new_money)

def pay_money(row, old_money_formulas, old_money_values, new_money_amount):
    new_money = new_money_list(old_money_formulas, pay_priority(old_money_values, new_money_amount))
    return update_money(row, new_money)

def get_pj_name(row):
    try:
        return sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'👨‍👨‍👧‍👧PJs!A{row}', valueRenderOption="FORMATTED_VALUE").execute().get('values', [])[0][0]
    except HttpError:
        return "ERROR recuperando nombre"

    
# print(get_dt(5))
# print(get_pj_name(5))