# from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

import json
from django.utils import timezone
from datetime import timedelta, datetime

#importing my models from Pharma
from pharma.models import UmutiEntree, ImitiSet, UmutiSold, \
    umutiReportSell

#importing the serializers
from .serializers import ImitiSetSeriazer, umutiReportSellSeriazer,\
        UmutiSoldSeriazer, UmutiEntreeSeriazer

#importing my additional code
from .code_generator import GenerateCode
from .shared.stringToList import StringToList
from .shared.listStrToList import listStrToList, listIntToList,\
      listDictIntSomme

# Create your views here.

class EntrantImiti(viewsets.ViewSet):
    """Manages all the Entrant Operations"""

    
    @action(methods=['post'], detail=False)
    # @action(methods=['get'], detail=False,\
    #          permission_classes= [IsAuthenticated])
    def kurangura(self, request):
        """Kwinjiza umuti nkukwo uwuranguye"""
        dataReceived = request.data
        print(f"The data Received: {dataReceived}")

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
            except ImitiSet.DoesNotExist:
                #when the code is new in the ImitiSet
                #we create that entry in the ImitiSet
                umuti_new = self._umutiMushasha(umutie)
                if str(type(umuti_new)) == "<class 'pharma.models.ImitiSet'>":
                    obj = {
                        'date': (str(umutie.date_uzohererako))[:7],
                        'qte': int(umutie.quantite_restant),
                        'code_operation': str(umutie.code_operation),
                        'to_panier': 0
                    }
                    arr = []
                    arr.append(obj)
                    jove = json.dumps(obj=arr)
                    umuti_new.lot = jove
                    umuti_new.save()
            else:
                qte_saved =  StringToList(umuti_set.checked_qte)
                qte_tracked = qte_saved.toList()
                print(f"The converted qte: {qte_tracked} out of {umuti_set.checked_qte}")
                converted_list = listStrToList(umuti_set.checked_imiti)
                if umutie.code_operation in converted_list:
                    synced = self._check_qte(umutie.code_operation, \
                                        umutie.quantite_restant, \
                                        qte_tracked )
                    print(f"already tracked into : {synced}")
                    continue  # skip to treat is as new
                    # sync quantite_restant according to umutie
                else:
                    print(f"{converted_list} : {umutie.code_operation}")
                    converted_list.append(umutie.code_operation)
                    qte_tracked.append(
                        {'code_operation':umutie.code_operation, 
                         'qte_restant': umutie.quantite_restant})
                    umuti_set.checked_imiti = converted_list
                    umuti_set.checked_qte = qte_tracked
                # print(f"the actual_qte_tracked is {umuti_set.checked_qte}")
                # check that the actual code_operation has passed,
                # i should add those code_operation in a fields in umutiSet
                # divided by a comma.

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
                        'code_operation': str(umutie.code_operation),
                        'to_panier': 0
                    }
                    i += 1
                    lot_list.append(obj)
                umuti_set.price_out = umutie.price_out # setting price_out to the last entrie
                # umuti_set.quantite_restant += umutie.quantite_restant
                umuti_set.quantite_restant = listDictIntSomme(umuti_set.checked_qte)
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
    
    def _check_qte(self, code_operation:str, quantite_restant:int,\
                    qte_tracked:list)-> list:
        # checked_qte = listStrToList(umutiset_new.checked_qte)
        cloned_qte = qte_tracked
        i = 0
        for obj in qte_tracked:
            if obj.get('code_operation') == code_operation:
                if obj['qte_restant'] != quantite_restant:
                    obj['qte_restant'] = quantite_restant
                else:
                    print(f"\n{obj['qte_restant']} === {quantite_restant}\n\n\n")

        return qte_tracked
    
    def _umutiMushasha(self, umuti):
        """Creates an instance of ImitiSet, it's input is 
        an instance of UmutiEntree"""
        umuti_new = ImitiSet.objects.create()
        umuti_new.code_umuti = str(umuti.code_umuti)
        umuti_new.name_umuti = str(umuti.name_umuti)
        umuti_new.description_umuti = str(umuti.description_umuti)
        umuti_new.type_umuti = str(umuti.type_umuti)
        umuti_new.type_in = str(umuti.type_in)
        umuti_new.ratio_type = str(umuti.ratio_type)
        umuti_new.type_out = str(umuti.type_out)
        try:
            last_umuti = UmutiEntree.objects.filter(code_umuti=umuti_new.code_umuti).last()
            umuti_new.price_in = int(last_umuti.price_in)
            umuti_new.price_out = int(last_umuti.price_out)
        except AttributeError:
            umuti_new.price_in = int(umuti.price_in)
            umuti_new.price_out = int(umuti.price_out)
            pass
        umuti_new.quantite_restant = int(umuti.quantite_restant)
        umuti_new.location = str(umuti.location)
        umuti_new.lot = str('')
        umuti_new.date_last_vente = umuti.date_winjiriyeko
        umuti_new.qte_entrant_big = int(umuti.quantite_initial)
        checked = []
        qte_obj= {
            'code_operation': umuti.code_operation,
            'qte_restant': umuti_new.quantite_restant
        }
        checked_qte = []
        checked_qte.append(qte_obj)
        checked.append(umuti.code_operation)
        umuti_new.checked_imiti = checked
        umuti_new.checked_qte = checked_qte

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
             permission_classes= [AllowAny])
    def dispo(self, request):
        # return JsonResponse({"THings are":"okay"})
        imiti = ImitiSet.objects.all().order_by('-date_last_vente')
        imitiSerialized = ImitiSetSeriazer(imiti, many=True)

        if imitiSerialized.is_valid:
            return Response(imitiSerialized.data)

        return JsonResponse({"THings are":"okay"})
    

    # @action(methods=['post'], detail=False,\
    #          permission_classes= [IsAuthenticated])
    @action(methods=['post'], detail=False)
    def sell(self, request):
        data_query = request.data
        print(f"The data sent is: {data_query}")
        bundle = data_query.get('imiti')
        # bundle.append(dict(data_query))
        for actual in bundle:
            print(f"actual: {actual}")
            code_umuti = actual.get('code_umuti')
            # code_operation = actual.get('code_operation')[0]
            # qte = actual.get('qte')[0]
            lot = actual.get('lot')
            for lote in lot:
                code_operation = lote.get('code_operation')
                qte = lote.get('qte')

            # code_operation = actual.get('lot')[0].get('code_operation')
            # qte = actual.get('lot')[0].get('qte')
            # print(f"The code gotten are: {code_umuti} and {code_operation} and {qte}")
            # return JsonResponse({"done":"okay"})
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
                        print(f"The rest qte is {umuti[0].quantite_restant}")

        #  after sell then call compile
        imiti = EntrantImiti()
        jove = imiti.compileImitiSet()
        print(f"La reponse de vente est: {jove}")

        return JsonResponse({"It is":"Okay"})
    
    def _imitiSell(self, umuti:UmutiEntree, qte:int, operator:str):
        """Will substract the quantite_restante in UmutiEntree and
        write a new instance of UmutiSell"""

        print(f"The umuti to work on is : {umuti} with qte: {qte} found with {umuti.quantite_restant}")
        reference_umuti = ImitiSet.objects.get(code_umuti=umuti.code_umuti)
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
        """THis one returns a list of objects from imitiSet with less than
          35% of the remaining quantity"""
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
    


class Rapport(viewsets.ViewSet):
    """This class is meant to be of generating reports"""

    @action(methods=['get'], detail=False)
    def reportEntree(self, request):
        """making an endpoint that will return all the UmutiEntree entries"""
        imiti = UmutiEntree.objects.all().order_by('-date_winjiriyeko')
        imitiSerialized = UmutiEntreeSeriazer(imiti, many=True)

        if imitiSerialized.is_valid:
            return Response(imitiSerialized.data)

        return JsonResponse({"THings are":"okay"})

    @action(methods=['get'], detail=False)
    def reportSold(self, request):
        """making an endpoint that will return all the umutisold entries"""
        imiti = UmutiSold.objects.all().order_by('-date_operation')
        imitiSerialized = UmutiSoldSeriazer(imiti, many=True)

        if imitiSerialized.is_valid:
            return Response(imitiSerialized.data)

        return JsonResponse({"THings are":"okay"})

    @action(methods=['post'], detail=False)
    def reportSell(self, request):
        """Will receive criteria from the form passed via request.
        Accepted criteria: today(default), date1, date2
        """
        criteria = request.data
        today = datetime.today()
        if criteria.get('date1'):
            date1 = criteria.get('date1')
        else:
            date1 = today
        if criteria.get('date2'):
            date2 = criteria.get('date2')
        else:
            date2 = today
        
        report = []
        # sold = UmutiSold.objects.filter(date_operation__gte=date1).\
        #     filter(date_operation__gte=date2)
        
        # report = self._makeReport(sold)
        # if report == 200:
        #     done_report = umutiReportSell.objects.all()
        #     if done_report:
        #         done_report_serializer = umutiReportSellSeriazer(\
        #             done_report, many=True)
        #         if done_report_serializer.is_valid:
        #             return Response(done_report_serializer.data)
        
        return JsonResponse({"Things are":"Quite well"})
            
    
    def _makeReport(self, data:UmutiSold):
        """will get a queryset an make a syntesis of the following form:
        umuti_code, umuti_name, nb_vente, px_T, benefice, nb_rest, px_T_rest
        """
        
        # if exist, clean all the report existing
        old_report = umutiReportSell.objects.all()
        if old_report:
            for element in old_report:
                element.delete()
            old_report.save()
        else:
            # print(f"No record in Report sell, use:")
            pass
        
        #stating a new report
        for element in data:
            try:
                umuti_set = umutiReportSell.objects.get\
                    (code_umuti=element.code_umuti)
                # print(f"Serching for : {element.code_umuti}")
            except umutiReportSell.DoesNotExist:
                umuti_record = self._recordNew(umuti=element)
                if not umuti_record:
                    pass
                    # print(f"a new record is not created")
                else:
                    pass
                    # print("The new record is created")
            else:
                update_record = self._updateRecord(umuti_set=umuti_set,\
                                                    umuti=element)
                if update_record:
                    print(f"The report is well done")
                else:
                    print(f"The report is not well done")
        
        return 200
    
    def _updateRecord(self,umuti_set:umutiReportSell, umuti:UmutiSold):
        """We update only:  nb_vente, px_T_vente, benefice, nb_rest,
          px_T_rest"""
        umuti_set.nb_rest -= umuti.quantity
        umuti_set.nb_vente += umuti.quantity
        umuti_set.px_T_vente += int(umuti.quantity * umuti.price_out)
        umuti_set.benefice += int(umuti.quantity) * \
            int(umuti.price_out - umuti.price_in)
        umuti_set.px_T_rest -= umuti_set.px_T_vente

        umuti_set.save()

        return umuti_set

    def _recordNew(self, umuti:UmutiSold):
        """Here we record new umuti report"""
        record_new = umutiReportSell.objects.create()
        record_new.code_umuti = umuti.code_umuti
        record_new.name_umuti = umuti.name_umuti
        record_new.nb_vente = umuti.quantity
        record_new.px_T_vente = int(umuti.price_out) * \
            int(umuti.quantity)
        # record_new.benefice = int(umuti.price_out * umuti.quantity) - \
        #                         int(umuti.price_in * umuti.quantity)
        record_new.benefice = int(umuti.price_out - umuti.price_in) * \
                                int (umuti.quantity)
        try:
            current = ImitiSet.objects.get(code_umuti=umuti.code_umuti)
            record_new.nb_rest = int(current.quantite_restant)
            record_new.px_T_rest = int(current.quantite_restant * \
                                    current.price_out)
        except ImitiSet.DoesNotExist:
            pass
        
        record_new.save()

        return record_new
    
    