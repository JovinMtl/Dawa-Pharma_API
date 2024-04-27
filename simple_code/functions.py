def getIndex(chaine:str, sous_chaine:str):
    """THis one will return the index of last caracter of 
    sous_chaine which is in a chaine"""

    
    worth = True
    
    def nextMatch(a, b):
        if a == b:
            return 1
        else:
            return 0
    length_chaine = len(chaine)
    i=0
    j=0
    found = 0
    rep = 0
    urufatiro = sous_chaine[i]
    while (worth and (i < (length_chaine-1)) and (j < len(sous_chaine))):
        print(f"UR: {sous_chaine[j]}")
        print(f"C:{chaine[i]}")
        if sous_chaine[j] == chaine[i]:
            i += 1
            j += 1
            found += 1
        else:
            worth = True
            i += 1
    if (len(sous_chaine) == found):
        return 1
    else:
        return found


print("Hello, we want to execute the function")
chaine = "Thierry Jovin est charmant"
sous_chaine = "est"
print(f"The response is {getIndex(chaine=chaine, sous_chaine=sous_chaine)}")
