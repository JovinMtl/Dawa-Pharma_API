


def superiorInput(func, val_achat:int=0, val_vente:int=0)->int:
    minimum_vente = int(func.objects.all()[0].minimum_vente)
    if (val_vente > (minimum_vente * val_achat)):
        return val_vente
    else:
        return minimum_vente * val_achat