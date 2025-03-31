
def roundNumber(val:int=0)->int:
    principe = 1
    if val <= 1000:
        principe = 100
        product = round(val / principe)
        result = product * principe
        return result
    elif val <= 10000:
        principe = 500
    elif val > 10000:
        principe = 1000
    product = int(val / principe) + 1
    result = product * result

    return result