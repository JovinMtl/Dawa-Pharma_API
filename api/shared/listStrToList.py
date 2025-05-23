
import os
from datetime import date, datetime

def listStrToList(data:str):
    """ THis function takes a String of list of Str and converts it into
      a real list"""
    # data = "['xt10', 'xt11', 'xt12']"
    data1 = data.replace('[',"").replace(']','').replace("'",",", -1)
    data2 = data1.split(',')
    data3 = []
    # print(f"The result {data2}")
    for dat in data2:
        if len(dat) > 1:
            # print(dat)
            data3.append(dat)
    return data3


def listIntToList(data:str):
    """ THis function takes a String of list of Int and converts it into
      a real list"""
    data1 = data.replace('[',"").replace(']','').replace("'",",", -1)
    data2 = data1.split(',')
    data3 = []
    for dat in data2:
        if float(dat):
            data3.append(float(dat))

    return(data3)
    
def listIntSomme(data: list):
    """This function returns the sum of the Int list"""
    data2 = 0
    for dat in data:
        if float(dat):
            data2 += dat
    return (data2)

def listDictIntSomme(data:list):
    """This function returns the sum of the Int keys contained in
    a dictionary.
    data = [{'code_operation': 'xt10', 'qte_restant': 5}, 
            {'code_operation': 'xt11', 'qte_restant': 5}, 
            {'code_operation': 'xt12', 'qte_restant': 4}]
    """
    data2 = 0
    
    for dat in data:
        if float(dat['qte_restant']):
            data2 += float (dat['qte_restant'])
    return (data2)

def listDictIntSomme2(data:list)->float:
    """ THis function will return the sum of the int values contained 
    in a list of dict of type:
    data = [
        {'a': 5},
        {'b': 81}
    ]
    """
    
    dict_val = 0
    for dat in data:
        if float((str(dat.values())).split('[')[1].split(']')[0]):
            dict_val += float((str(dat.values())).split('[')[1].split(']')[0])
    
    # print(f"The code operation is : {data} and the answer is {dict_val}")
    return (dict_val)

def listDictIntSomme3( data:list):
    """ This function returns the sum of the list of dict of this type:

        data = [{'date': '2024-06', 'qte': 9, 
                'code_operation': [{'xt10': 4}, 
                {'xt11': 5}], 'to_panier': 0}, 
                {'date': '2025-08', 'qte': 6, 
                'code_operation': [{'xt12': 6}], 'to_panier': 0}]
    
    """
    data2 = 0
    for dat in data:
        try:
            print(dat['qte'],  file=open(os.devnull, 'w'))
        except KeyError:
            pass
        else:
            data2 += dat['qte']
    
    return (data2)

def _assess_order(code_umuti:str, code_operatio:list) -> list:
        """ THis function will take a list of object of this kind:
    
                    code_operation = [{'xt10': 2}, {'xt11': 5}]
            coupled with :  code_umuti = 'AL123'
           and return a  list of str and int of this kind:
            [['AL123', 'xt10', 2], ['AL123', 'xt11', 5]]
        """
        data = []
        code_operation = code_operatio.copy()
        for obj in code_operation:
            code = (str(obj)).replace('[',"").replace(']','').\
                replace("'",",", -1).split(',')[1]
            qte = float((str(obj)).replace('[',"").replace(']','').\
                replace("'",",", -1).split(" ")[1].split('}')[0])
            
            data.append([code_umuti, code, qte])
        
        return data

def __place_order(data:list, qte:int) -> list:
    """ The function takes a list of order and make a repartition of qte
    based on input data of this type:
        data = [['AL123', 'xt10', 2], ['AL123', 'xt11', 5]]

        with: qte = 1

    and return :  [['AL123', 'xt10', 1], ['AL123', 'xt11', 0]]
    """
    reste = 0
    if qte < 1:
        return []
    for dat in data:
        if (qte > dat[2]) and (reste == 0):
            reste = qte - dat[2]
            qte = reste
        elif (qte <= dat[2]) and (reste != -1):
            dat[2] = qte
            reste = -1
            qte = 0
        elif reste == -1:
            dat[2] = 0
        else:
            return ['Empty',]
    
    return data


def _giveDate(date_winjiriyeko:str)-> str:
        """THis function checkes that an date isoString is given 
        from Javascript and then converts it to real python date object."""
        if date_winjiriyeko:
            return datetime(date_winjiriyeko)
        else:
            today = datetime.now()
            return today
            
    


# listStrToList()
# listIntToList()
# listIntSomme()
# listDictIntSomme()
# listDictIntSomme2()
# listDictIntSomme3()
# _assess_order()
# __place_order()

_giveDate('')