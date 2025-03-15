


def superiorInput(func, val:int=0)->int:
    minimum_vente = int(func.objects.all()[0].minimum_vente)
    return minimum_vente * val