from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from math import ceil
import os
import json
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# SERVICE_ACCOUNT_FILE = "google-credentials.json"
# creds = service_account.Credentials.from_service_account_file(
# SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# SPREADSHEET_ID = '1gPknOWaAWmaeUAs6UTG6yC_ad8f5RT85Y72-hWHbuqM'

# service = build('sheets', 'v4', credentials=creds)
# sheet = service.spreadsheets()


def sign(num):
    return 1 if num >= 0 else -1


def gp_to_coin_list(num:float, with_electrum=False):

    num = (1 if num >= 0 else -1)*int(round(abs(float(num))*100))

    pp = num//1000
    gp = num % 1000//100
    ep = 0
    sp = num % 100//10
    cp = num % 10
    if with_electrum:
        ep = sp//5
        sp = sp%5

    return [pp, gp, ep, sp, cp]


def pay_priority(coins, paid_amt):
    # calcula la diferencia (lo que hay que restarle al dinero original) para pagar paid_amt
    price = gp_to_coin_list(paid_amt, with_electrum=True)
    # pagamos de las monedas mas caras a las mas baratas
    old = [int(x) for x in coins]
    vals = [10, 2, 5, 10]

    resta = [old[i]-price[i] for i in range(5)]

    #magia negra
    for i in range(4):
        if resta[i] < 0:
            resta[i+1] += resta[i]*vals[i]
            resta[i] = 0

    for j in range(1, 5, -1):
        if resta[i] < 0:
            cambio = ceil(-resta[i])
            resta[i] += cambio*10
            resta[i-1] -= cambio

    return [resta[i]-old[i] for i in range(5)]

