
def give_sync_code(val:int=0)->int:
    vals = [1, 2, 3, 4, 5]
    len_vals = len(vals)
    if val < len_vals:
        return vals[val]
    return 0