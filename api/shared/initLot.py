

def init_lot(umuti)->list:
    obj = {
            'date': (str(umuti.date_peremption))[:7],
            'qte': int(umuti.quantite_restant),
            'code_operation': [
                        { 
                            str(umuti.code_operation) : int(umuti.quantite_restant)
                        }
                    ],
            'to_panier': 0
        }
    return [obj]