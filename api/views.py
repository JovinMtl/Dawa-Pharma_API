# from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny,\
    IsAdminUser

import json
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from datetime import timedelta, datetime
import os

#importing my models from Pharma
from pharma.models import UmutiEntree, ImitiSet, UmutiSold, \
    umutiReportSell, imitiSuggest, UmutiEntreeBackup, UsdToBif,\
    BonDeCommande, Assurance

#importing the serializers
from .serializers import ImitiSetSeriazer, UmutiSoldSeriazer,\
      UmutiEntreeSeriazer, ImitiSuggestSeria, imitiSuggestSeria, \
      LastIndexSeria, SyntesiSeria, AssuranceSeria,\
      BonCommaSeria, SoldAsBonSeria

#importing my additional code
from .code_generator import GenerateCode
from .shared.stringToList import StringToList
from .shared.listStrToList import listStrToList, listIntToList,\
      listDictIntSomme, listDictIntSomme2, listDictIntSomme3
from .shared.stringToDate import stringToDate, shortStr2Date


# Making a weekday dict that will be used
week_days = {
    1: 'Lun',
    2: 'Mar',
    3: 'Mer',
    4: 'Jeu',
    5: 'Ven',
    6: 'Sam',
    7: 'Dim'
}

# Create your views here.

class GeneralOps(viewsets.ViewSet):
    """
    Designed to do general operations like setup
    """

    @action(methods=['get'], detail=False,\
             permission_classes= [IsAdminUser])
    def setup(self, request):
        """
        checks and creates required instances.
        """
        created = []
        try:
            assu_sans = Assurance.objects.get(name="Sans")
        except Assurance.DoesNotExist:
            assu_sans = Assurance.objects.create(name="Sans", rate_assure=0)
            assu_sans.save()
            created.append(assu_sans.name)
        try:
            assu_ph = Assurance.objects.get\
                (name="Pharmacie Ubuzima")
        except Assurance.DoesNotExist:
            assu_ph = Assurance.objects.create()
            assu_ph.name = "Pharmacie Ubuzima"
            assu_ph.rate_assure = 10
            assu_ph.save()
            created.append(assu_sans.name)
        try:
            bon_default = BonDeCommande.objects.get\
                (organization__name='Sans')
        except BonDeCommande.DoesNotExist:
            assu_sans = Assurance.objects.get(name="Sans")
            bon_default = BonDeCommande.objects\
                .create(organization=assu_sans)
            bon_default.num_du_bon = '0001'
            bon_default.is_paid = True
            bon_default.save()
            created.append("Default BdC")
        
        taux_usd = UsdToBif.objects.first()
        if not taux_usd:
            new_taux = UsdToBif.objects.create()
            new_taux.actualExchangeRate = 6200
            new_taux.save()

        return JsonResponse({"Setup done" : created})
    
    @action(methods=['post', 'get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def addAssu(self, request):
        """
        This endpoint will check and create a new
        assurance
        """
        data_sent = request.data
        status = False
        assu_name = 'Sans'
        assu_rate = 0
        if data_sent:
            data_sent = data_sent.get('imiti')
            print("Have received assuData: ", data_sent.get('assu'))
            assu_name = data_sent.get('assu')[0]
            assu_rate = data_sent.get('assu')[1]
            if assu_rate > 100 or assu_rate < 0:
                return JsonResponse({"status": 0,\
                                'reason':'assu_rate invalid'},\
                                status=406)
        else:
            print("Did not receive assuData, but ", data_sent)
        try:
            assu = Assurance.objects.get(name=assu_name)
        except Assurance.DoesNotExist:
            new_assu = Assurance.objects.create()
            new_assu.name = assu_name
            new_assu.rate_assure = assu_rate
            new_assu.save()
            status = True
        else:
            return JsonResponse({"status": 0,\
                                'reason':"Cette assurance existe"},\
                                status=400)
        # assu_name = data_sent.get('name')
        return JsonResponse({"status": 1,\
                                'reason':"Assurance ajoutee"},\
                                status=200)
    
    @action(methods=['get'], detail=False,\
             permission_classes= [AllowAny])
    def isSetUp(self, request):
        """
        Checks if all requirements handled by setup 
        that are all set.
        """
        isReady = True
        missing = []
        try:
            assu_sans = Assurance.objects.get(name="Sans")
        except Assurance.DoesNotExist:
            missing.append('Sans')
            isReady = False
        try:
            assu_ph = Assurance.objects.get\
                (name="Pharmacie Ubuzima")
        except Assurance.DoesNotExist:
            isReady = False
            missing.append("Pharmacie Ubuzima")
        try:
            bon_default = BonDeCommande.objects.get\
                (organization__name='Sans')
        except BonDeCommande.DoesNotExist:
            isReady = False
            missing.append("Default Bon de Commande")
        taux_usd = UsdToBif.objects.first()
        if not taux_usd:
            isReady = False
            missing.append("Taux de change")

        return JsonResponse({"Setup" : isReady,\
                             "Missing": missing})

    @action(methods=['get'], detail=False,\
             permission_classes= [AllowAny])
    def getAssu(self, request):
        """
        Returns all instances of Assurances
        """
        assu = Assurance.objects.all()
        assu_seria = AssuranceSeria(assu, many=True)
        if assu_seria.is_valid:
            return Response(assu_seria.data)
        return JsonResponse({"status": 0,\
                            'reason':'server failed'},\
                            status=406)
    
    @action(methods=['post'], detail=False,\
             permission_classes= [AllowAny])
    def setBons(self, request):
        """
        Sets to true the given instances of BonDeCommande
        """ 
        bon_ids = request.data.get('imiti')
        print("THe requested data Set:", bon_ids)

        for id in bon_ids:
            try:
                bon = BonDeCommande.objects.get(num_du_bon=id)
            except BonDeCommande.DoesNotExist:
                return JsonResponse({"status": 0,\
                            'reason':'Bon invalide'},\
                            status=406)
            else:
                bon.is_paid = True
                bon.save()
        
        return JsonResponse({"status": 1,\
                            'reason':'request completed'},\
                            status=200)

    @action(methods=['post'], detail=False,\
             permission_classes= [AllowAny])
    def getBons(self, request):
        """
        Returns all instances of BonDeCommande
        """
        requested_data = request.data.get('imiti')
        print("THe requested data:", requested_data)
        request_bons = []
        for bon in requested_data:
            try:
                query = BonDeCommande.objects.get(id=bon)
            except BonDeCommande.DoesNotExist:
                return JsonResponse({"status": 0,\
                            'reason':'Bon invalide'},\
                            status=406)
            else:
                request_bons.append(query)
        bons_seria = BonCommaSeria(request_bons, many=True)
        if bons_seria.is_valid:
            return Response(bons_seria.data)
        
        return JsonResponse({"status": 0,\
                            'reason':'erreur du serveur'},\
                            status=406)
    


class EntrantImiti(viewsets.ViewSet):
    """Manages all the Entrant Operations"""

    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def kurangura(self, request):
        """Kwinjiza umuti nkukwo uwuranguye"""
        dataReceived = request.data
        data = dataReceived.get('jov')
        print(f"The data Received: {data}")
        # first of all, generate the codes
        code_12 = GenerateCode()
        code_operation = code_12.giveCode()
        error_list = []
        i = 0
        single = False
        for obj in data:
            if (len(data) > 2) and (i == 0):
                i += 1 #to skip the title string
                continue
            elif (len(data) == 1):
                single = True
            
            code_6 = GenerateCode(6)
            code_med = code_6.giveCode()
            print(f"using code: {code_med}")
            # We should check the existence of umuti with that code or nom_med
            check_exist = self._doesExist(obj=obj)
            if check_exist:
                code_med = check_exist # in case there is a match.
            reponse = self._addUmuti(obj=obj,code_med=code_med,\
                                      code_operation=code_operation, \
                                        single=single, operator=request.user.username) # 200 if ok
            if reponse != 200:
                error_list.append(i)
        
        if len(error_list):
            return JsonResponse({"Finished with errors ": error_list})

        return JsonResponse({"Things ":"well"})
    
    def _doesExist(self, obj:dict):
        """This method checks if the umuti already exist with the same
        nom_med in order to share the code_med.
        In case there is a match of nom_med or obj.code_med,
        then return that code_med."""
        nom_med = obj.get('nom_med')
        code_med = obj.get('code_med')
        if len(code_med) == 6:
            return code_med
        try:
            umuti_exist = UmutiEntree.objects.get(nom_med=nom_med)
        except UmutiEntree.DoesNotExist:
            return None
        else:
            return umuti_exist.code_med
    
    def _addUmuti(self, obj:dict, code_med:str, code_operation:str,\
                   single:bool, operator:str):
        """THis method is in charge of creating and filling a new instance
        of UmutiEntree, of this type: 

        obj = {'code_med': '', 'date_entrant': '2024-06-08T09:01:18.785Z', 
               'date_peremption': '12:00:00 AM', 'nom_med': 'AMINOPHYLLINE', 
               'description_med': 'Uvura uburuhe', 'famille_med': 'Ovule', 
               'type_achat': 'Carton', 'ratio': '10', 'type_vente': 'Piece', 
               'prix_vente': '1500', 'prix_vente': '1800', 
               'quantite_initial': '15', 'location': ''}
        """
        print(f"THe operator is : {operator}")
        umuti_new = UmutiEntree.objects.create()
        umuti_new.nom_med = obj.get('nom_med')
        umuti_new.code_med = code_med
        umuti_new.code_operation = code_operation
        umuti_new.quantite_initial = obj.get('quantite_initial')
        umuti_new.quantite_restant = umuti_new.quantite_initial
        usd_to_bif = UsdToBif.objects.first()
        umuti_new.prix_achat = obj.get('prix_achat')
        umuti_new.prix_vente = obj.get('prix_vente')
        umuti_new.prix_achat_usd = obj.get('prix_achat') / usd_to_bif.actualExchangeRate
        umuti_new.prix_vente_usd = obj.get('prix_vente') / usd_to_bif.actualExchangeRate
        if not single:
            umuti_new.date_peremption = self._giveDate_exp(obj.get('date_peremption'))
            umuti_new.date_entrant = self._giveDate_entree(obj.get('date_entrant'))
        else:
            umuti_new.date_peremption = obj.get('date_peremption')
            umuti_new.date_entrant = obj.get('date_entrant')
        # umuti_new.description_umuti = (obj.get('description_med'))
        umuti_new.type_med = obj.get('famille_med') 
        umuti_new.type_achat = obj.get('type_achat') 
        if obj.get('ratio'):
            umuti_new.ratio = obj.get('ratio')
        umuti_new.type_vente = obj.get('type_vente')
        umuti_new.location = obj.get('location')
        umuti_new.operator = operator

        umuti_new.save()

        print("THe new saved Med: ", umuti_new.nom_med)

        # Creating a backup of UmutiEntree which will keep unchanged initial state.
        # This is to copy each new instance of UmutiEntree into backup.
        reponse = self._duplicateUmutiEntree(instance=umuti_new)
        
        return 200
    
    def _duplicateUmutiEntree(self, instance):
        """This method duplicated UmutiEntree instance into 
        UmutiEntreeBackup."""
        umuti_backup = UmutiEntreeBackup.objects.create()
        umuti_backup.nom_med = instance.nom_med
        umuti_backup.code_med = instance.code_med
        umuti_backup.code_operation = instance.code_operation
        umuti_backup.quantite_initial = instance.quantite_initial
        umuti_backup.quantite_restant = instance.quantite_initial
        umuti_backup.prix_achat = instance.prix_achat
        umuti_backup.prix_vente = instance.prix_vente
        umuti_backup.date_peremption = instance.date_peremption
        umuti_backup.date_entrant = instance.date_entrant
        # umuti_backup.description_umuti = instance.date_entrant
        umuti_backup.type_med = instance.type_med
        umuti_backup.type_achat = instance.type_achat
        umuti_backup.ratio = instance.ratio
        umuti_backup.type_vente = instance.type_vente
        umuti_backup.location = instance.location
        umuti_backup.operator = instance.operator
        umuti_backup.save()

        return 200
    
    def _giveDate_exp(self, date_peremption:str)->str:
        """ This function checks the expiring date sent in the format:
            "04/01/27" and return datetime.datetime(2027, 4, 1, 0, 0)
        """
        if date_peremption:
            return datetime.strptime(date_peremption, "%m/%d/%y")
        else:
            return timezone.now()

    def _giveDate_entree(self, date_entrant:str)-> str:
        """THis function checks that an date isoString is given 
        from Javascript and then converts it to real python date object."""
        if date_entrant:
            return datetime(date_entrant)
        else:
            today = datetime.now()
            return today


    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def compileImitiSet(self, request=None):
        """Compile all the list of the Medicament procured, according
        the code_med and date_echeance"""
        procured = UmutiEntree.objects.all()
        i = 1
        j = 1
        lot = []
        for umutie in procured:
            code = umutie.code_med
            try:
                umuti_set = ImitiSet.objects.get(code_med=code)
            except ImitiSet.DoesNotExist:
                #when the code is new in the ImitiSet
                #we create that entry in the ImitiSet
                umuti_new = self._umutiMushasha(umutie)
            else:
                qte_saved =  StringToList(umuti_set.checked_qte)
                qte_tracked = qte_saved.toList()
                # print(f"The converted qte: {qte_tracked} out of {umuti_set.checked_qte}")
                converted_list = listStrToList(umuti_set.checked_imiti)
                if umutie.code_operation in converted_list:
                    # sync quantite_restant according to umutie
                    synced = self._check_qte(umutie.code_operation, \
                                        umutie.quantite_restant, \
                                        qte_tracked )
                    synced_lot = self._sync_lot(umuti_set.lot, umutie)
                    somme_lot = listDictIntSomme3(synced_lot)
                    usd_to_bif = UsdToBif.objects.get(id=1)
                    usd_to_bif = UsdToBif.objects.last()
                    # print(f"The new prix_vente : {umutie.prix_vente_usd} times {usd_to_bif.actualExchangeRate} of {umutie.code_med}")
                    umuti_set.prix_vente = float(umutie.prix_vente_usd) * \
                                        usd_to_bif.actualExchangeRate
                    umuti_set.quantite_restant = somme_lot
                    umuti_set.lot = synced_lot
                    umuti_set.checked_qte = synced
                    umuti_set.save()
                    continue  # skip to treat is as new
                else:
                    converted_list.append(umutie.code_operation)
                    qte_tracked.append(
                        {'code_operation':umutie.code_operation, 
                         'qte_restant': umutie.quantite_restant})
                    umuti_set.checked_imiti = converted_list
                    umuti_set.checked_qte = qte_tracked
                # check that the actual code_operation has passed,
                # i should add those code_operation in a fields in umutiSet
                # divided by a comma.

                #mugihe iyo code ihari muri Set
                lot_list = self._check_lot(umuti_set.lot, umutie)
                # umuti_set.prix_vente = umutie.prix_vente # setting prix_vente to the last entrie
                usd_to_bif = UsdToBif.objects.get(id=1)
                umuti_set.prix_vente = float(umutie.prix_vente_usd) * \
                        usd_to_bif.actualExchangeRate
                umuti_set.prix_vente_usd = float(umutie.prix_vente_usd)
                # 
                # umuti_set.quantite_restant += umutie.quantite_restant
                umuti_set.quantite_restant = listDictIntSomme(umuti_set.checked_qte)
                umuti_set.lot = lot_list
                last_date = self._findLastDate(code_med=umuti_set.code_med)
                if last_date:
                    umuti_set.date_last_vente = last_date
                #checking if there is qte_entrant bigger than before
                if (int(umuti_set.qte_entrant_big)) < (int(umutie.quantite_initial)):
                    umuti_set.qte_entrant_big = int(umutie.quantite_initial)
#                     print(f"The Umutie is bigger {umutie.quantite_initial}\
#  out of {umuti_set.qte_entrant_big}")
                # else:
#                     print(f"The Existing UmutiSet :\
#  {umutie.quantite_initial}  \
# isn't bigger than {umuti_set.qte_entrant_big}.")
                umuti_set.save()

        print("compileImitiSet: SYNC done.")
        return JsonResponse({"Things went":"well 2"})
    

    def _sync_lot(self, lot:str, umutie):
        lot_string = StringToList(lot)
        #the string of list must be made into json
        lot_list = lot_string.toList()
        i = 0

        for lote in lot_list:
            if lote.get('date') == (str(umutie.date_peremption))[:7]:
                # print(f"Found: {lote.get('date')}  and {(str(umutie.date_peremption))[:7]}")
                operation = lote.get('code_operation')
                for lot in operation:
                    # print(f"exe: {lot}")
                    i += 1
                    try:
                        print(f"exo: {lot[umutie.code_operation]} to {umutie.quantite_restant}",  file=open(os.devnull, 'w'))
                    except KeyError:
                        pass
                    else:
                        lot[umutie.code_operation] = umutie.quantite_restant
                somme_operation = listDictIntSomme2(lote['code_operation'])
                # print(f"La somme est : {somme_operation}")
                lote['qte'] = somme_operation
            # else:s equal: {lote.get('date')} and {(str(umutie.date_peremption))[:7]}")

        return lot_list

    
    def _check_lot(self, lot:str, umutie:UmutiEntree):
        lot_string = StringToList(lot)
        #the string of list must be made into json
        lot_list = lot_string.toList()
        i = 0
        j = 0
        for lote in lot_list:
            if lote.get('date') == (str(umutie.date_peremption))[:7]:
                obj = { 
                            str(umutie.code_operation) : int(umutie.quantite_restant)
                        }
                lote['code_operation'].append(obj)
                lote['qte'] = int(listDictIntSomme2(lote['code_operation']))
                j += 1
            
        if not j:
            obj = {
                'date': (str(umutie.date_peremption))[:7],
                'qte': int(umutie.quantite_restant),
                'code_operation': [
                        { 
                            str(umutie.code_operation) : int(umutie.quantite_restant)
                        }
                    ],
                'to_panier': 0
            }
            i += 1
            lot_list.append(obj)

        return lot_list
    

    def _check_qte(self, code_operation:str, quantite_restant:int,\
                    qte_tracked:list)-> list:
        # checked_qte = listStrToList(umutiset_new.checked_qte)
        cloned_qte = qte_tracked
        i = 0
        for obj in qte_tracked:
            if obj.get('code_operation') == code_operation:
                if obj['qte_restant'] != quantite_restant:
                    obj['qte_restant'] = quantite_restant
                # else:
                #     print(f"\n{obj['qte_restant']} === {quantite_restant}\n\n\n")

        return qte_tracked
    
    def _umutiMushasha(self, umuti:UmutiEntree):
        """Creates an instance of ImitiSet, it's input is 
        an instance of UmutiEntree"""
        umuti_new = ImitiSet.objects.create()
        umuti_new.code_med = str(umuti.code_med)
        umuti_new.nom_med = str(umuti.nom_med)
        umuti_new.classe_med = (str(umuti.classe_med))[:29]
        umuti_new.sous_classe_med = \
            (str(umuti.sous_classe_med))[:29]
        umuti_new.type_med = str(umuti.type_med)
        umuti_new.type_achat = str(umuti.type_achat)
        umuti_new.ratio = str(umuti.ratio)
        umuti_new.type_vente = str(umuti.type_vente)
        usd_to_bif = UsdToBif.objects.get(id=1)
        try:
            last_umuti = UmutiEntree.objects.filter(code_med=umuti_new.code_med).last()
            umuti_new.prix_achat = int(last_umuti.prix_achat)
            # umuti_new.prix_vente = int(last_umuti.prix_vente)
            umuti_new.prix_vente = int(last_umuti.prix_vente_usd) * \
                usd_to_bif.actualExchangeRate
        except AttributeError:
            umuti_new.prix_achat = int(umuti.prix_achat)
            # umuti_new.prix_vente = int(umuti.prix_vente)
            umuti_new.prix_vente = int(last_umuti.prix_vente_usd) * \
                usd_to_bif.actualExchangeRate
            pass
        
        umuti_new.quantite_restant = int(umuti.quantite_restant)
        umuti_new.location = str(umuti.location)
        umuti_new.lot = str('')
        umuti_new.date_last_vente = umuti.date_entrant
        umuti_new.qte_entrant_big = int(umuti.quantite_initial)

        obj = {
            'date': (str(umuti.date_peremption))[:7],
            'qte': int(umuti.quantite_restant),
            'code_operation': [
                        { 
                            str(umuti.code_operation) : int(umuti.quantite_restant)
                        }
                    ],
            'to_panier': 0
        }
        lot = []
        lot.append(obj)

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
        umuti_new.lot = lot

        umuti_new.save()

        return umuti_new
    
    def _findLastDate(self, code_med:str):
        sell_done = UmutiSold.objects.filter(code_med=code_med).last()
        if sell_done:
            date = sell_done
            # print(f"The umuti SOLD is: {date} with date {date.date_operation}")
            return date.date_operation
        else:
            # print(f"THe umuti SOLD is not found")
            return None


class Assurances(viewsets.ModelViewSet):
    """THis primary deals with assurances."""
    queryset = Assurance.objects.all()
    serializer_class = AssuranceSeria
    permission_classes = [IsAuthenticated]


class ImitiOut(viewsets.ViewSet):
    """THis will give informations about the Imiti in the Store 
    or etagere"""

    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def dispo(self, request):
        get_data = request.query_params
        page = 0
        if get_data:
            # print(f"Your queryParams: {get_data}")
            page = int(get_data.get('page'))
        else:
            # print(f"No param")
            pass
        imiti = ImitiSet.objects.all().order_by('-date_last_vente')
        # numbering total/syntesis
        syntesis = self.__make_syntesis(imiti=imiti)
        syntesis['page_number'] = page
        syntesis_serialized = SyntesiSeria(syntesis)
        if page > 0:
            paginated = Paginator(imiti, 15)
            imiti = paginated.get_page(int(page))

        imitiSerialized = ImitiSetSeriazer(imiti, many=True)

        if imitiSerialized.is_valid and syntesis_serialized.is_valid:
            return JsonResponse({
                'data': imitiSerialized.data,
                'syntesis': syntesis_serialized.data
            })

        return JsonResponse({"THings are":"okay"})
    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def dispo_date(self, request):
        """This endpoint will get range dates and return its disponible."""
        data_sent = request.data
        date1 = data_sent.get(date1)
        date2 = data_sent.get(date2)

        imiti =ImitiSet.objects.filter()

        return JsonResponse({"things are":"ok"})
    
    def __make_syntesis(self, imiti:list)->dict:
        """This method will calculate the sum and benefice."""
        syntesis = {
            'qte':0,
            'pa_t': 0,
            'pv_t': 0,
            'benefice': 0,
        }
        for umuti in imiti:
            syntesis['qte'] += int(umuti.quantite_restant)
            syntesis['pa_t'] += int(umuti.quantite_restant * \
                                umuti.prix_achat)
            syntesis['pv_t'] += int(umuti.quantite_restant * \
                                umuti.prix_vente)
            syntesis['benefice'] += int (umuti.quantite_restant *\
                        (umuti.prix_vente - umuti.prix_achat))
        
        return syntesis
    

    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def sell(self, request):
        data_query = request.data
        print(f"The data sent is: {data_query}")
        bundle = data_query.get('imiti')
        panier = bundle.get('panier')
        client = bundle.get('client')
        # First checking the client dict, in order to access the
        # BonDeCommande objet to assign to UmutiSold
        bon_de_commande = BonDeCommande.objects.first()
        total_facture = 0
        once = 0
        for actual in panier:
            code_med = actual.get('code_med')
            lot = actual.get('lot')
            if not lot:
                continue
            for lote in lot:
                code_operation = lote.get('code_operation')
                qte = lote.get('qte')
                orders = self._assess_order(code_med=code_med,\
                                         code_operation=code_operation,\
                                             qte=qte)
                for order in orders:
                    if order[2] == 0:
                        continue
                    try:
                        umuti = UmutiEntree.objects.\
                            filter(code_med=code_med).\
                            filter(code_operation=order[1])
                    except UmutiEntree.DoesNotExist:
                        pass
                    else:
                        #can now perfom the Vente operation
                        print(f"The Umuti found : {umuti}")
                        if not umuti:
                            return JsonResponse({"Umuti":"does not exist"})
                        be_sold = ImitiSet.objects.get(code_med=umuti[0].code_med)
                        
                        if client and (once==0):
                            # there is client data, and is special
                            # create a new instance of commande
                            bon_de_commande = self._createBon(\
                                client=client, price=be_sold.prix_vente)
                            if bon_de_commande == 403:
                                return JsonResponse({"The Assurance does ":"not exist"})
                        sold = self._imitiSell(umuti=umuti[0], qte=order[2], \
                                    operator=request.user, \
                                        reference_umuti=be_sold,\
                                        bon_de_commande=bon_de_commande)

                        if sold == 200:
                            total_facture += be_sold.prix_vente * order[2]
                once += 1 # create bon_de_commande only once
        # Should now update the reduction in bon_de_commande
        if client:
            bon_de_commande = self._updateReduction(bon_de_commande, total=total_facture)
            print("The client is: ", client)
        #  after sell then call compile
        imiti = EntrantImiti()
        jove = imiti.compileImitiSet()

        # should calculate the number of sold in this year
        elapsed_month = timezone.now().month
        today_number = timezone.now().day
        year_start = timezone.now() - timedelta(\
            days=((30*elapsed_month)+today_number))
        imiti_sold = UmutiSold.objects.filter(\
            date_operation__gte=year_start)

        return JsonResponse({"sold": len(imiti_sold)})
    
    def _updateReduction(self, \
            bon_de_commande:BonDeCommande, \
                total:int=0)->BonDeCommande:
        """Updates the total dettes in as reduction."""
        org = bon_de_commande.organization
        paid = total * (org.rate_assure/100)
        bon_de_commande.montant_dette = total - paid
        bon_de_commande.save()

        return bon_de_commande
    

    def _createBon(self, client, price:int)->int:
        """Will create a new instance of BonDeCommande
        according to client dict.
        """
        new_bon = BonDeCommande.objects.create()
        new_bon.beneficiaire = client.get('nom_client')
        org = client.get('assureur') # use name of organization
        try:
            organization = Assurance.objects.get(name=org)
        except Assurance.DoesNotExist:
            # indicate that assurance does not exist
            return 403
        else:
            org = organization
        new_bon.organization = org
        new_bon.categorie = client.get('categorie')
        new_bon.num_beneficiaire = client.get('numero_carte')
        # Dealing with uniqueness of num_du_bon
        if new_bon.organization.name \
            == "Pharmacie Ubuzima" or \
            new_bon.organization.name == "Sans":
            code_8 = GenerateCode(7)
            code_bon = code_8.giveCode()
            new_bon.num_du_bon = 'P_' + code_bon
        else:
            new_bon.num_du_bon = client.get('numero_bon')
        
        
        new_bon.montant_dette = org.rate_assure * price
        if client.get('date_bon'):
            date_arr = stringToDate(client.get('date_bon'))
            new_bon.date_du_bon = timezone.datetime(\
                date_arr[0], date_arr[1], date_arr[2])
        new_bon.date_served = timezone.now()

        new_bon.save()
        return new_bon
    
    def _assess_order(self, code_med:str, code_operation:list, qte:int) -> list:
        """ THis function will take a list of object of this kind:
    
                    code_operation = [{'xt10': 2}, {'xt11': 5}]
            coupled with :  code_med = 'AL123'
           and return a  list of str and int of this kind:
            [['AL123', 'xt10', 2], ['AL123', 'xt11', 5]]
        """
        data = []
        for obj in code_operation:
            code = (str(obj)).replace('[',"").replace(']','').\
                replace("'",",", -1).split(',')[1]
            qtee = int((str(obj)).replace('[',"").replace(']','').\
                replace("'",",", -1).split(" ")[1].split('}')[0])
            
            data.append([code_med, code, qtee])
        
        orders = self.__place_order(data=data, qte=qte)
        
        return orders
    
    def __place_order(self, data:list, qte:int) -> list:
        """ The function takes a list of order and make a repartition of qte
        based on input data of this type:
            data = [['AL123', 'xt10', 2], ['AL123', 'xt11', 5]]

            with: qte = 1

        and return :  [['AL123', 'xt10', 1], ['AL123', 'xt11', 0]]
        """
        print(f"The qte received: {qte}") 
        reste = 0
        if qte < 1:
            return []
        for dat in data:
            if (qte > dat[2]) and (reste == 0):
                reste = qte - dat[2]
                qte = reste
            elif (qte <= dat[2]) and (reste != -1):
                dat[2] = qte
                reste = -1
                qte = 0
            elif reste == -1:
                dat[2] = 0
            else:
                return ['Empty',]
        
        return data

    
    def _imitiSell(self, umuti:UmutiEntree, \
                   qte:int, operator:str, \
                   reference_umuti:ImitiSet,\
                bon_de_commande:BonDeCommande=None):
        """Will substract the quantite_restante in UmutiEntree and
        write a new instance of UmutiSell"""

        print(f"The umuti to work on is : {umuti} with qte: {qte} found with {umuti.quantite_restant}")
        # reference_umuti = ImitiSet.objects.get(code_med=umuti.code_med)
        new_vente = UmutiSold.objects.create()
        new_vente.code_med = umuti.code_med
        new_vente.nom_med = umuti.nom_med
        new_vente.quantity = qte
        new_vente.prix_achat = reference_umuti.prix_achat
        new_vente.prix_vente = reference_umuti.prix_vente
        new_vente.difference = new_vente.prix_vente - new_vente.prix_achat
        new_vente.code_operation_entrant = umuti.code_operation
        code = GenerateCode(12)
        new_vente.code_operation = code.giveCode()
        new_vente.operator = str(operator.username)
        new_vente.date_operation = timezone.now()
        new_vente.bon_de_commande = bon_de_commande
        umuti.quantite_restant -= int(qte)

        umuti.save()
        new_vente.save()
        
        return 200
    


class Rapport(viewsets.ViewSet):
    """This class is meant to be of generating reports"""

    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def reportEntree(self, request):
        """making an endpoint that will return all the UmutiEntreeBackup instead of
          UmutiEntree entries."""
        imiti = UmutiEntreeBackup.objects.all().order_by('-date_entrant')
        imitiSerialized = UmutiEntreeSeriazer(imiti, many=True)

        if imitiSerialized.is_valid:
            return Response(imitiSerialized.data)

        return JsonResponse({"THings are":"okay"})

    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def reportSold(self, request):
        """making an endpoint that will return all the umutisold entries"""
        imiti = UmutiSold.objects.all().order_by('-date_operation')
        imitiSerialized = UmutiSoldSeriazer(imiti, many=True)

        if imitiSerialized.is_valid:
            return Response(imitiSerialized.data)

        return JsonResponse({"THings are":"okay"})
    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def reportVentes(self, request):
        """making an endpoint that will return all the umutisold entries"""
        begin_date, end_date = self._getDate(request.data)
        # imiti = UmutiSold.objects.all().order_by('-date_operation')
        meds = UmutiSold.objects.filter(date_operation__gte=begin_date)\
            .filter(date_operation__lte=end_date)
        meds_built = self._builtVente(meds)
        print(f"THe things gotten: {meds_built}")
        imitiSerialized = SoldAsBonSeria(data=meds_built, many=True)

        if imitiSerialized.is_valid():
            return Response(imitiSerialized.data)

        return JsonResponse({"response": meds_built})

    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def reportSell(self, request):
        """Will receive criteria from the form passed via request.
        Accepted criteria: today(default), date1, date2
        """
        criteria = request.data
        today = timezone.now()
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
                    (code_med=element.code_med)
                # print(f"Serching for : {element.code_med}")
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
        umuti_set.px_T_vente += int(umuti.quantity * umuti.prix_vente)
        umuti_set.benefice += int(umuti.quantity) * \
            int(umuti.prix_vente - umuti.prix_achat)
        umuti_set.px_T_rest -= umuti_set.px_T_vente

        umuti_set.save()

        return umuti_set

    def _recordNew(self, umuti:UmutiSold):
        """Here we record new umuti report"""
        record_new = umutiReportSell.objects.create()
        record_new.code_med = umuti.code_med
        record_new.nom_med = umuti.nom_med
        record_new.nb_vente = umuti.quantity
        record_new.px_T_vente = int(umuti.prix_vente) * \
            int(umuti.quantity)
        # record_new.benefice = int(umuti.prix_vente * umuti.quantity) - \
        #                         int(umuti.prix_achat * umuti.quantity)
        record_new.benefice = int(umuti.prix_vente - umuti.prix_achat) * \
                                int (umuti.quantity)
        try:
            current = ImitiSet.objects.get(code_med=umuti.code_med)
            record_new.nb_rest = int(current.quantite_restant)
            record_new.px_T_rest = int(current.quantite_restant * \
                                    current.prix_vente)
        except ImitiSet.DoesNotExist:
            pass
        
        record_new.save()

        return record_new
    
    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
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
                umuti_exist_15 = ventes_15.filter(code_med=umuti['code_med'])
                # check that the actual umuti is among one sold within the past two weeks.
                if umuti_exist_15:
                    final_imiti.append(umuti)
        
        if final_imiti:
            # result = ImitiSuggestSeria(instance=final_imiti, many=True)
            result = ImitiSuggestSeria(final_imiti, many=True)
            print(f"THe imitiFinal : {final_imiti} ")
            if result.is_valid:
                print(f"The final recommandation: {final_imiti}")
                return Response(result.data)
            else:
                print(f"Things are not well serialized")
        else:
            print(f"There are no recommandations.")
            return JsonResponse({"response":"empty"})
            
        return JsonResponse({"Things are ":"well"})
    

    def _getLess35(self):
        """THis one returns a list of objects from imitiSet with less than
          35% of the remaining quantity"""
        imiti = ImitiSet.objects.all()
        less_35 = []
        for umuti in imiti:
            if (umuti.qte_entrant_big / (umuti.quantite_restant | 1)) < 3.5:
                obj = {
                    'code_med': umuti.code_med,
                    'nom_med' : umuti.nom_med,
                    'quantite_restant' : umuti.quantite_restant
                }
                less_35.append(obj)
        
        if less_35:
            return less_35
        else:
            return None
    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def beneficeEval(self, request):
        """THis endpoint returns the all imitiSold according to the 
        benefice.
        It works on date1 and date2, yesterday and today instead of None.
        """
        dataReceived = request.data
        date1 = dataReceived.get('date1')
        date2 = dataReceived.get('date2')
        
        # deleting all the instances of imitiSuggest
        imitiSuggest.objects.all().delete()

        # checking that there are keys as date1 and date2
        if not (date1 and date2):
            print(f"The data sent is wrong formatted")
            # The assign date1 and date2 with a default values of 
            # yesterday and today
            date1 = timezone.now() - timedelta(days=2) # before yesterday
            date2 = date1 + timedelta(days=2) # tomorrow, I know date2 would have today() but more tierce would be added, to be precise.
                
        print(f"THe dates are: {date1} and {type(date2)}")
        # now read the UmutiSold table with parameters of date1 & date2
        try:
            queryset = UmutiSold.objects.filter(date_operation__gte=date1).\
                filter(date_operation__lte=date2)
        except ValidationError:
            return JsonResponse({"Format Date":"Incorrect"})
        
        print(f"THe queryset is: {queryset}")   

        # parcourir le queryset
        for instance in queryset:
            obj = {
                'nom_med' : instance.nom_med,
                'code_med' : instance.code_med,
                'qte' : instance.quantity,
                'p_achat' : instance.prix_achat * instance.quantity,
                'p_vente' : instance.prix_vente * instance.quantity,
                'benefice' : (instance.prix_vente - instance.prix_achat) * \
                        instance.quantity,
                'previous_date': instance.date_operation
            }             
            print(f"The obj is: {obj}")

            add_suggest = self._addSuggestion(obj)
        
        # Add qte_big and qte_restant in case there is 'rest' key in request
        if dataReceived.get('rest'):
            add_qte = self._addQte()
        
        # Now query all the instances of imitiSuggest  according to benefice
        suggestion = imitiSuggest.objects.all().order_by('-benefice')
        suggestion_seria = imitiSuggestSeria(suggestion, many=True)
        
        if suggestion_seria.is_valid:
            # deleting all the instances of imitiSuggest
            # imitiSuggest.objects.all().delete()
            return Response(suggestion_seria.data)
        
        return JsonResponse({"Everyone is": "right"})
    
    def _addQte(self):
        """This method adds qte_big and qte_restant."""
        suggestion = imitiSuggest.objects.all()
        for element in suggestion:
            try:
                selected = ImitiSet.objects.\
                    get(code_med=element.code_med)
            except ImitiSet.DoesNotExist:
                pass
            else:
                element.qte_big = selected.qte_entrant_big
                element.qte_restant = selected.quantite_restant
                element.save()
        return 200
    def _addSuggestion(self, obj):
        """This method receives an obj and adds it on imitiSuggest Model.
        """
        # checking the existence of obj in imitiSuggest
        try:
            exist_suggest = imitiSuggest.objects.get(code_med=obj.\
                                                     get('code_med'))
        except imitiSuggest.DoesNotExist:
            new_suggest = imitiSuggest.objects.create()
            new_suggest.code_med = obj.get('code_med')
            new_suggest.nom_med = obj.get('nom_med')
            new_suggest.qte = obj.get('qte')
            new_suggest.p_achat = obj.get('p_achat')
            new_suggest.p_vente = obj.get('p_vente')
            new_suggest.benefice = obj.get('benefice')
            new_suggest.previous_date = obj.get('previous_date')
            new_suggest.save()

            return 200
        else:
            exist_suggest.qte += int(obj.get('qte'))
            exist_suggest.p_achat += int(obj.get('p_achat'))
            exist_suggest.p_vente += int(obj.get('p_vente'))
            exist_suggest.benefice += int(obj.get('benefice'))
            exist_suggest.previous_date = obj.get('previous_date')
            exist_suggest.save()
            
            return 200
    

    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def isAdmin(self, request):
        """This endpoint asks that an authenticated user is an Admin 
        or not."""
        user = request.user
        print(f"THe user connected is Admin: {user.is_superuser}")

        return JsonResponse({"isAdmin": user.is_superuser})
    

    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def giveLastIndex(self, request):
        """This endpoint returns the last ID in the following models:
        1. UmutiEntree;
        2. UmutiSold.
        """
        last_umutiEntree = UmutiEntree.objects.last()
        last_umutiSold = UmutiSold.objects.last()

        obj = {
            'last_umutiEntree': last_umutiEntree.id,
            'last_umutiSold' : last_umutiSold.id
        }
        print(f"THe obj : {obj}")
        obj_serialized = LastIndexSeria(obj)
        if obj_serialized.is_valid:
            return Response(obj_serialized.data)

        return JsonResponse({"done":"ok"})
    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getForSync(self, request):
        """This endpoint will retrieve the above instances from 
        parameters."""
        data_gotten = request.data.get('imiti')
        print(f"getForSync, The data gotten {data_gotten}")
        last_umutiEntree = int(data_gotten.get('last_umutiEntree'))
        last_umutiSold = int(data_gotten.get('last_umutiSold'))
        imitiEntree = UmutiEntree.objects.filter(id__gt=last_umutiEntree)
        imitiSold = UmutiSold.objects.filter(id__gt=last_umutiSold)

        imitiEntree_serialized = UmutiEntreeSeriazer(imitiEntree,\
                                                      many=True)
        imitiSold_serialized = UmutiSoldSeriazer(imitiSold, many=True)
        obj = {}
        if imitiEntree_serialized.is_valid:
            obj['last_umutiEntree'] = imitiEntree_serialized.data
        if imitiSold_serialized.is_valid:
            obj['last_umutiSold'] = imitiSold_serialized.data

        return Response(obj)
    

    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def syncFromLocal(self, request):
        """This endpoint will write records according to the index."""
        data_sent = request.data.get('imiti')
        # first take the new umutiEntree instances.
        # last_umutiEntree = data_sent.get('last_umutiEntree')
        # Mimic the last_umutiEntree
        print(f"syncFromLocal, The data sent: {data_sent}")
        last_umutiEntree = [
            {
                'date_entrant': "2024-07-05T08:38:34.519033Z",
                'date_peremption': "2027-04-01",
                'code_med': "4X6768",
                'nom_med': "AMINOPHYLLINE",
                'description_med': "2024-07-05 08:38:34.519033",
                'famille_med': "Ovule",
                'type_achat': "Carton",
                'ratio': 10,
                'type_vente': "Piece",
                'prix_vente': 1500,
                'prix_vente': 1800,
                'difference': 0,
                'quantite_initial': 15,
                'quantite_restant': 15,
                'location': "",
                'code_operation': "fVobVV41Dbkt",
                'operator': "User1",
            }
        ]
        last_umutiEntree = data_sent.get('last_umutiEntree')
        rep = self._entree(entree=last_umutiEntree) # write these new instances into UmutiEntree model.
        rep = self._entree(entree=last_umutiEntree, sort=2) # write these new instances into UmutiEntreeBackup model.

        # Mimic a list of UmutiSold
        last_umutiSold = [
            {
                'code_med': '055AWL',
                'nom_med': 'Quinine',
                'quantity': 1,
                'prix_vente': 2500,
                'price_total': 1,
                'prix_vente': 2200,
                'difference': 0,
                'code_operation_entrant': 'kUyVk390907W',
                'code_operation': '875mOdv17417',
                'operator': 'User1',
                'date_operation': "2024-07-05T08:08:24.138300Z",

            },
        ]
        last_umutiSold = data_sent.get('last_umutiSold')
        rep = self._entree_sold(sold=last_umutiSold) # will work on entree and Sold


        return JsonResponse({"done":""})
    
    def _entree(self, entree:list, sort:int=1)->int:
        """This method will populate new instances of UmutiEntree."""
        for umuti_entree in entree:
            # make distinction where to write
            if sort == 1: #for UmutiEntree
                check = UmutiEntree.objects.filter(code_operation=\
                    umuti_entree.get('code_operation')).filter(code_med=\
                    umuti_entree.get('code_med'))
                if not len(check): # will remove 'not' when on real data.
                    continue # In case there is such instance
                umuti_new = UmutiEntree.objects.create()

            elif sort == 2:   #for UmutiEntreeBackup
                check = UmutiEntreeBackup.objects.filter(code_operation=\
                    umuti_entree.get('code_operation')).filter(code_med=\
                    umuti_entree.get('code_med'))
                if not len(check): # will remove 'not' when on real data.
                    continue # In case there is such instance
                umuti_new = UmutiEntreeBackup.objects.create()

            umuti_new.date_entrant = umuti_entree.get('date_entrant')
            umuti_new.date_peremption = umuti_entree.get('date_peremption')
            umuti_new.code_med = umuti_entree.get('code_med')
            umuti_new.nom_med = umuti_entree.get('nom_med')
            umuti_new.description_umuti = umuti_entree.get('description_med')
            umuti_new.type_med = umuti_entree.get('famille_med')
            umuti_new.type_achat = umuti_entree.get('type_achat')
            umuti_new.ratio = umuti_entree.get('ratio')
            umuti_new.type_vente = umuti_entree.get('type_vente')
            umuti_new.prix_achat = umuti_entree.get('prix_vente')
            umuti_new.prix_vente = umuti_entree.get('prix_vente')
            umuti_new.difference = umuti_entree.get('difference')
            umuti_new.quantite_initial = umuti_entree.get('quantite_initial')
            umuti_new.quantite_restant = umuti_entree.get('quantite_restant')
            umuti_new.location = umuti_entree.get('location')
            umuti_new.code_operation = umuti_entree.get('code_operation')
            umuti_new.operator = umuti_entree.get('operator')

            umuti_new.save()
        return 200
    
    def _entree_sold(self, sold:list)->int:
        """ Will work imitiEntree and UmutiSold"""
        for umutisold in sold:
            code_operation_entrant = umutisold.get('code_operation_entrant')
            code_med = umutisold.get('code_med')
            # check the equality of remaining
            now_umuti = UmutiEntree.objects.filter(code_operation=\
                code_operation_entrant).filter(code_med=code_med)
            if not len(now_umuti): 
                continue
            
            now_umuti[0].quantite_restant -= umutisold.get('quantity')         

            # creating UmutiSold instance and clone umutisold
            umuti_new = self.__cloneUmutisold(instance=umutisold)
            if not umuti_new:
                pass # should signal that things didn't go well.
            
            # saving/updating  the existing UmutiEntree
            now_umuti[0].save()
    
    def __cloneUmutisold(self, instance)->int:
        """manage creating UmutiSold instance and clone umutisold."""
        new_umuti = UmutiSold.objects.create()
        new_umuti.code_operation = instance.get('code_operation')
        new_umuti.code_med = instance.get('code_med')
        new_umuti.nom_med = instance.get('nom_med')
        new_umuti.quantity = instance.get('quantity')
        new_umuti.prix_vente = instance.get('prix_vente')
        new_umuti.price_total = instance.get('price_total')
        new_umuti.prix_achat = instance.get('prix_vente')
        new_umuti.difference = instance.get('difference')
        new_umuti.code_operation_entrant = instance.get('code_operation_entrant')
        new_umuti.operator = instance.get('operator')
        new_umuti.date_operation = instance.get('date_operation')

        new_umuti.save()

        return 200
    

    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getInstances(self, request):
        """Will query the instances requested."""
        data_sent = request.data
        imiti_entree = UmutiEntree.objects.filter(id__gte=\
                    data_sent.get(last_umutiEntree))
        imiti_sold = UmutiSold.objects.filter(id__gte=\
                    data_sent.get(last_umutiSold))
        
        imiti_entree_serialized = UmutiEntreeSeriazer(imiti_entree,\
                                     many=True)
        imiti_sold_serialized = UmutiSoldSeriazer(imiti_sold, many=True)

        if imiti_entree_serialized.is_valid \
              and imiti_sold_serialized.is_valid:
            # the obj to send to the server.
            obj = {
                'last_umutiEntree': imiti_entree_serialized.data,
                'last_umutiSold': imiti_sold_serialized.data
            }
            return Response(data=obj)
        # in case it didn't pass
        return JsonResponse({"It didn't":"pass"})

    @action(methods=['get'], detail=False,\
             permission_classes= [AllowAny])
    def getInstance(self, request):
        """Will query the instances requested."""
        data_sent = request.data
        imiti_entree = UmutiEntree.objects.filter(id__gte=1)
        imiti_sold = UmutiSold.objects.filter(id__gte=1)
        
        imiti_entree_serialized = UmutiEntreeSeriazer(imiti_entree,\
                                     many=True)
        imiti_sold_serialized = UmutiSoldSeriazer(imiti_sold, many=True)

        if imiti_entree_serialized.is_valid \
              and imiti_sold_serialized.is_valid:
            # the obj to send to the server.
            obj = {
                'last_umutiEntree': imiti_entree_serialized.data,
                'last_umutiSold': imiti_sold_serialized.data
            }
            return Response(data=obj)
        # in case it didn't pass
        return JsonResponse({"It didn't":"pass"})
    

    @action(methods=['get'], detail=False,\
             permission_classes= [AllowAny])
    def getLowStock(self, request):
        """This will return all instances of Imitiset with under
        30% and above 1%.
        Return ImitiSet."""

        imiti = ImitiSet.objects.all()
        less_25 = []
        for umuti in imiti:
            if (umuti.qte_entrant_big / (umuti.quantite_restant | 1)) > 2.5:
                less_25.append(umuti)
        
        if not len(less_25):
            return JsonResponse({"data":"empty"})
        
        less_25_serialized = ImitiSetSeriazer(less_25, many=True)
        if less_25_serialized.is_valid:
            return Response(less_25_serialized.data)

        
    
    @action(methods=['get'], detail=False,\
             permission_classes= [AllowAny])
    def getEndStock(self, request):
        """This will return all instances of Imitiset with under 1%.
        Return ImitiSet."""

        imiti = ImitiSet.objects.all()
        less_one = []
        for umuti in imiti:
            if umuti.quantite_restant  == 0:
                less_one.append(umuti)
        
        if not len(less_one):
            return JsonResponse({"data":"empty"})
        
        less_one_serialized = ImitiSetSeriazer(less_one, many=True)
        if less_one_serialized.is_valid:
            return Response(less_one_serialized.data)
    
    @action(methods=['get'], detail=False,\
             permission_classes= [AllowAny])
    def getOutDate(self, request):
        """This will return all instances of UmutiEntree 
        with and with quantite_restant above 0 and
          date_peremption less than 3months.
        Return UmutiEntree."""
        
        date_notice = timezone.now() + timedelta(days=90)
        queryset = UmutiEntree.objects.filter(quantite_restant__gte=1).\
            filter(date_peremption__lte=date_notice)
        
        if not len(queryset):
            return JsonResponse({"data":"empty"})
        queryset_serialized = UmutiEntreeSeriazer(queryset, many=True)
        if queryset_serialized.is_valid:
            return Response(queryset_serialized.data)
        
        return JsonResponse({"It did":"pass"})
        
    
    @action(methods=['get'], detail=False,\
             permission_classes= [AllowAny])
    def getAllFine(self, request):
        """This endpoint works all instances of UmutiEntree and ImitiSet with
        no wrong case.
        Return UmutiEntree."""

        code_med = ''
        pure_result = [] # UmutiEntree
        date_notice = timezone.now() + timedelta(days=90)
        imiti = ImitiSet.objects.all()

        for umuti in imiti:
            code_med = umuti.code_med
            if (umuti.qte_entrant_big / (umuti.quantite_restant | 1)) > 2.5 :
                continue # the quantity is not safe

            # kuri iyo code, raba iyifise date imeze neza
            safe_date = UmutiEntree.objects.filter(code_med=code_med).\
                filter(date_peremption__gte=date_notice)
            if len(safe_date):
                pure_result += safe_date # should add the Queryset instead of appending.
        
        if not len(pure_result):
            return JsonResponse({"data":"empty"})
        
        result_serialized = UmutiEntreeSeriazer(pure_result, many=True)
        if result_serialized.is_valid:
            return Response(result_serialized.data)
    

    @action(methods=['get','post'], detail=False,\
             permission_classes= [AllowAny])
    def getVentes(self, request):
        """
        This will return ventes journalieres.
        7days for default from today.
        """
        data_params = request.data
        end_date = None
        begin_date = None
        # checking that there is dates object
        # the set end_date and begin_date
        # else, set these defaults value of 7days
        if data_params.get('dates'):
            if data_params.get('dates')[0]:
                date1 = data_params.get('dates')[0]
                date_arr = shortStr2Date(date1)
                begin_date = timezone.datetime(date_arr[0],\
                    date_arr[1], date_arr[2])
            if data_params.get('dates')[1]:
                date2 = data_params.get('dates')[1]
                date_arr = shortStr2Date(date2)
                end_date = timezone.datetime(date_arr[0],\
                    date_arr[1], date_arr[2])
        else:
            end_date = timezone.now()
            end_date -= timedelta(hours=end_date.hour) #init to 0:00
            begin_date = end_date - timedelta(days=7)
        print("THe dates are: ", begin_date, end_date)
        x = [] # date
        y = [] # quantifiers
        while begin_date != end_date:
            query = UmutiSold.objects.filter\
                (date_operation__gte=begin_date)\
                .filter(date_operation__lt=begin_date+timedelta(days=0.8))
            # date_str = (str(begin_date)).split()[0]
            week_day = datetime.weekday(begin_date)
            x.append(week_days[week_day+1])
            y.append(len(query))
            begin_date += timedelta(days=1)
        return JsonResponse({"X":x, 'Y':y})
    
    def _getDate(self, data_params)->list:
        end_date = None
        begin_date = None
        # checking that there is dates object
        # the set end_date and begin_date
        # else, set these defaults value of 7days
        if data_params.get('dates'):
            if data_params.get('dates')[0]:
                date1 = data_params.get('dates')[0]
                date_arr = shortStr2Date(date1)
                begin_date = timezone.datetime(date_arr[0],\
                    date_arr[1], date_arr[2])
            if data_params.get('dates')[1]:
                date2 = data_params.get('dates')[1]
                date_arr = shortStr2Date(date2)
                end_date = timezone.datetime(date_arr[0],\
                    date_arr[1], date_arr[2])
        else:
            end_date = timezone.now()
            end_date -= timedelta(hours=end_date.hour) #init to 0:00
            begin_date = end_date - timedelta(days=7)
        print("THe dates are: ", begin_date, end_date)

        return [begin_date, end_date]
    
    def _builtVente(self, meds):
        """
        Will return a mixed info from
          UmutiSold, BonDeCommande and Assurance.
        needed dict: {
            'nom_med', 'qte', 'pa','pv','total','bnf',
            'caisse', 'dette', 'assu', 'categ','date',
            'id_bon', 'is_paid'
        }
        """
        bons = []
        for umuti_sold in meds:
            vente = {}
            vente['nom_med'] = umuti_sold.nom_med
            vente['qte'] = umuti_sold.quantity
            vente['prix_achat'] = umuti_sold.prix_achat
            vente['prix_vente'] = umuti_sold.prix_vente
            vente['total'] = umuti_sold.prix_vente * umuti_sold.quantity
            vente['bnf'] = (umuti_sold.prix_vente - umuti_sold.prix_achat)\
                            * umuti_sold.quantity
            bon = umuti_sold.bon_de_commande
            assu = bon.organization
            assu_name = assu.name
            rate = assu.rate_assure
            vente['dette'] = bon.montant_dette
            vente['caisse'] = vente['total'] - bon.montant_dette
            if bon.montant_dette:
                vente['dette'] = vente['total'] - bon.montant_dette
                vente['caisse'] = bon.montant_dette
            vente['assu'] = assu_name
            vente['categ'] = bon.categorie
            vente['date_operation'] = bon.date_du_bon
            vente['date_served'] = bon.date_served
            vente['num_du_bon'] = bon.num_du_bon
            vente['is_paid'] = bon.is_paid

            bons.append(vente)

            # print(f"Bon {vente};")
        
        return bons
    
    @action(methods=['get','post'], detail=False,\
             permission_classes= [AllowAny])
    def getDiffStock(self, request):
        """
        Will return the categorized level of stocks.
        """
        today = timezone.now()
        qte_sup = UmutiEntree.objects.filter(quantite_restant__gte=1)
        six_month = today +timedelta(days=180)
        one_year = today + timedelta(days=360)
        two_year = today + timedelta(days=720)

        outdated = qte_sup.filter(date_peremption__lte=today)
        with_less_six_month = qte_sup.filter(date_peremption__gt=today)\
            .filter(date_peremption__lt=six_month)
        with_six_month = qte_sup.filter(date_peremption__gte=six_month)\
            .filter(date_peremption__lte=one_year)
        with_one_year = qte_sup.filter(date_peremption__gte=one_year)\
            .filter(date_peremption__lte=two_year)
        with_two_year = qte_sup.filter(date_peremption__gte=two_year)

        y = ['Perimé', '1-5mois', '6-12mois',\
            '12-24mois','24mois +']
        x = [len(outdated), len(with_less_six_month), \
            len(with_six_month), len(with_one_year),\
                len(with_two_year)]
        return JsonResponse({"X":x, "Y":y})
    
    
    @action(methods=['get','post'], detail=False,\
             permission_classes= [AllowAny])
    def getUnpaidUmutiSold(self, request):
        """
        Return UmutiSold instance(s) with the unpaid BonDeCommande.
        default range is 7 days.
        """
        begin_date, end_date = self._getDate(request.data)
        # queryset = BonDeCommande.filter(date_du_bon__gte=begin_date)\
        #     .filter(date_du_bon__lte=end_date)\
        #     .filter(is_paid=False)
        queryset = UmutiSold.objects.filter\
            (bon_de_commande__date_du_bon__gte=begin_date)\
            .filter(bon_de_commande__date_du_bon__lte=end_date)\
            .filter(bon_de_commande__is_paid=True)
        query_seria = UmutiSoldSeriazer(queryset,\
                                        many=True)
        if query_seria.is_valid:
            return Response(query_seria.data)
        return JsonResponse({"Something":"is not right"})
    


