from math import ceil
import random

def sign(num):
    return 1 if num >= 0 else -1


def gp_to_coin_list(num: float):

    num = (1 if num >= 0 else -1)*int(round(abs(float(num))*100))

    pp = num//1000
    gp = num % 1000//100
    sp = num % 100//10
    cp = num % 10

    return [pp, gp, sp, cp]


def check_results(DC, result, dice):
    CHECK_RESULTS = {
    -1:0,
    0:0, # crit fail
    1:1, # fail
    2:2, # success
    3:3, # crit success
    4:3
}
    return CHECK_RESULTS[((0 if result<=DC-10 else (1 if result<DC else (2 if result<DC+10 else 3))) + (1 if dice==20 else 0) - (1 if dice==1 else 0))]

def result_name(result:int):
    return ["fallo crítico", "fallo", "éxito", "éxito crítico"][result]

def pay_priority(coins, paid_amt: float):
    # calcula la diferencia (lo que hay que restarle al dinero original) para pagar paid_amt
    price = gp_to_coin_list(paid_amt, with_electrum=True)
    # pagamos de las monedas mas caras a las mas baratas
    old = [int(float(x)) for x in coins]
    vals = [10, 10, 10, 10]

    resta = [old[i]-price[i] for i in range(5)]

    # convierte monedas pequeñas en monedas grandes
    for i in range(4):
        if resta[i] < 0:
            resta[i+1] += resta[i]*vals[i]
            resta[i] = 0

    # convierte las monedas grandes en monedas pequeñas
    for j in range(4, 0, -1):
        if resta[j] < 0:
            cambio = ceil(-resta[j]/vals[j-1])
            resta[j] += cambio*vals[j-1]
            resta[j-1] -= cambio

    return [resta[i]-old[i] for i in range(5)]


def numToColumn(column_int):
    start_index = 1  # it can start either at 0 or at 1
    letter = ''
    while column_int > 25 + start_index:
        letter += chr(65 + int((column_int-start_index)/26) - 1)
        column_int = column_int - (int((column_int-start_index)/26))*26
    letter += chr(65 - start_index + (int(column_int)))
    return letter


def renown_tier(renown_val: int):
    renown_val = int(renown_val)
    if renown_val >= 50:
        return 4
    elif renown_val >= 25:
        return 3
    elif renown_val >= 10:
        return 2
    elif renown_val >= 3:
        return 1
    else:
        return 0
