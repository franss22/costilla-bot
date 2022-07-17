from math import ceil


def sign(num):
    return 1 if num >= 0 else -1


def gp_to_coin_list(num: float, with_electrum=False):

    num = (1 if num >= 0 else -1)*int(round(abs(float(num))*100))

    pp = num//1000
    gp = num % 1000//100
    ep = 0
    sp = num % 100//10
    cp = num % 10
    if with_electrum:
        ep = sp//5
        sp = sp % 5

    return [pp, gp, ep, sp, cp]


def pay_priority(coins, paid_amt: float):
    # calcula la diferencia (lo que hay que restarle al dinero original) para pagar paid_amt
    price = gp_to_coin_list(paid_amt, with_electrum=True)
    # pagamos de las monedas mas caras a las mas baratas
    old = [int(float(x)) for x in coins]
    vals = [10, 2, 5, 10]

    resta = [old[i]-price[i] for i in range(5)]

    # magia negra
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


def numToColumn(column_int):
    start_index = 1  # it can start either at 0 or at 1
    letter = ''
    while column_int > 25 + start_index:
        letter += chr(65 + int((column_int-start_index)/26) - 1)
        column_int = column_int - (int((column_int-start_index)/26))*26
    letter += chr(65 - start_index + (int(column_int)))
    return letter


def renown_tier(renown_val: int):
    if renown_val >= 50:
        return 4
    elif renown_val >= 25:
        return 3
    elif renown_val >= 10:
        return 2
    elif renown_val >= 3:
        return 1


class FACTION:
    @classmethod
    def has_value(cls, value):
        return value in cls.__dict__.values()

    dinastia    = "Dinastía Li Hei"
    principado  = "Principado Infernal"
    conclave    = "Conclave de la Raiz"
    corona      = "Corona de la Orden"
    
    dinastia_short    = "dinastia"
    principado_short  = "principado"
    conclave_short    = "conclave"
    corona_short      = "corona"

    @classmethod
    def full_name(cls, short_name: str):
        return {
            "principado": cls.principado,
            "dinastia": cls.dinastia,
            "conclave": cls.conclave,
            "corona": cls.corona
        }[short_name]
