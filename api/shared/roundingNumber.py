
#  Written on March 31, 2025. Thierry Nsanzumukiza.
#  muteule Jove.

def roundNumber(val:int=0)->int:
    principe = 1
    product = 1
    if val <= 1000:
        principe = 100
        product = round(val / principe)
        result = product * principe
        return result
    elif val <= 10000:
        principe = 500
    elif val > 10000:
        principe = 1000

    if (int(val / principe)) == (val / principe):
        product = val / principe
    else:
        product = int(val / principe) + 1
        
    result = product * principe

    return result