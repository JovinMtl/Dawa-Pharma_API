
def roundNumber(val:int=0)->int:
    principe = 1
    if val < 1000:
        return val
    elif val <= 10000:
        principe = 500
    elif val > 10000:
        principe = 1000
    product = int(val / principe) + 1
    result = product * result

    return result