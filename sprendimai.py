"""Pavyzdiniai sprendimai mokytojui.

Kiekviena funkcija grąžina erdvę (dict), kurią galima perduoti
`kortele._ivertink(lygis, erdve)`. Testai tuo naudojasi, kad patikros ir
atsakymai niekada neišsiskirtų.
"""

import random

from kortele import rodyk_kortele


def sprendimas_1():
    vardas = "Birutė"
    amzius = 17
    svajoniu_projektas = "robotas, kuris tvarko kambarį"
    faktas = "turiu du šunis"

    rodyk_kortele(vardas, amzius, svajoniu_projektas, faktas)
    return {"vardas": vardas, "amzius": amzius, "svajoniu_projektas": svajoniu_projektas, "faktas": faktas}


def sprendimas_2():
    erdve = sprendimas_1()
    pomegiai = ["krepšinis", "fotografija", "animė"]

    rodyk_kortele(erdve["vardas"], erdve["amzius"], erdve["svajoniu_projektas"], erdve["faktas"],
                  pomegiai=pomegiai)
    erdve["pomegiai"] = pomegiai
    return erdve


def sprendimas_3():
    erdve = sprendimas_2()
    slapyvardis = f"{erdve['vardas'][:3].upper()}-{erdve['amzius'] * 2}"

    rodyk_kortele(erdve["vardas"], erdve["amzius"], erdve["svajoniu_projektas"], erdve["faktas"],
                  pomegiai=erdve["pomegiai"], slapyvardis=slapyvardis)
    erdve["slapyvardis"] = slapyvardis
    return erdve


def slapyvardis_is(vardas, amzius):
    """4 lygio a) variantas."""
    return f"{vardas[:3].upper()}-{amzius * 2}"


def sprendimas_4():
    erdve = sprendimas_3()
    faktai = ["turiu du šunis", "moku žongliruoti", "buvau Islandijoje"]

    rodyk_kortele(erdve["vardas"], erdve["amzius"], erdve["svajoniu_projektas"],
                  random.choice(faktai),
                  pomegiai=erdve["pomegiai"], slapyvardis=erdve["slapyvardis"],
                  tema="matrix")
    erdve["slapyvardis_is"] = slapyvardis_is
    erdve["random"] = random
    erdve["faktai"] = faktai
    return erdve
