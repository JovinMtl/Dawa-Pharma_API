


def superiorInput(func, val_achat:int=0, val_vente:int=0)->int:
    try:
        a = int(val_achat)
        b = int(val_vente)
    except ValueError:
        return 0
    minimum_vente = int(func.objects.all()[0].ben)
    if (val_vente > (minimum_vente * val_achat)):
        return val_vente
    else:
        return minimum_vente * val_achat