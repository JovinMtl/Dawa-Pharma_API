from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

import json
from django.utils import timezone
from datetime import timedelta

#importing my models from Pharma
from pharma.models import UmutiEntree, ImitiSet, UmutiSold

#importing the serializers
from .serializers import ImitiSetSeriazer

#importing my additional code
from .code_generator import GenerateCode
from .shared.stringToList import StringToList

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
                umuti_set = ImitiSet.objects.get(code_umuti=code)
                umuti_set.quantite_restant = 0
                # umuti_set.qte_entrant_big = 0
            except ImitiSet.DoesNotExist:
                #when the code is new in the ImitiSet
                #we create that entry in the ImitiSet
                umuti_new = self._umutiMushasha(umutie)
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
                # print(f"THe existing UMUTI: {umuti_set}")
                #mugihe iyo code ihari muri Set
                lot = umuti_set.lot
                lot_string = StringToList(umuti_set.lot)
                #the string of list must be made into json
                lot_list = lot_string.toList()
                i = 0
                j = 0
                for lote in lot_list:
                    if lote.get('date') == (str(umutie.date_uzohererako))[:7]:
                        lote['qte'] += umutie.quantite_restant
                        j += 1
                    
                if not j:
                    obj = {
                        'date': (str(umutie.date_uzohererako))[:7],
                        'qte': int(umutie.quantite_restant),
                        'code_operation': str(umutie.code_operation)
                    }
                    i += 1
                    lot_list.append(obj)
                umuti_set.quantite_restant += umutie.quantite_restant
                umuti_set.lot = lot_list
                last_date = self._findLastDate(code_umuti=umuti_set.code_umuti)
                if last_date:
                    umuti_set.date_last_vente = last_date
                #checking if there is qte_entrant bigger than before
                if (int(umuti_set.qte_entrant_big)) < (int(umutie.quantite_initial)):
                    umuti_set.qte_entrant_big = int(umutie.quantite_initial)
                    print(f"The Umutie is bigger {umutie.quantite_initial}\
 out of {umuti_set.qte_entrant_big}")
                else:
                    print(f"The Existing UmutiSet :\
 {umutie.quantite_initial}  \
isn't bigger than {umuti_set.qte_entrant_big}.")
                umuti_set.save()

        return JsonResponse({"Things ":"well"})
    
    def _umutiMushasha(self, umuti):
        umuti_new = ImitiSet.objects.create()
        umuti_new.code_umuti = str(umuti.code_umuti)
        umuti_new.name_umuti = str(umuti.name_umuti)
        umuti_new.description_umuti = str(umuti.description_umuti)
        umuti_new.type_umuti = str(umuti.type_umuti)
        umuti_new.type_in = str(umuti.type_in)
        umuti_new.ratio_type = str(umuti.ratio_type)
        umuti_new.type_out = str(umuti.type_out)
        last_umuti = UmutiEntree.objects.filter(code_umuti=umuti_new.code_umuti).last()
        umuti_new.price_in = int(last_umuti.price_in)
        umuti_new.price_out = int(last_umuti.price_out)
        umuti_new.quantite_restant = int(umuti.quantite_restant)
        umuti_new.location = str(umuti.location)
        umuti_new.lot = str('')
        umuti_new.date_last_vente = umuti.date_winjiriyeko
        umuti_new.qte_entrant_big = int(umuti.quantite_initial)

        umuti_new.save()

        return umuti_new
    
    def _findLastDate(self, code_umuti:str):
        sell_done = UmutiSold.objects.filter(code_umuti=code_umuti).last()
        if sell_done:
            date = sell_done
            # print(f"The umuti SOLD is: {date} with date {date.date_operation}")
            return date.date_operation
        else:
            # print(f"THe umuti SOLD is not found")
            return None



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
        bundle = []
        bundle.append(dict(data_query))
        for actual in bundle:
            print(f"actual: {actual}")
            code_umuti = actual.get('code_umuti')[0]
            code_operation = actual.get('code_operation')[0]
            qte = actual.get('qte')[0]
            try:
                umuti = UmutiEntree.objects.\
                    filter(code_umuti=code_umuti).\
                    filter(code_operation=code_operation)
            except UmutiEntree.DoesNotExist:
                pass
            else:
                #can now perfom the Vente operation
                print(f"The Umuti found : {umuti}")
                if not umuti:
                    return JsonResponse({"Umuti":"does not exist"})
                sold = self._imitiSell(umuti=umuti[0], qte=qte, operator=request.user)
                if sold == 200:
                    print(f"Umuti with code '{umuti[0].code_umuti}' is sold")

        #  after sell then call compile
        imiti = EntrantImiti()
        jove = imiti.compileImitiSet()
        print(f"La reponse de vente est: {jove}")

        return JsonResponse({"It is":"Okay"})
    
    def _imitiSell(self, umuti:UmutiEntree, qte:int, operator:str):
        """Will substract the quantite_restante in UmutiEntree and
        write a new instance of UmutiSell"""

        reference_umuti = ImitiSet.objects.get(code_umuti='AMT23')
        new_vente = UmutiSold.objects.create()
        new_vente.code_umuti = umuti.code_umuti
        new_vente.name_umuti = umuti.name_umuti
        new_vente.quantity = qte
        new_vente.price_out = reference_umuti.price_out
        new_vente.code_operation_entrant = umuti.code_operation
        code = GenerateCode(12)
        new_vente.code_operation = code.giveCode()
        new_vente.operator = str(operator.username)
        new_vente.date_operation = timezone.now()
        umuti.quantite_restant -= int(qte)

        umuti.save()
        new_vente.save()
        
        return 200
    
    def _getLess35(self):
        imiti = ImitiSet.objects.all()
        less_35 = []
        for umuti in imiti:
            if (umuti.qte_entrant_big / umuti.quantite_restant) < 3.5:
                obj = {
                    'code_umuti': umuti.code_umuti,
                    'name_umuti' : umuti.name_umuti,
                    'quantite_restant' : umuti.quantite_restant
                }
                less_35.append(obj)
        
        if less_35:
            return less_35
        else:
            return None
    
    def workOn35(self, request):
        """THis one works on imitiSet with  less than 35% of
          remaining quantity and return among them the sold
            within past 15days"""
        imiti = self._getLess35()
        days_15 = timezone.now().date() - timedelta(days=15)
        ventes_15 = UmutiSold.objects.filter(date_operation__gte=days_15)
        final_imiti = []
        if imiti:
            i = 0
            for umuti in imiti:
                umuti_exist_15 = ventes_15.filter(code_umuti=umuti.code_umuti)
                if umuti_exist_15:
                    final_imiti.append(imiti[i])
        
        if final_imiti:
            print(f"The final recommandation: {final_imiti}")
        else:
            print(f"There are no recommandations")
        return JsonResponse({"Things are ":"well"})
    
    def rapportVente(self, request):

