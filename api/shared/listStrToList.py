

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
        if int(dat):
            data3.append(int(dat))

    return(data3)
    
def listIntSomme(data: list):
    """This function returns the sum of the Int list"""
    data2 = 0
    for dat in data:
        if int(dat):
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
        if int(dat['qte_restant']):
            data2 += int (dat['qte_restant'])
    return (data2)

def listDictIntSomme2(data:list)->int:
    """ THis function will return the sum of the int values contained 
    in a list of dict of type:
    data = [
        {'a': 5},
        {'b': 81}
    ]
    """
    dict_val = 0
    for dat in data:
        if int((str(dat.values())).split('[')[1].split(']')[0]):
            dict_val += int((str(dat.values())).split('[')[1].split(']')[0])
    print(dict_val)


# listStrToList()
# listIntToList()
# listIntSomme()
# listDictIntSomme()
# listDictIntSomme2()