from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

#importing my models from Pharma
from pharma.models import UmutiEntree, ImitiSet

# Create your views here.

class EntrantImiti(viewsets.ViewSet):
    """Manages all the Entrant Operations"""

    
    # @action(methods=['get'], detail=False)
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def kurangura(self, request):
        """Kwinjiza umuti nkukwo uwuranguye"""
        dataReceived = request.data
        print(f"The data Received: {request.user}")

        return JsonResponse({"Things ":"well"})
    
    # @action(methods=['get'], detail=False,\
    #          permission_classes= [IsAuthenticated])
    @action(methods=['get'], detail=False)
    def imitiSet(self, request):
        """Compile all the list of the Medicament procured, according
        the Code_umuti and date_echeance"""
        procured = UmutiEntree.objects.all()
        i = 1
        j = 1
        lot = []
        for umutie in procured:
            # print(f"The current UMUTI is {type(umutie)}")
            # print(f"The umuti Code is {umutie.code_umuti}")
            code = umutie.code_umuti
            # umuti.location
            try:
                code_set = ImitiSet.objects.get(code_umuti=code)
            except ImitiSet.DoesNotExist:
                #when the code is new in the ImitiSet
                #we create that entry in the ImitiSet
                # print(f"The Umutie: {umutie}")
                umuti_new = self._umutiMushasha(umutie)
                print(f"the new UMUTI: {umuti_new} : {type(umuti_new)}")
                if str(type(umuti_new)) == "<class 'pharma.models.ImitiSet'>":
                    obj = {
                        'date': (str(umutie.date_uzohererako))[:7],
                        'qte': int(i),
                        'code_operation': str(code)
                    }
                    i += 1
                    lot.append(obj)
                    print(f"The lot: {lot}")
                    umuti_new.lot = str(lot)
                    print(f"Lot assigned: {umuti_new.lot}")
                    umuti_new.save()
            else:
                print(f"THe existing UMUTI: {code_set}")
            
                #mugihe iyo code ihari muri Set
                if ((code_set.lot)[11:18] == (str(umutie.date_uzohererako))[:7]):
                    date_index = getIndex(code_set.lot, (code_set.lot)[11:18]) + 10
                    # current_date = current_lot
                    qte = code_set.lot[date_index]
                    qte_int = int(qte) + 1
                    # code_set.lot[date_index] = '3'
                    # [4] = '9'
                    code = str(code_set.code_umuti)
                    code[4] = 'T'
                    print(f"This is what we already have: {code_set.lot} :\
                          Index: {date_index} ; STR:{(code_set.lot)[:7]}")
                    print(f"Qte: {qte} : {qte_int}")
                    print(f"Code um: {code_set.code_umuti[1]}")
                    # code_set.save()
                else:
                    print(f"Pas egale: {(code_set.lot)[11:18]} et {(str(umutie.date_uzohererako))[:7]}")
                pass

        print(f"The data Received: {request.user}")

        return JsonResponse({"Things ":"well"})
    
    def _umutiMushasha(self, umuti):
        umuti_new = ImitiSet.objects.create()
        umuti_new.code_umuti = str(umuti.code_umuti)
        # print(f"The Sent umuti Code: {umuti.code_umuti}")
        umuti_new.name_umuti = str(umuti.name_umuti)
        umuti_new.description_umuti = str(umuti.description_umuti)
        umuti_new.type_umuti = str(umuti.type_umuti)
        umuti_new.type_in = str(umuti.type_in)
        umuti_new.ratio_type = str(umuti.ratio_type)
        umuti_new.type_out = str(umuti.type_out)
        # imiti_reversed = UmutiEntree.objects.filter(code_umuti=umuti_new.code_umuti)[-1]
        # last_umuti = imiti_reversed[0]
        umuti_new.price_in = str(umuti.price_in)
        umuti_new.quantite_restant = str(umuti.quantite_restant)
        umuti_new.location = str(umuti.location)
        umuti_new.lot = str('')

        umuti_new.save()
        print("saving")

        return umuti_new

# class 
def getIndex(chaine:str, sous_chaine:str):
    """THis one will return the index of last caracter of 
    sous_chaine which is in a chaine of type STRING.
    
    RETURNS index or 0
    """

    worth = True
    length_chaine = len(chaine)
    i=0 #counter for chaine
    j=0 #counter for sous_chaine
    found = 0 #the number of occurence
    while (worth and (i < length_chaine) and (j < len(sous_chaine))):
        if sous_chaine[j] == chaine[i]:
            i += 1
            j += 1
            found += 1
        else:
            i += 1
    if (len(sous_chaine) == found):
        return i
    else:
        return 0



