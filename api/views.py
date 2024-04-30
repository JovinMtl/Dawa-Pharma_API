from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

import json
from django.utils import timezone

#importing my models from Pharma
from pharma.models import UmutiEntree, ImitiSet, UmutiSold

#importing the serializers
from .serializers import ImitiSetSeriazer

#importing my code generator
from .code_generator import GenerateCode

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
    def compileImitiSet(self, request=None):
        """Compile all the list of the Medicament procured, according
        the Code_umuti and date_echeance"""
        procured = UmutiEntree.objects.all()
        i = 1
        j = 1
        lot = []
        for umutie in procured:
            code = umutie.code_umuti
            try:
                code_set = ImitiSet.objects.get(code_umuti=code)
            except ImitiSet.DoesNotExist:
                #when the code is new in the ImitiSet
                #we create that entry in the ImitiSet
                umuti_new = self._umutiMushasha(umutie)
                print(f"the new UMUTI: {umuti_new} : {type(umuti_new)}")
                if str(type(umuti_new)) == "<class 'pharma.models.ImitiSet'>":
                    obj = {
                        'date': (str(umutie.date_uzohererako))[:7],
                        'qte': int(umutie.quantite_restant),
                        'code_operation': str(umutie.code_operation)
                    }
                    arr = []
                    arr.append(obj)
                    jove = json.dumps(obj=arr)
                    umuti_new.lot = jove
                    umuti_new.save()
            else:
                print(f"THe existing UMUTI: {code_set}")
                #mugihe iyo code ihari muri Set
                lot = code_set.lot
                saved_lot = json.loads(lot)
                print(f"The Saved lot {lot} ; type {type(lot)}")
                print(f"The converted: {saved_lot} of type: {type(saved_lot)}")
                i = 0
                j = 0
                for lote in saved_lot:
                    if lote.get('date') == (str(umutie.date_uzohererako))[:7]:
                        lote.qte += umutie.quantite_restant
                        j += 1
                    print(f"The lote : {lote} of type {type(lote)}")
                if not j:
                    obj = {
                        'date': (str(umutie.date_uzohererako))[:7],
                        'qte': int(umutie.quantite_restant),
                        'code_operation': str(umutie.code_operation)
                    }
                    i += 1
                    saved_lot.append(obj)
                code_set.quantite_restant += umutie.quantite_restant
                code_set.lot = saved_lot
                code_set.save()
                print(f"The now lot: {code_set.lot}")

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
        umuti_new.quantite_restant = int(umuti.quantite_restant)
        umuti_new.location = str(umuti.location)
        umuti_new.lot = str('')

        umuti_new.save()
        print("saving")

        return umuti_new



class ImitiOut(viewsets.ViewSet):
    """THis will give informations about the Imiti in the Store 
    or etagere"""

    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def dispo(self, request):
        imiti = ImitiSet.objects.all().order_by('name_umuti')
        imitiSerialized = ImitiSetSeriazer(imiti, many=True)

        if imitiSerialized.is_valid:
            return Response(imitiSerialized.data)

        return JsonResponse({"THings are":"okay"})
    

    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def sell(self, request):
        data_query = request.data
        bundle = data_query
        for actual in bundle:
            code_umuti = actual.get('code_umuti')
            code_operation = actual.get('code_operation')
            qte = actual.get('qte')
            try:
                umuti = UmutiEntree.objects.\
                    filter(code_umuti=code_umuti).\
                    filter(code_operation=code_operation)
            except UmutiEntree.DoesNotExist:
                pass
            else:
                #can now perfom the Vente operation
                print(f"The Umuti found : {umuti}")
                sold = self._imitiSell(umuti=umuti, qte=qte, operator=request.user)
                if sold == 200:
                    print(f"Umuti {umuti.code_umuti} is sold")

        #  after sell then call compile
        imiti = EntrantImiti()
        jove = imiti.compileImitiSet()
        print(f"La reponse de vente est: {jove}")

        return JsonResponse({"It is":"Okay"})
    
    def _imitiSell(umuti:UmutiEntree, qte:int, operator:str):
        """Will substract the quantite_restante in UmutiEntree and
        write a new instance of UmutiSell"""
        reference_umuti = ImitiSet.objects.get(code_umuti=umuti.code_umuti)
        new_vente = UmutiSold.objects.create()
        new_vente.code_umuti = umuti.code_umuti
        new_vente.name_umuti = umuti.name_umuti
        new_vente.quantity = qte
        new_vente.price_out = reference_umuti.price_out
        new_vente.code_operation_entrant = umuti.code_operation
        new_vente.code_operation = GenerateCode.gene(12)
        new_vente.operator = operator
        new_vente.date_operation = timezone.now()
        umuti.quantite_restant -= qte
        
        return 200
