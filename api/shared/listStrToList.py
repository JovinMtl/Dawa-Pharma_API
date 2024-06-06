

def listStrToList(data:str):
    """ THis function takes a String of list and converts it into
      a real list"""
    # data = "['xt10', 'xt11', 'xt12']"
    data1 = data.replace('[', '').replace(']','').replace("'",'')
    data2 = data1.split(',')
    print(f"The result {data2}")
