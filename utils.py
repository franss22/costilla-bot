from math import ceil

from nextcord import SlashOption

default_user_option = SlashOption(
    name="usuario-target",
    description="Usuario al que se le aplica el comando",
    required=False,
    default=None,
)


def sign(num: int | float) -> int:
    return 1 if num >= 0 else -1


def parse_float_arg(num: str) -> float:
    rnum = num.replace(",", ".")
    try:
        return float(rnum)
    except ValueError:
        raise ValueError(f"{num} no es un número válido")


def gp_to_coin_list(num: float) -> list[int]:
    """Given an amount of gold, returns its representation in coins, minimizing the total amount of coins."""

    num = (1 if num >= 0 else -1) * int(round(abs(float(num)) * 100))

    pp = num // 1000
    gp = num % 1000 // 100
    sp = num % 100 // 10
    cp = num % 10

    return [pp, gp, sp, cp]


def check_results(DC: int, result: int, dice: int) -> int:
    """Given a DC, a dice result (with bonuses), and the unmodified result of the dice,
    returns the degree of success of the check, from 0 (crit fail) to 3 (crit success).
    """
    CHECK_RESULTS = {
        -1: 0,
        0: 0,  # crit fail
        1: 1,  # fail
        2: 2,  # success
        3: 3,  # crit success
        4: 3,
    }
    return CHECK_RESULTS[
        (
            (
                0
                if result <= DC - 10
                else (1 if result < DC else (2 if result < DC + 10 else 3))
            )
            + (1 if dice == 20 else 0)
            - (1 if dice == 1 else 0)
        )
    ]


def result_name(result: int) -> str:
    """Given a success value from 0 to 3,
    returns the string name representation of the success degree."""
    return ["fallo crítico", "fallo", "éxito", "éxito crítico"][result]


def pay_priority(coins: list[int], paid_amt: float) -> list[int]:
    """Given a list of coins (pp, gp, sp, cp) and an amount of gold to be paid,
    returns the amount of coins of each type that should be paid.
    """
    # calcula la diferencia (lo que hay que restarle al dinero original) para pagar paid_amt
    price = gp_to_coin_list(paid_amt)
    # pagamos de las monedas mas caras a las mas baratas
    old = [int(float(x)) for x in coins]
    vals = [10, 10, 10, 10]

    resta = [old[i] - price[i] for i in range(5)]

    # convierte monedas pequeñas en monedas grandes
    for i in range(4):
        if resta[i] < 0:
            resta[i + 1] += resta[i] * vals[i]
            resta[i] = 0

    # convierte las monedas grandes en monedas pequeñas
    for j in range(4, 0, -1):
        if resta[j] < 0:
            cambio = ceil(-resta[j] / vals[j - 1])
            resta[j] += cambio * vals[j - 1]
            resta[j - 1] -= cambio

    return [resta[i] - old[i] for i in range(5)]


def num_to_column(column_int: int) -> str:
    if column_int <= 0:
        raise ValueError("Column must be 1 or higher.")
    start_index = 1  # it can start either at 0 or at 1
    letter = ""
    while column_int > 25 + start_index:
        letter += chr(65 + int((column_int - start_index) / 26) - 1)
        column_int = column_int - (int((column_int - start_index) / 26)) * 26
    letter += chr(65 - start_index + (int(column_int)))
    return letter


def column_to_num(column: str) -> int:
    letters: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()
    num: int = 0
    for letter in column.lower():
        if letter not in letters:
            raise ValueError("Column must have only roman alphabet characters.")
        num *= len(letters)
        num += letters.index(letter) + 1

    return num - 1
