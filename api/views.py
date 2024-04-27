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
    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def imitiSet(self, request):
        """Compile all the list of the Medicament procured, according
        the Code_umuti and date_echeance"""
        procured = UmutiEntree.objects.all()
        i = 1
        j = 1
        lot = []
        for umuti in procured:
            code = umuti.code_umuti
            umuti.location
            try:
                code_set = ImitiSet.objects.get(code_umuti=code)
            except ImitiSet.DoesNotExist:
                #when the code is new in the ImitiSet
                #we create that entry in the ImitiSet
                umuti_new = self._umutiMushasha(umuti=umuti)
                if type(umuti_new) == 'ImitiSet':
                    obj = {
                        'date': (str(umuti.date_uzohererako))[:7],
                        'qte': int(i),
                        'code_operation': str(code)
                    }
                    i += 1
                    lot.append(obj)
                    umuti_new.lot = lot
                    umuti_new.save()
            else:
                #mugihe iyo code ihari muri Set
                if ((code_set.lot)[:7] == (str(umuti.date_uzohererako))[:7]):
                    date_index = getIndex(code_set.lot, (code_set.lot)[:7]) + 3
                    # current_date = current_lot
                    print(f"This is what we already have: {code_set.lot} :\
                          Index: {date_index} ; STR:{(code_set.lot)[:7]}")
                pass

        print(f"The data Received: {request.user}")

        return JsonResponse({"Things ":"well"})
    
    def _umutiMushasha(self, umuti):
        umuti_new = ImitiSet.objects.create()
        umuti_new.code_umuti = str(umuti.umuti_code)
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



