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
from django.db.models import Q
from django.contrib.auth.models import User
from datetime import timedelta, datetime
import os

#importing my models from Pharma
from pharma.models import UmutiEntree, ImitiSet, UmutiSold, \
    umutiReportSell, imitiSuggest, UmutiEntreeBackup, UsdToBif,\
    BonDeCommand, Assurance, ClassThep, SubClassThep,\
    Client, BeneficeProgram, Journaling, CriticalOperation, \
    Info, PerteMed

#importing the serializers
from .serializers import ImitiSetSeriazer, UmutiSoldSeriazer,\
      UmutiEntreeSeriazer, ImitiSuggestSeria, imitiSuggestSeria, \
      LastIndexSeria, SyntesiSeria, AssuranceSeria,\
      ClientSeria, BonDeCommandSeria, OperationSeria, \
    CollectionSeria, InfoSeria

#importing my additional code
from .code_generator import GenerateCode
from .shared.stringToList import StringToList
from .shared.listStrToList import listDictIntSomme2
from .shared.stringToDate import stringToDate, shortStr2Date
# from .shared.superiorInput import superiorInput
from .shared.roundingNumber import roundNumber
from .shared.syncCode import give_sync_code
from .shared.initLot import init_lot

import requests


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
# Global function
def recordOperation(who_did_id, what_operation:str, from_value:str, to_value:str)->int:
    """
    creates an instance: CriticalOperation
    """
    new_record = CriticalOperation.objects.create(who_did_it=who_did_id)
    msg = f"{what_operation} : {from_value} ==> {to_value}."
    new_record.operation = msg
    new_record.save()
    return 200

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
        num_client = self._createInitClient()
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
            bon_default = BonDeCommand.objects.filter\
                (organization__name='Sans').first()
        except BonDeCommand.DoesNotExist:
            client_ordi = Client.objects.get(beneficiaire="Ordinary")
            assu_sans = Assurance.objects.get(name="Sans")
            bon_default = BonDeCommand.objects\
                .create(beneficiaire=client_ordi, \
                    organization=assu_sans)
            bon_default.num_bon = '0001'
            bon_default.is_paid = True
            bon_default.save()
            created.append("Default BdC")
        
        taux_usd = UsdToBif.objects.first()
        if not taux_usd:
            new_taux = UsdToBif.objects.create()
            new_taux.actualExchangeRate = 6200
            new_taux.save()
        minimum_benefice = BeneficeProgram.objects.first()
        ben = 0
        if not minimum_benefice:
            minimum_benefice = BeneficeProgram.objects.create()
            minimum_benefice.save()
            ben = 1
        journal = Journaling.objects.first()
        journal_i = 0
        if not journal:
            journal = Journaling.objects.create()
            journal.codes_for_sync = []
            journal.save()
            journal_i = 1
        cls = self._createClasses_cloned()
        
        created.append(f"with {cls} ther. classes")
        created.append(f"{num_client} Init clients")
        created.append(f"ben : {ben}")
        created.append(f"Journal : {journal_i}")

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
            assu_name = data_sent.get('assu')[0]
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
    
    @action(methods=['post', 'get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def addClient(self, request):
        data_sent = request.data
        status = False
        print("The data sent:", data_sent)
        return JsonResponse({"status": 1,\
                                'reason':"Client ajoutee"},\
                                status=200)
    
    @action(methods=['post', 'get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getClients(self, request):
        queryset = Client.objects.exclude(\
            Q(nom_adherant="Self"))
        query_seria = ClientSeria(queryset, many=True)
        if query_seria.is_valid:
            return Response(query_seria.data)
        return JsonResponse({"status": 1,\
                                'reason':"Client ajoutee"},\
                                status=200)
    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def listUser(self, request):
        users = User.objects.all()
        users_obj = {}
        for user in users:
            users_obj[user.id] = user.username
        return Response({
            'response': users_obj
        })
    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def update_nom_med(self, request):
        data = request.data.get('imiti')
        code_med = data.get('code_med', None)
        nom_med = data.get('nom_med', None)
        if not(code_med and nom_med):
            return Response({
                'response': 404
            })
        try:
            exist_med = ImitiSet.objects.get(nom_med=nom_med)
        except ImitiSet.DoesNotExist:
            pass
        else:
            return Response({
                'response': 0
            })
        med = ImitiSet.objects.get(code_med=code_med)
        old_nom_med = med.nom_med
        op1 = self._nom_achat(code_med=code_med, nom_med=nom_med)
        op2 = self._nom_achat_2(code_med=code_med, nom_med=nom_med)
        if op1+op2 == 400:
            med.nom_med = nom_med
            med.save()
        recordOperation(who_did_id=request.user,\
                        what_operation="Changé le nom",\
                        from_value=old_nom_med,\
                        to_value=nom_med)
        self._update_code_for_sync(code_med=code_med)
        return Response({
            'response': 1
        })
    
    def _nom_achat(self, code_med:str, nom_med:str)->int:
        meds = UmutiEntree.objects.filter(code_med=code_med)
        if not meds:
            return 403
        
        for med in meds:
            med.nom_med = nom_med
            med.save()

        return 200
    
    def _nom_achat_2(self, code_med:str, nom_med:str)->int:
        meds = UmutiEntreeBackup.objects.filter(code_med=code_med)
        if not meds:
            return 403
        
        for med in meds:
            med.nom_med = nom_med
            med.save()
            
        return 200


    
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
            bon_default = BonDeCommand.objects.get\
                (organization__name='Sans')
        except BonDeCommand.DoesNotExist:
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
        Returns all instances of Assurances, except
        of name: 'Sans' and 'Pharmacie Ubuzima'
        """
        assu = Assurance.objects\
            .exclude(Q(name='Sans')| \
                     Q(name="Pharmacie Ubuzima"))
        assu_seria = AssuranceSeria(assu, many=True)
        if assu_seria.is_valid:
            return Response(assu_seria.data)
        return JsonResponse({"status": 0,\
                            'reason':'server failed'},\
                            status=406)
    
    @action(methods=['get'], detail=False,\
             permission_classes= [AllowAny])
    def getDefRate(self, request):
        """
        Returns the assu_rate for Pharmacie Ubuzima
        """
        query = Assurance.objects.filter(name="Pharmacie Ubuzima")
        if query:
            assu_rate = query[0].rate_assure
            return JsonResponse({"status": 1,\
                                'reason':"Client ajoutee",\
                                'rep': assu_rate},\
                                status=200)
        return JsonResponse({"status": 0,\
                                'reason':"Client ajoutee",\
                                'rep': 0},\
                                status=404)
    
    @action(methods=['post'], detail=False,\
             permission_classes= [AllowAny])
    def setBons(self, request):
        """
        Sets to true the given instances of BonDeCommand
        """ 
        bon_ids = request.data.get('imiti')
        print("THe requested data Set:", bon_ids)

        for id in bon_ids:
            try:
                bon = BonDeCommand.objects.get(num_bon=id)
            except BonDeCommand.DoesNotExist:
                return JsonResponse({"status": 0,\
                            'reason':'Bon invalide'},\
                            status=406)
            else:
                bon.is_paid = True
                bon.date_is_paid = timezone.now().date()
                bon.save()
        
        return JsonResponse({"status": 1,\
                            'reason':'request completed'},\
                            status=200)

    @action(methods=['post'], detail=False,\
             permission_classes= [AllowAny])
    def getBons(self, request):
        """
        Returns all instances of BonDeCommand
        """
        requested_data = request.data.get('imiti')
        print("THe requested data:", requested_data)
        request_bons = []
        for bon in requested_data:
            try:
                query = BonDeCommand.objects.get(id=bon)
            except BonDeCommand.DoesNotExist:
                return JsonResponse({"status": 0,\
                            'reason':'Bon invalide'},\
                            status=406)
            else:
                request_bons.append(query)
        bons_seria = BonDeCommandSeria(request_bons, many=True)
        if bons_seria.is_valid:
            return Response(bons_seria.data)
        
        return JsonResponse({"status": 0,\
                            'reason':'erreur du serveur'},\
                            status=406)
    
    @action(methods=['post'], detail=False,\
             permission_classes= [AllowAny])
    def getInfo(self, request):
        """
        Should return infos from code_operation in UmutiSold.
        """
        # sent_data = request.data.get('imiti').get('_value')
        sent_data = request.data.get('imiti')
        print(f"The sent_data: {sent_data}")
        if not sent_data:
            return JsonResponse({"response": 'NoneType'})
        codes = sent_data.split(';')
        codes = codes[:len(codes)-1]
        infos = []
        for code in codes:
            obj = {}
            umuti = UmutiSold.objects.get(code_operation=code)
            obj['nom_med'] = umuti.nom_med
            obj['quantity'] = umuti.quantity
            obj['prix_vente'] = umuti.prix_vente
            obj['operator'] = umuti.operator
            infos.append(obj)
        return JsonResponse({"response":infos})
    
    def _createClasses_cloned(self)->int:
        """
        For creating therap. class and sub-class
        """
        c1 = ['Anesthesie_et_Reanimation',
                'Anesthésiques généraux',
                'Anesthésiques locaux',
                'Agents de réanimation',
                'Autre'
                ]
        c2 = ['Antalgiques_Analgesiques',
                'Antalgiques périphériques',
                "Antalgiques centraux (Opioïdes et dérivés)",
                'Autre'
                ]
        c3 = ['Anti_inflammatoires',
                "AINS (Anti-Inflammatoires Non Stéroïdiens)",
                "Corticostéroïdes",
                "Inhibiteurs de COX-2",
                'Autre'
                ]
        c4 = ['Cancerologie_et_Hematologie',
                'Chimiothérapies',
                'Immunothérapies',
                "Thérapies ciblées",
                "Agents hématopoïétiques",
                'Autre'
                ]
        c5 = ['Cardiologie_et_Angiologie'
                "Anti-hypertenseurs",
                "Antiarythmiques",
                "Antiangineux",
                "Anticoagulants",
                "Diurétiques",
                'Autre'
                ]
        c6 = ['Contraception_et_Interruption_de_Grossesse',
                "Contraceptifs oraux",
                "Contraceptifs injectables",
                "Dispositifs intra-utérins",
                'Autre'
                ]
        c7 = ['Dermatologie',
                "Antifongiques locaux",
                "Antibactériens locaux",
                "Corticostéroïdes topiques",
                "Anti-allergiques",
                'Autre'
                ]
        c8 = ['Endocrinologie',
                "Antidiabétiques oraux",
                'Insulines',
                'Hormonothérapies',
                'Autre'
                ]
        c9 = ['Gastro_Entero_Hepatologie',
                "Antiulcéreux et Antiacides",
                'Laxatifs',
                'Antidiarrhéiques',
                'Hépatoprotecteurs',
                'Antispasmodiques',
                'Anti-vomitique',
                'Autre'
                ]
        c10 = ['Gynecologie',
                "Oestrogènes et Progestatifs",
                "Traitement des infections gynécologiques",
                "Uterotoniques",
                "Antispasmodiques",
                'Autre'
                ]
        c11 = ['Hemostase_et_Sang',
                "Facteurs de coagulation",
                "Antifibrinolytiques",
                "Produits sanguins",
                'Autre'
                ]
        c12 = ['Immunologie',
                'Vaccins',
                'Immunoglobulines',
                'Immunosuppresseurs',
                'Autre'
                ]
        c13 = ['Infectiologie_Parasitologie',
                'Antibiotiques',
                'Antiviraux',
                'Antiparasitaires',
                'Antifongiques',
                'Autre'
                ]
        c14 = ['Metabolisme_et_Nutrition',
                "Suppléments nutritionnels",
                "Régulateurs de l'appétit",
                'Autre'
                ]
        c15 = ['Neurologie_Psychiatrie',
                'Antidépresseurs',
                'Anxiolytiques',
                'Antipsychotiques',
                'Antiépileptiques',
                'Autre'
                ]
        c16 = ['Ophtalmologie',
                'Antiglaucomateux',
                'Mydriatiques',
                "Lubrifiants oculaires",
                "Antibiotiques",
                "Corticoides",
                'Autre'
                ]
        c17 = ['Oto_Rhino_Laryngologie',
                'Antihistaminiques',
                'Décongestionnants',
                "Anti-inflammatoires",
                'Autre'
                ]
        c18 = ['Pneumologie',
                'Bronchodilatateurs',
                "Corticostéroïdes inhalés",
                'Antileucotriènes',
                'Expectorants',
                'Autre'
                ]
        c19 = ['Rhumatologie',
                "DMARDs (Disease-Modifying Antirheumatic Drugs)",
                "Anti-inflammatoires",
                'Biothérapies',
                "Myorelaxants",
                'Autre'
                ]
        c20 = ['Sang_et_Derives',
                'Érythropoïétine',
                'Plasma',
                "Concentrés de plaquettes",
                'Autre'
                ]
        c21 = ['Stomatologie'
                "Antiseptiques buccaux"
                "Analgésiques bucco-dentaires",
                'Autre'
                ]
        c22 = ['Toxicologie',
                'Antidotes',
                'Chélateurs',
                'Autre'
                ]
        c23 = ['Urologie_et_Nephrologie',
                'Diurétiques',
                'Anticholinergiques',
                "Suppléments de potassium",
                'Autre'
                ]
        c24 = ['Hygiene_et_Protection',
                'Gants',
                'Masques',
                'Blouses',
                'Bottes',
                "Produits antisceptiques",
                'Autre'
                ]
        c25 = ['Autre',
                'Autre'
                ]
        all_cs = [c1, c2, c3, c4, c5, c6, c7,\
            c7, c8, c9, c10, c11, c12, c13, c14,\
            c15, c16, c17, c18, c19, c20, c21,\
            c22, c23, c24, c25]
        all_cs.reverse()
        i, counter = 0, 0
        len_cs = len(all_cs)
        while counter < len_cs:
            cl = all_cs.pop()
            cl_make = self._createOneClass(cl)
            if cl_make == 200: i += 1
            counter += 1
        
        return i
    
    def _createOneClass(self, data)->int:
        """
        creates a ther.class with its members.
        """
        cl_name = ClassThep.objects.filter(name=data[0])
        if (not len(data)) or (len(cl_name)):
            return 0

        cl_object = None
        n_group = GenerateCode(4).giveCode()
        cl_object = ClassThep.objects.\
                    create()
        cl_object.name = (data[0])[:69]
        cl_object.n_group = n_group
        cl_object.save()

        for s_cl in data[1:]:
            sub_cl_obj = SubClassThep.objects\
                .create(parent=cl_object)
            sub_cl_obj.name = (str(s_cl))[:69]
            sub_cl_obj.n_group = n_group
            sub_cl_obj.save()
        
        return 200
    
    def _createInitClient(self)->int:
        """
        Will create two instances of Client:
        1. beneficiaire: Ordinary,
        2. beneficiaire: Special 
        """
        ordinary = None
        created = 0
        try:
            ordinary = Client.objects.get(beneficiaire="Ordinary")
        except Client.DoesNotExist:
            ordinary = Client.objects.create(beneficiaire="Ordinary")
            ordinary.employeur = "Self"
            ordinary.joined_on = timezone.now()
            ordinary.nom_adherant = "Self"
            ordinary.numero_carte = 1
            ordinary.relation = "lui-meme"

            ordinary.save()

            created += 1
        else:
            pass
        try:
            special = Client.objects.get(beneficiaire="Special")
        except Client.DoesNotExist:
            special = Client.objects.create(beneficiaire="Special")
            special.employeur = "Self"
            special.joined_on = timezone.now()
            special.nom_adherant = "Self"
            special.numero_carte = 1
            special.relation = "lui-meme"

            special.save()

            created += 1
        else:
            pass

        return created

    
    @action(methods=['get'], detail=False,\
             permission_classes= [AllowAny])
    def getClasses(self, request):
        """
        Returns the array of classes with 
        the sub-classes:
        x = ['class-one', 'class-two']
        y = [[sub-cl-one, sub-cl-two], [sub-cl-one, sub-cl-two]]
        """
        x = []  # for classes
        y = []  # for sub-classes
        n_groups = []

        sub_classes = SubClassThep.objects.all()
        same_group = []
        code_group = ''
        local_cl = []
        for sb in sub_classes:
            code_group = sb.n_group
            if code_group not in same_group:
                same_group.append(code_group)
                y.append(local_cl)
                x.append(sb.parent.name)
                local_cl = []
            local_cl.append(sb.name)
        
        y.append(local_cl) # adding the last group of sub-class 
        y.remove([]) # removing the initial empty list

        return JsonResponse({"x":x, "y":y})
    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAdminUser])
    def getPrInterest(self, request):
        """Will return a Pr-Interest."""
        pr = BeneficeProgram.objects.first()
        return Response({
            'pr_interest': pr.ben
        })
    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAdminUser])
    def setPrInterest(self, request):
        """Will return a Pr-Interest."""
        in_sent = request.data
        print(f"THe sent: {in_sent}")
        # sent_pr = in_sent.get('imiti').get('_value')
        sent_pr = in_sent.get('imiti')
        pr = BeneficeProgram.objects.first()
        former_interest = pr.ben
        pr_interest = float(sent_pr)
        if pr_interest > 0 and pr_interest < 2:
            pr.ben = pr_interest
            pr.save()
            recordOperation(who_did_id=request.user,\
                what_operation="Changé le principe d'intérêt",\
                from_value=former_interest, \
                to_value=pr_interest)
            return Response({
                'status': pr.ben
            })
        return Response({
                'status': 0
            })

    @action(methods=['get'], detail=False,\
            permission_classes= [IsAdminUser])
    def getTxChange(self, request):
        """Will return a Pr-Interest."""
        tx = UsdToBif.objects.first()
        return Response({
            'txChange': tx.actualExchangeRate
        })
    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAdminUser])
    def setTxChange(self, request):
        """Will set a UsdToBif."""
        in_sent = request.data
        # sent_pr = in_sent.get('imiti').get('_value')
        sent_pr = in_sent.get('imiti')
        tx = UsdToBif.objects.first()
        tx_change = float(sent_pr)
        if tx_change > 1000 and tx_change < 10000:
            tx.actualExchangeRate = tx_change
            tx.save()
            return Response({
                'status': tx.actualExchangeRate
            })
        return Response({
                'status': 0
            })
    

    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def setDecimal(self, request):
        """
        Will get the id for umutiSet and return or 
        update its decimal field.
        """
        data_sent = request.data.get('imiti')
        print(f"The data sent: {data_sent}")
        if not data_sent:
            return JsonResponse({
            'response': 0
        })
        code_med = data_sent.get('code_med')
        try:
            umuti_set = ImitiSet.objects.get(code_med=code_med)
            umuti_set_seria = ImitiSetSeriazer(umuti_set)
        except ImitiSet.DoesNotExist:
            return JsonResponse({
                'response': 404,
            })
        else:
            if data_sent.get('request') == 'get':
                if umuti_set_seria.is_valid:
                    return Response(umuti_set_seria.data)
            elif data_sent.get('request') == 'post':
                umuti_set.is_decimal = bool(data_sent.get('is_decimal'))
                umuti_set.save()
                recordOperation(who_did_id=request.user, \
                        what_operation=f"Fractionner {(umuti_set.nom_med)[:15]}", \
                        from_value=(not umuti_set.is_decimal), \
                        to_value=umuti_set.is_decimal)
        return JsonResponse({
            'response': 1
        })
    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAdminUser])
    def setIndivPrInterest(self, request):
        """
        Will get the id for umutiSet and return or 
        update its pr_interest.
        """
        data_sent = request.data.get('imiti')
        print(f"The data sent: {data_sent}")
        current_value = 0
        new_value = 0
        default_pr_interest = BeneficeProgram.objects.first().ben
        if not data_sent:
            return JsonResponse({
            'response': 0
        })
        code_med = data_sent.get('code_med')
        try:
            umuti_set = ImitiSet.objects.get(code_med=code_med)
            umuti_set_seria = ImitiSetSeriazer(umuti_set)
        except ImitiSet.DoesNotExist:
            return JsonResponse({
                'response': 404,
            })
        else:
            if data_sent.get('request') == 'get':
                if umuti_set_seria.is_valid:
                    return Response(umuti_set_seria.data)
            elif data_sent.get('request') == 'post':
                former_interest = 1
                umuti_set.is_pr_interest = bool(data_sent.get('is_pr_interest'))
                cond_1 = float(data_sent.get('pr_interest'))
                current_value = umuti_set.pr_interest
                new_value = cond_1
                cond_2 = bool(data_sent.get('is_pr_interest'))
                
                if cond_1:
                    umuti_set.pr_interest = float(data_sent.get('pr_interest'))
                if cond_2:
                    former_interest = self._updatePrixVenteEntree(code_med=code_med, \
                                            pr_interest=umuti_set.pr_interest, \
                                            is_individual=True)
                if cond_1 and cond_2:
                    umuti_set.prix_vente = self.__updatePvSet(val=umuti_set.prix_vente, \
                                                    former_interest=former_interest, \
                                                    new_interest=umuti_set.pr_interest)
                umuti_set.save()
        if umuti_set.is_pr_interest:
            recordOperation(who_did_id=request.user,\
                        what_operation=f"Intérêt individuel ({umuti_set.code_med} - {umuti_set.nom_med[:10]})",\
                        from_value=current_value,\
                        to_value=new_value)
        else:
            print(f"The default ben: {default_pr_interest}")
            recordOperation(who_did_id=request.user,\
                        what_operation="Intérêt individuel",\
                        from_value=umuti_set.pr_interest,\
                        to_value=default_pr_interest)
        return JsonResponse({
            'response': 1
        })
    def _updatePrixVenteEntree(self, code_med,pr_interest:float=1, is_individual:bool=False):
        actual_interest = 1
        former_interest = 1
        if is_individual:
            actual_interest = pr_interest
        else:
            actual_interest = BeneficeProgram.objects.first().ben
            former_interest = actual_interest
        imiti_entree = UmutiEntree.objects.filter(Q(code_med=code_med) & \
                                                  Q(quantite_restant__gte=1))

        imiti_entree_backup = UmutiEntree.objects.filter(Q(code_med=code_med) & \
                                                  Q(quantite_restant__gte=1))
        
        for umuti in imiti_entree:
            umuti.prix_vente = roundNumber(umuti.prix_achat * float(actual_interest))
            umuti.save()
        for umuti in imiti_entree_backup:
            umuti.prix_vente = roundNumber(umuti.prix_achat * float(actual_interest))
            umuti.save()
        
        return former_interest
    
    def __updatePvSet(self, val:int=1, former_interest:float=1, new_interest:float=1)->int:
        prix_achat = val / former_interest
        prix_vente = prix_achat * new_interest
        return prix_vente
    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def changePasswd(self, request):
        """Update the password of the connected User"""
        data_sent = request.data.get('imiti')
        pwd1 = data_sent.get('pwd1')
        pwd2 = data_sent.get('pwd2')

        c1_1 = len(str(pwd1)) > 7
        c1_2 = len(str(pwd2)) > 7
        c1_3 = c1_1 == c1_2
        all_conditions_match = c1_1 and c1_2 and c1_3
        if not all_conditions_match:
            return JsonResponse({
                'response': 403
            })
        
        user = request.user
        user_obj = User.objects.get(username=user)
        print(f"The user is : {user}, found: {user_obj.username}")
        user_obj.set_password(pwd1)
        user_obj.save()
        return JsonResponse({
            'response': 200
        })
    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAdminUser])
    def setPachatEntree(self, request):
        """
        Will get the id for umutiSet and return or 
        update its pr_interest.
        """
        data_sent = request.data.get('imiti')
        print(f"The data sent: {data_sent}")
        former_state = None
        if not data_sent:
            return JsonResponse({
            'response': 0
        })
        code_med = data_sent.get('code_med')
        if data_sent.get('request') == 'get':
            imiti_entree = UmutiEntree.objects.filter(Q(code_med=code_med) & \
                                                    Q(quantite_restant__gte=1))
            if not imiti_entree:
                return JsonResponse({
                    'response': 404,
                })
            imiti_serialized = UmutiEntreeSeriazer(imiti_entree, many=True)
            if imiti_serialized.is_valid:
                return Response(imiti_serialized.data)
        elif data_sent.get('request') == 'post':
            # former_interest = 1
            journal = None
            update_status = [0]
            code_operation = data_sent.get('code_operation')
            current_value = 0
            if code_operation:
                update_status = self._updateAchatEntree(\
                    code_med=code_med, \
                    code_operation=code_operation, \
                    data=data_sent)
            print(f"The code operation: {code_operation}")
            if update_status[0] == 200:
                self._update_code_for_sync(code_med=code_med)
                recordOperation(who_did_id=request.user,\
                    what_operation=f"Modifier Achat ({update_status[1]['code_med']}-{update_status[1]['nom_med'][:15]})",\
                    from_value=f"qte:{update_status[1]['qte']}, pxA:{update_status[1]['pxA']} , per:{update_status[1]['per']}",\
                    to_value=f"qte:{data_sent['quantite_initial']}, pxA:{data_sent['prix_achat']} , per:{data_sent['date_peremption']}") 
                return JsonResponse({
                    'response': 200
                })
            else:
                return JsonResponse({'response': 404})
           
        return JsonResponse({
            'response': 1
        })
    
    def _update_code_for_sync(self, code_med:str='')->int:
        journal = Journaling.objects.first()
        codes_for_sync = list(StringToList(journal.codes_for_sync).toList())
        if not(code_med in codes_for_sync): 
            codes_for_sync.append(code_med)
            journal.codes_for_sync = codes_for_sync
            journal.save()
        return 0

    
    def _updateAchatEntree(self, code_med, code_operation, data)->int:
        consumed = 0
        new_qte = 0
        adding = 0
        current_data = {}
        try:
            umuti = UmutiEntree.objects.get(\
                Q(code_med=code_med) & \
                Q(code_operation=code_operation))
            umuti_ = UmutiEntreeBackup.objects.get(\
                Q(code_med=code_med) & \
                Q(code_operation=code_operation))
        except UmutiEntree.DoesNotExist:
            return 404
        new_qte = int(data.get('quantite_initial'))
        diff = 0
        case = 0
        if new_qte >= umuti.quantite_initial:
            diff = new_qte - umuti.quantite_initial
            case = 1
        else:
            diff = umuti.quantite_initial - new_qte
            case = 2
        current_data['qte'] = umuti.quantite_initial
        current_data['per'] = umuti.date_peremption
        current_data['pxA'] = umuti.prix_achat
        current_data['code_med'] = umuti.code_med
        current_data['nom_med'] = umuti.nom_med
        if (case == 1):
            umuti.quantite_initial = new_qte
            umuti.quantite_restant += diff
        elif (case == 2) and (umuti.quantite_restant >= diff):
            umuti.quantite_initial = new_qte
            umuti.quantite_restant -= diff
        else:
            return 403
        umuti_.quantite_initial = umuti.quantite_initial
        umuti_.quantite_restant = umuti.quantite_restant

        umuti.prix_achat = int(data.get('prix_achat'))
        umuti_.prix_achat = umuti.prix_achat
        umuti.date_peremption = data.get('date_peremption')
        umuti_.date_peremption = umuti.date_peremption
        umuti.save()
        umuti_.save()
        return [200, current_data]

    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def doublon_management(self, request):
        """
        Will attribute a new code_operation of 4letters for
        the one having same date entrant and code_med.
        """
        fixed = 0
        code_generator8 = GenerateCode(8)
        new_code_operation = code_generator8.giveCode()
        codes = []
        codes.append(new_code_operation)
        counter = 0

        meds = UmutiEntree.objects.all()
        # meds = UmutiEntree.objects.filter(code_med='963326')
        code_med_list = {x.code_med:[] for x in meds}

        
        for med in meds:
            if med.code_operation in code_med_list[med.code_med]:
                med.code_operation = codes[counter]
                while med.code_operation in code_med_list[med.code_med]:
                    try:
                        actual_code = codes[counter + 1]
                    except IndexError:
                        # generate a new code
                        code_generator8 = GenerateCode(8)
                        new_code_operation = code_generator8.giveCode()
                        codes.append(new_code_operation)
                        med.code_operation = codes[counter + 1]
                        break
                    else:
                        actual_code = codes[counter + 1]
                        if actual_code in code_med_list[med.code_med]:
                            pass
                        else:
                            med.code_operation = actual_code
                    counter += 1
                counter = 0 
                code_med_list[med.code_med].append(med.code_operation)
                med.save()
                fixed += 1
            else:
                code_med_list[med.code_med].append(med.code_operation)

        return JsonResponse({
            "corrected": [code_med_list, fixed]
        })
    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def doublon_management_today(self, request):
        """
        Will attribute a new code_operation of 4letters for
        the one having same date entrant and code_med.
        """
        today = timezone.now()
        today -= timedelta(hours=today.hour)
        meds = UmutiEntree.objects.filter(date_entrant__gte=today)

        if not meds:
            return JsonResponse({
                "corrected": 0
            })
        
        fixed = 0
        code_generator8 = GenerateCode(8)
        new_code_operation = code_generator8.giveCode()
        codes = []
        codes.append(new_code_operation)
        counter = 0

        code_med_list = {x.code_med:[] for x in meds}

        
        for med in meds:
            if med.code_operation in code_med_list[med.code_med]:
                med.code_operation = codes[counter]
                while med.code_operation in code_med_list[med.code_med]:
                    try:
                        actual_code = codes[counter + 1]
                    except IndexError:
                        # generate a new code
                        code_generator8 = GenerateCode(8)
                        new_code_operation = code_generator8.giveCode()
                        codes.append(new_code_operation)
                        med.code_operation = codes[counter + 1]
                        break
                    else:
                        actual_code = codes[counter + 1]
                        if actual_code in code_med_list[med.code_med]:
                            pass
                        else:
                            med.code_operation = actual_code
                    counter += 1
                counter = 0 
                code_med_list[med.code_med].append(med.code_operation)
                med.save()
                fixed += 1
            else:
                code_med_list[med.code_med].append(med.code_operation)

        return JsonResponse({
            "corrected": [code_med_list, fixed]
        })
    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def fix_doublon_bckup(self, request):
        counter = 0

        meds2 = UmutiEntreeBackup.objects.all()

        for med in meds2:
            per = med.date_peremption
            qte = med.quantite_initial
            med1 = UmutiEntree.objects.filter(\
                Q(date_peremption=per) &\
                Q(code_med=med.code_med) &\
                Q(quantite_initial=qte))
            
            if med1:
                med.code_operation = med1[0].code_operation
                med.save()
                counter += 1
        return Response({
            'response': counter == len(meds2)
        })
    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def fix_doublon_bckup_today(self, request):

        today = timezone.now()
        today -= timedelta(hours=today.hour)
        counter = 0

        meds2 = UmutiEntreeBackup.objects.filter(date_entrant__gte=today)

        for med in meds2:
            per = med.date_peremption
            qte = med.quantite_initial
            med1 = UmutiEntree.objects.filter(\
                Q(date_peremption=per) &\
                Q(code_med=med.code_med) &\
                Q(quantite_initial=qte))
            
            if med1:
                med.code_operation = med1[0].code_operation
                med.save()
                counter += 1
        return Response({
            'response': counter == len(meds2)
        })

    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def repair_bon_with_zero(self, request):
        """We be based on the fied meds of each bon,
        and build from umutisold instances.
        """
        bons = BonDeCommand.objects.filter(total=0)
        bons_seria = BonDeCommandSeria(bons, many=True)
        for bon in bons:
            code_operations = str(bon.meds).split(';')[:-1]
            total = 0
            for code_operation in code_operations:
                try:
                    umuti_sold = UmutiSold.objects.get(code_operation=code_operation)
                except UmutiSold.DoesNotExist:
                    pass
                else:
                    qte = umuti_sold.quantity
                    prix_vente = umuti_sold.prix_vente
                    total += (qte * prix_vente)
            bon.total = total
            bon.cout = total - (total * bon.assu_rate)
            bon.save()
        if bons_seria.is_valid:
            return Response(bons_seria.data)
        return Response({
                "corrected": 0
            })
    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def date_per_to_31(self, request):
        """
        convert date_peremption to the last day of the month.
        """
        days = [ 28, 31,28,31,30,31,30,31,31,30,31,30,31 ]
        meds = UmutiEntree.objects.all()
        meds2 = UmutiEntreeBackup.objects.all()

        for (med, med2) in zip (meds, meds2):
            actual_date = med.date_peremption
            actual_date2 = med2.date_peremption
            new_date = timezone.datetime(actual_date.year, \
                            actual_date.month, days[actual_date.month])
            new_date2 = timezone.datetime(actual_date2.year, \
                            actual_date2.month, days[actual_date2.month])
            med.date_peremption = new_date
            med2.date_peremption = new_date2
            med.save()
            med2.save()
        return Response({
            'response': 1
        })
    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def today_per_to_31(self, request):
        """
        convert the inputs entered today to have date_peremption to the last day of the month.
        """
        today = timezone.localdate()
        days = [ 28, 31,28,31,30,31,30,31,31,30,31,30,31 ]

        meds = UmutiEntree.objects.filter(date_entrant__gte=today)
        meds2 = UmutiEntreeBackup.objects.filter(date_entrant__gte=today)

        for (med, med2) in zip (meds, meds2):
            actual_date = med.date_peremption
            actual_date2 = med2.date_peremption
            new_date = timezone.datetime(actual_date.year, \
                            actual_date.month, days[actual_date.month])
            new_date2 = timezone.datetime(actual_date2.year, \
                            actual_date2.month, days[actual_date2.month])
            med.date_peremption = new_date
            med2.date_peremption = new_date2
            med.save()
            med2.save()
        return Response({
            'response': 1
        })
    
    

    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def collection_len(self, request):
        """
        gives the length of the collection.
        """
        meds_len = ImitiSet.objects.all().count()
        return Response({
            'response': meds_len
        })
    
    @action(methods=['get', 'post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def request_collection(self, request):
        """
        gives the length of the collection.
        """
        token = request.data.get('imiti', 'done')
        # token = token[1:]
        # token = token[:-1]
        if len(token) <= 2:
            return JsonResponse({
                'response': 500,
                'counter': 0
            }, status=500)
        data_to_send = []

        meds = ImitiSet.objects.all()
    
        for med in meds:
            obj = {}
            obj['nom_med'] = med.nom_med
            obj['qte'] = med.quantite_restant
            obj['price'] = med.prix_vente
            lote = StringToList(med.lot).toList()
            lote = self._pack_dates(lote)[:3]
            obj['lot'] = lote
            data_to_send.append(obj)
        
        meds_len = len(data_to_send)

        # forcing garbage collection
        meds = None
        obj = None

        ip = "http://127.0.0.1:8008/"
        # ip = "https://5hmc28-8008.csb.app/"  #CodeSandbox
        endpoint = "api/in/updateCollection/"
        url = ip + endpoint
        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwMDcwNTIxLCJpYXQiOjE3NTAwNjMzMjEsImp0aSI6ImU0NDNmNjg0ZTkxMzQ3ZmU4ZDAyNmNkYTg3ZmEwYjgyIiwidXNlcl9pZCI6MX0.8ycBqdyvnGZruNf1-tMsRLVVK8aFGBATXgWji0p0444"
        Authorization = "Bearer " + token
        headers = {
            'Authorization' :  Authorization
        }

        size = 20
        paginated = Paginator(data_to_send, size)
        begin = 1
        page = 1
        failure = 0
        
        # ask the sync_code
        url_sync_code = "api/in/request_code_sync/"
        sync_code = 0
        ask_code = requests.post(ip+url_sync_code, json={}, headers=headers)
        if ask_code.status_code == 200:
            response = ask_code.json()
            sync_code = response.get('response', 0)
        sync_code = self._give_code(num=sync_code)
        
        while (meds_len / begin) >= 1 and failure < 10:
            paged = paginated.get_page(page)
            paged_serialized = CollectionSeria(paged, many=True)

            try:
                response = requests.post(url, json={'data': paged_serialized.data, 'sync_code':sync_code}, headers=headers)
            except requests.RequestException as e:
                failure += 1
                continue

            if response.status_code == 200:
                page += 1
                begin += size
            else:
                failure += 1
                begin = 1
                page = 1  # restart if failed
        # request to clean the outdated.
        url_clean_outdated = "api/in/clean_outdated/"
        # sync_code = 0
        ask_code = requests.post(ip+url_clean_outdated, \
                        json={'sync_code':sync_code}, \
                        headers=headers)
        return Response({
            'response': 1,
            'counter': 0
        })
    
    def _give_code(self, num)->int:
        codes = [1, 2, 3, 4, 5]
        if (num > 4) or (num < 0):
            num = 0
        return codes[num]
    
    def _pack_dates(self, dates)->list:
        date_list = []
        for date in dates:
            tmp = date['date']
            formatted = self.__format_date(tmp)
            date_list.append(formatted)
        return date_list
    
    def __format_date(self, date:str)->str:
        tmp = str(date).split('-')
        formatted_str = tmp[1] + "-" + tmp[0]
        return formatted_str

class GeneralOps2(viewsets.ViewSet):
    """
    An extension of GeneralOps.
    """
    @action(methods=['get', 'post'], detail=False,\
             permission_classes= [IsAdminUser])
    def request_infos(self, request):
        info = Info.objects.first()
        info_s = InfoSeria(info)
    
        if info_s.is_valid:
            return Response({
                'response': info_s.data
            })
        return Response({
            'response': 1
        }) 
    
    @action(methods=['get', 'post'], detail=False,\
             permission_classes= [IsAdminUser])
    def update_infos(self, request):
        infos = request.data.get('imiti')
        print(f"The infos received: {infos}")
        update_info = self._make_update_info(infos=infos)
        if update_info == 200:
            print("Successfully updated infos.")
            return Response({
                'response': 200
            })
        return Response({
            'response': 1
        })
    
    def _make_update_info(self, infos)->int:
        info_update = Info.objects.last()
        name_pharma = infos.get("name_pharma", '')[:34]
        code_pharma = infos.get("code_pharma", '1000')
        
        remote_password = infos.get("remote_password", 'j')

        if len(remote_password) >= 8 and len(name_pharma) >= 5:
            info_update.name_pharma = name_pharma
            info_update.code_pharma = code_pharma
            info_update.tel = int(infos.get('tel',0))
            info_update.loc_street = infos.get("loc_street", '')[:14]
            info_update.loc_quarter = infos.get("loc_quarter", '')[:14]
            info_update.loc_commune = infos.get("loc_commune", '')[:14]
            info_update.loc_Province = infos.get("loc_Province", '')[:14]
            info_update.remote_username = name_pharma
            info_update.remote_password = remote_password

            info_update.save()

        return 200
    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def set_last_prix_vente(self, request):
        """
        Will get the id for umutiSet and return or 
        update its decimal field.
        """
        data_sent = request.data.get('imiti')
        print(f"The data sent: {data_sent}")
        if not data_sent:
            return JsonResponse({
            'response': 0
        })
        code_med = data_sent.get('code_med')
        try:
            umuti_set = ImitiSet.objects.get(code_med=code_med)
            umuti_set_seria = ImitiSetSeriazer(umuti_set)
        except ImitiSet.DoesNotExist:
            return JsonResponse({
                'response': 404,
            })
        else:
            if data_sent.get('request') == 'get':
                if umuti_set_seria.is_valid:
                    return Response(umuti_set_seria.data)
            elif data_sent.get('request') == 'post':
                umuti_set.last_prix_vente = bool(data_sent.get('last_prix_vente'))
                umuti_set.save()
                recordOperation(who_did_id=request.user, \
                        what_operation=f"Consideré le dernier prix sur {(umuti_set.nom_med)[:15]}", \
                        from_value=(not umuti_set.last_prix_vente), \
                        to_value=umuti_set.last_prix_vente)
                GeneralOps._update_code_for_sync(self=GeneralOps, code_med=umuti_set.code_med)
        return JsonResponse({
            'response': 1
        })
                
            

                

class EntrantImiti(viewsets.ViewSet):
    """Manages all the Entrant Operations"""

    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def kurangura(self, request):
        """Kwinjiza umuti nkukwo uwuranguye"""
        dataReceived = request.data
        data = dataReceived.get('imiti')
        print(f"The data Received: {dataReceived.get('imiti')}")
        # return JsonResponse({"detail":"NoneType"})
        if not data:
            return JsonResponse({"detail":"NoneType"})
        # first of all, generate the codes
        code_12 = GenerateCode()
        code_operation = code_12.giveCode()
        error_list = []
        i = 0
        single = False
        pr_interest = BeneficeProgram.objects.first().ben
        journal = Journaling.objects.first()
        codes_for_sync = list(StringToList(journal.codes_for_sync).toList())
        for obj in data:
            # if (len(data) > 2) and (i == 0): # no title is sent
            #     i += 1 #to skip the title string
            #     continue
            if (len(data) == 1):
                single = True
            
            code_6 = GenerateCode(6)
            code_med = code_6.giveCode()
            # print(f"using code: {code_med}")
            # We should check the existence of umuti with that code or nom_med
            check_exist = self._doesExist(obj=obj)
            if check_exist:
                code_med = check_exist # in case there is a match.
            reponse = self._addUmuti(obj=obj,code_med=code_med,\
                                      code_operation=code_operation, \
                                        single=single, operator=request.user.username,
                                        pr_interest=pr_interest) # 200 if ok
            if reponse != 200:
                error_list.append(i)
            codes_for_sync =  self._add_for_sync(codes_for_sync=codes_for_sync, code_med=code_med)
        
        if len(error_list):
            return JsonResponse({"detail": error_list})
        journal.codes_for_sync = codes_for_sync
        journal.save()

        return JsonResponse({"detail":"ok"}, status=200)
    
    def _add_for_sync(self, codes_for_sync, code_med:str='')->int:
        if not(code_med in codes_for_sync): 
            codes_for_sync.append(code_med)
        return codes_for_sync
    
    def _doesExist(self, obj:dict):
        """This method checks if the umuti already exist with the same
        nom_med in order to share the code_med.
        In case there is a match of nom_med or obj.code_med,
        then return that code_med."""
        nom_med = obj.get('nom_med')
        code_med = obj.get('code_med')
        # try:
        #     umuti_exist = UmutiEntree.objects.get(nom_med=nom_med)
        # except UmutiEntree.DoesNotExist:
        #     return None
        # else:
        #     return umuti_exist.code_med
        umuti_exist = UmutiEntree.objects.filter(nom_med__iexact=nom_med)
        if umuti_exist:
            return umuti_exist[0].code_med
        else:
            return None
    
    def _addUmuti(self, obj:dict, code_med:str, code_operation:str,\
                   single:bool, operator:str, pr_interest:float=1.0):
        """THis method is in charge of creating and filling a new instance
        of UmutiEntree, of this type: 

        obj = {'code_med': '', 'date_entrant': '2024-06-08T09:01:18.785Z', 
               'date_peremption': '12:00:00 AM', 'nom_med': 'AMINOPHYLLINE', 
               'description_med': 'Uvura uburuhe', 'famille_med': 'Ovule', 
               'type_achat': 'Carton', 'ratio': '10', 'type_vente': 'Piece', 
               'prix_vente': '1500', 'prix_vente': '1800', 
               'quantite_initial': '15', 'location': ''}
        """
        # print(f"THe operator is : {operator}")
        umuti_new = UmutiEntree.objects.create()
        umuti_new.nom_med = obj.get('nom_med')
        umuti_new.code_med = code_med
        umuti_new.code_operation = code_operation
        umuti_new.quantite_initial = int(obj.get('quantite_initial'))
        umuti_new.quantite_restant = umuti_new.quantite_initial
        # usd_to_bif = UsdToBif.objects.first()
        umuti_new.prix_achat = int(obj.get('prix_achat'))
        prix_vente = umuti_new.prix_achat * pr_interest
        umuti_new.prix_vente = roundNumber(prix_vente)
        # umuti_new.prix_achat_usd = umuti_new.prix_achat / usd_to_bif.actualExchangeRate
        # umuti_new.prix_vente_usd = umuti_new.prix_vente / usd_to_bif.actualExchangeRate
        if not single:
            umuti_new.date_peremption = self._giveDate_exp(obj.get('date_peremption'))
            # umuti_new.date_entrant = self._giveDate_entree(obj.get('date_entrant'))
        else:
            umuti_new.date_peremption = obj.get('date_peremption')
            # umuti_new.date_entrant = obj.get('date_entrant')
        # umuti_new.description_umuti = (obj.get('description_med'))
        umuti_new.date_entrant = datetime.now()
        umuti_new.classe_med = obj.get('classe_med') 
        umuti_new.sous_classe_med = obj.get('sous_classe_med') 
        umuti_new.forme = obj.get('forme')
        # if obj.get('ratio'):
        #     umuti_new.ratio = obj.get('ratio')
        # umuti_new.type_vente = obj.get('type_vente')
        # umuti_new.location = obj.get('location')
        umuti_new.operator = operator

        umuti_new.save()

        # print("THe new saved Med: ", umuti_new.nom_med)

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
        # umuti_backup.type_med = instance.type_med
        # umuti_backup.type_achat = instance.type_achat
        # umuti_backup.ratio = instance.ratio
        # umuti_backup.type_vente = instance.type_vente
        # umuti_backup.location = instance.location
        umuti_backup.classe_med = instance.classe_med
        umuti_backup.sous_classe_med = instance.sous_classe_med
        umuti_backup.forme = instance.forme
        umuti_backup.operator = instance.operator
        umuti_backup.save()

        return 200
    
    def _giveDate_exp(self, date_peremption:str)->str:
        """ This function checks the expiring date sent in the format:
            "04/01/27" and return datetime.datetime(2027, 4, 1, 0, 0)
        """
        result = timezone.now()
        if date_peremption:
            try:
                return datetime.strptime(date_peremption, "%m/%d/%y")
            except ValueError:
                print(f"THE WRONG DATE FORMAT as: {date_peremption}")
                return result
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
        previous_sync_code = ImitiSet.objects.first().sync_code
        sync_code = give_sync_code(previous_sync_code)
        journal = Journaling.objects.first()
        codes_for_sync = journal.codes_for_sync
        codes_for_sync = StringToList(codes_for_sync).toList()
        procured = []
        if len(codes_for_sync):
            print(f"will compile : {len(codes_for_sync)} existing")
            procured = UmutiEntree.objects.filter(code_med__in=codes_for_sync).order_by('date_peremption')
            sync_code = 8 # assuring to re-write the lot
        else:
            print(f"will compile : {len(codes_for_sync)} existing")
            # procured = UmutiEntree.objects.filter(quantite_restant__gte=1).order_by('date_peremption')
            procured = UmutiEntree.objects.filter(quantite_restant__gte=1).order_by('date_entrant')
        print(f"GOtten len: {len(procured)}")
        pr_interest = BeneficeProgram.objects.first()
        for umutie in procured:
            code = umutie.code_med
            try:
                umuti_set = ImitiSet.objects.get(code_med=code)
            except ImitiSet.DoesNotExist:
                #when the code is new in the ImitiSet
                #we create that entry in the ImitiSet
                umuti_new = self._umutiMushasha(umutie)
            else:
                if sync_code != umuti_set.sync_code:
                    umuti_set.lot = str(init_lot(umuti=umutie))
                    umuti_set.sync_code = sync_code
                qte_saved =  StringToList(umuti_set.checked_qte)
                qte_tracked = dict(qte_saved.toList())
                current_operation = {
                    umutie.code_operation: umutie.quantite_restant
                }
                qte_tracked.update(current_operation)
                somme_lot = sum(qte_tracked.values())
                
                synced_lot = self._check_lot(umuti_set.lot, umutie)

                
                umuti_set.prix_achat = umutie.prix_achat
                prix_vente = 0

                if umuti_set.is_pr_interest:
                    prix_vente = umuti_set.prix_achat * umuti_set.pr_interest
                else:
                    prix_vente = umuti_set.prix_achat * pr_interest.ben 
                if (prix_vente > umuti_set.prix_vente) and \
                    (umuti_set.last_prix_vente == False):
                    umuti_set.prix_vente = roundNumber(prix_vente)
                elif (prix_vente <= umuti_set.prix_vente) and \
                    (umuti_set.last_prix_vente == False):
                    umuti_set.prix_vente = umuti_set.prix_vente
                else:
                    umuti_set.prix_vente = umutie.prix_vente

                umuti_set.quantite_restant = round(somme_lot, 1)
                umuti_set.lot = synced_lot
                umuti_set.checked_qte = qte_tracked

                last_date = self._findLastDate(code_med=umuti_set.code_med)
                if last_date:
                    umuti_set.date_last_vente = last_date
                #checking if there is qte_entrant bigger than before
                if (int(umuti_set.qte_entrant_big)) < (int(umutie.quantite_initial)):
                    umuti_set.qte_entrant_big = int(umutie.quantite_initial)
                umuti_set.save()
        journal.codes_for_sync = []
        journal.save()
        print("compileImitiSet: SYNC done.")
        return JsonResponse({"detail":"ok"}, status=200)
    
    
    
    def _round100(self, data:int)->int:
        """Rounding number according to 100.
        expecting data = 7215 and return 7300"""
        d = int(data / 100) + 1
        result = d * 100
        return result
    
    def _sync_lot(self, lot:str, umutie):
        lot_string = StringToList(lot)
        #the string of list must be made into json
        # print(f"The lot: {lot}")
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
        """Has to take this if this umutie is new."""
        lot_string = StringToList(lot)
        #the string of list must be made into json
        lot_list = lot_string.toList()
        code_operation = umutie.code_operation
        i = 0
        j = 0
        once = 0
        zero_qte = []
        is_zero = False
        counter = 0
        for lote in lot_list:
            add_ope = False
            updated = False
            if is_zero:
                del lot_list[counter - 1]
            if lote['qte'] == 0:
                is_zero = True
            if lote.get('date') == (str(umutie.date_peremption))[:7]:
                codes_operation = lote.get('code_operation')
                for ope in codes_operation:
                    cp_ope = dict(ope)
                    code_ope_str = cp_ope.popitem()[0]
                    if code_ope_str == umutie.code_operation:
                        # should update
                        ope[code_operation] = umutie.quantite_restant
                        updated = True
                        
                    else:
                        # should add new
                        add_ope = True
                        continue
                once += 1
                if updated:
                    lote['qte'] = (listDictIntSomme2(lote['code_operation']))
                if add_ope:
                    obj = { 
                                str(umutie.code_operation) : umutie.quantite_restant
                            }
                    lote['code_operation'].append(obj)
                    lote['qte'] = int(listDictIntSomme2(lote['code_operation']))
                    j += 1
                    once +=1
            counter += 1
            
        if (not j) and (not once):
            obj = {
                'date': (str(umutie.date_peremption))[:7],
                'qte': (umutie.quantite_restant), # was int.
                'code_operation': [
                        { 
                            str(umutie.code_operation) : umutie.quantite_restant
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
        umuti_new.nom_med = str(umuti.nom_med)[:65]
        umuti_new.classe_med = (str(umuti.classe_med))[:65]
        umuti_new.sous_classe_med = \
            (str(umuti.sous_classe_med))[:65]
        umuti_new.forme = (str(umuti.forme))[:7]
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
        
        umuti_new.quantite_restant = umuti.quantite_restant
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
        # qte_obj= {
        #     'code_operation': umuti.code_operation,
        #     'qte_restant': umuti_new.quantite_restant
        # }
        operations_checked = {
            umuti.code_operation: umuti_new.quantite_restant
        }
        checked_qte = []
        # checked_qte.append(qte_obj)
        checked.append(umuti.code_operation)
        umuti_new.checked_imiti = checked
        umuti_new.checked_qte = operations_checked
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
        page = 0
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
            syntesis['qte'] += umuti.quantite_restant
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
        """
        Handles the sell operation
        """
        data_query = request.data
        print(f"The data sent is: {data_query}")
        bundle = data_query.get('imiti')
        panier = bundle.get('panier')
        client = bundle.get('client')
        case = 0

        # create client instance for case 3.
        # otherwise, 1&2, link the existing instance 
        client_obj = None
        assu_obj = None
        bon_de_commande = None
        categorie = ''
        rate_assure = 0
        bon_created = False
        existing_bon = False
        success = 0
        client_name = ''
        created_facture_number = 0
        elapsed_month = timezone.now().month
        today_number = timezone.now().day
        year_start = timezone.now() - timedelta(\
            days=((30*elapsed_month)+today_number))
        
        if not client:
            # Client ordinaire, categorie: 'no'
            case = 1
            client_obj, assu_obj = self._getClient1()
            categorie = 'no'
        elif not client.get('nom_adherant'):
            # Client special, categorie: tv, mt, md
            case = 2
            client_obj, assu_obj = self._getClient2(client)
            categorie = client.get('categorie')
        else:
            # Assure: categorie: au
            case = 3
            client_obj, assu_obj= self._getClient3(client)
            categorie = client.get('categorie')
        total_facture = 0
        if case ==3:
            num_bon = client.get("numero_bon")
            existing_bon = self._checkNumBon(num_bon)
        if existing_bon:
            return JsonResponse({"sold":"FailedBecauseAlreadyExist"})
        rate_assure = assu_obj.rate_assure
        
        # Take the client_name 
        try:
            client_name = client_obj.beneficiaire
        except AttributeError:
            client_name = '' # should call him 'Visiteur'
        
        journal = Journaling.objects.first()
        codes_for_sync = list(StringToList(journal.codes_for_sync).toList())
        
        for actual in panier:
            code_med = actual.get('code_med')
            lot = actual.get('lot')
            qte = actual.get('qte')
            if not lot:
                continue
            # for lote in lot:
            #     code_operation = lote.get('code_operation')
            #     qte = lote.get('qte')
            #     print(f"Things to assess: {code_med}, {code_operation}, {qte}")
                # orders = self._assess_order(code_med=code_med,\
                #                          code_operation=code_operation,\
                #                              qte=qte)

                # should indent the all below to take
                # the frontend in consideration.
            orders = self._place_order(code_med=code_med, qte=qte)
            if not orders:
                return Response({
                    "imperfect": 1,
                    "suceeded": success,
                    "num_facture": created_facture_number,
                    "client_name": client_name,
                })
            counter = 0
            for order in orders:
                print(f"Counted: {counter}")
                counter += 1
                if order[2] == 0:
                    continue
                umuti = UmutiEntree.objects.\
                    filter(code_med=code_med).\
                    filter(code_operation=order[1])
                #can now perfom the Vente operation
                
                if (not umuti) and (success):
                    bon_de_commande = self._updateReduction(bon_de_commande, \
                                total=total_facture, rate_assure=rate_assure, \
                                num_facture=created_facture_number)
                    return Response({
                        "imperfect": 1,
                        "suceeded": success,
                        "num_facture": created_facture_number,
                        "client_name": client_name,
                    })
                elif (not umuti) and (not success):
                    return Response({
                        "imperfect": 1,
                        "suceeded": success,
                        "num_facture": created_facture_number,
                        "client_name": client_name,
                    })
                    
                if umuti[0].quantite_restant < float(order[2]):
                    return Response({
                        "imperfect": 1,
                        "suceeded": success,
                        "num_facture": created_facture_number,
                    })
                if (float(qte)) and (not bon_created):
                    bon_de_commande = self._createBon(\
                        client=client, \
                        client_obj=client_obj,\
                        assu_obj=assu_obj,\
                        categorie=categorie)
                    bon_created = True
                    created_facture_number = len(BonDeCommand.objects.filter(\
                                                date_served__gte=year_start))
                    if bon_de_commande == 403:
                        return Response({
                            "imperfect": 1,
                            "suceeded": success,
                            "num_facture": created_facture_number,
                            "client_name": client_name,
                        })
                        # in case "The Assurance does ":"not exist"
                    

                be_sold = ImitiSet.objects.get(code_med=umuti[0].code_med)
                
                # Only create a bon_de_commande when this is True
                # print(f"and qte before creating Bon: {qte}")
                
                sold = self._imitiSell(umuti=umuti[0], qte=order[2], \
                            operator=request.user, \
                                reference_umuti=be_sold,\
                                bon_de_commande=bon_de_commande)
                # completing bon_de_commande
                bon_de_commande = self._completeBon(\
                    bon_de_commande=bon_de_commande,\
                    code_operation=sold)
                if sold:
                    total_facture += be_sold.prix_vente * order[2]
                codes_for_sync =  self._add_for_sync(codes_for_sync=codes_for_sync, code_med=code_med)
                journal.codes_for_sync = codes_for_sync
                journal.save()
            success += 1
        # Should now update the reduction in bon_de_commande
        bon_de_commande = self._updateReduction(bon_de_commande, \
                total=total_facture, rate_assure=rate_assure, \
                num_facture=created_facture_number)

        return JsonResponse({"sold": [created_facture_number, client_name]})
    
    def _add_for_sync(self, codes_for_sync, code_med:str='')->int:
        if not(code_med in codes_for_sync): 
            codes_for_sync.append(code_med)
        return codes_for_sync

    def _checkNumBon(self, num_bon:str='')->bool:
        bon = BonDeCommand.objects.filter(num_bon=num_bon)
        if bon:
            return True
        else:
            return False
    
    def _getClient3(self, dataClient)->list:
        """Returns a instance created or existed client with the rate_assure."""
        relation = dataClient.get('relation')
        beneficiaire = dataClient.get('nom_client')
        if relation == 'Lui-même':
            beneficiaire = dataClient.get('nom_adherant')
        rate_assure = int(dataClient.get('rate_assure'))
        assureur = dataClient.get('assureur')
        assurance = None
        # Check to create assurance
        try:
            assurance = Assurance.objects.get(name=assureur)
        except Assurance.DoesNotExist:
            assurance = Assurance.objects.create(name=assureur)
            assurance.rate_assure = rate_assure
            assurance.save()
        else:
            assurance.rate_assure = rate_assure
            assurance.save()
        
        # Check or create client
        try:
            client = Client.objects.get(beneficiaire=beneficiaire)
        except Client.DoesNotExist:
            # create that client
            client = Client.objects.create(beneficiaire=beneficiaire)
            client.employeur = dataClient.get('employeur')
            client.joined_on = timezone.now()
            client.nom_adherant = dataClient.get('nom_adherant')
            client.numero_carte = dataClient.get('numero_carte')
            client.relation = dataClient.get('relation')
            client.save()
            return [client, assurance]
        else:
            return [client, assurance]

    def _getClient2(self, dataClient)->list:
        """
        Will return the only instance for special client
        """
        client = None 
        beneficiaire = str(dataClient.get('nom_client'))[:24]
        # rate_assure = int(dataClient.get('rate_assure'))
        numero_tel = dataClient.get('numero_tel')
        # assureur = dataClient.get('assureur')

        # query = Client.objects.filter(beneficiaire='Special')
        assurance = Assurance.objects.get(name = "Pharmacie Ubuzima")
        try:
            client = Client.objects.get(phone_number=numero_tel)
        except Client.DoesNotExist:
            # create that client
            client = Client.objects.create(beneficiaire=beneficiaire)
            client.joined_on = timezone.now()
            client.nom_adherant = beneficiaire
            client.phone_number = numero_tel
            client.save()
            return [client, assurance]
        else:
            return [client, assurance]

        return 0
        if query:
            return [query[0], assurance]
        return [None, assurance]
    
    def _getClient1(self)->list:
        """
        Will return the instance for ordinary Client
        """
        assurance = Assurance.objects.get(name='Sans')
        query = Client.objects.filter(beneficiaire='Ordinary')
        if query:
            return [query[0], assurance]
        return [None, assurance]

    def _updateReduction(self, \
            bon_de_commande:BonDeCommand, \
                total:int=0, \
                rate_assure:int=0, \
                num_facture:int=0)->BonDeCommand:
        """Updates the total dettes in as reduction."""
        print(f"The bons is: {bon_de_commande}")
        if rate_assure:
            org = bon_de_commande.organization
            paid = total * ((org.rate_assure/100) or 1)
            bon_de_commande.cout = total - paid
            bon_de_commande.assu_rate = rate_assure
            bon_de_commande.montant_dette = paid
        else:
            bon_de_commande.cout = total
        bon_de_commande.total = total
        bon_de_commande.num_facture = num_facture
        bon_de_commande.save()

        return bon_de_commande
    
    def _completeBon(self,bon_de_commande:BonDeCommand,\
         code_operation:str)->BonDeCommand:
        bon_de_commande.meds += f"{code_operation};"
        bon_de_commande.save()
        return bon_de_commande
    
    def _createBon(self, client,\
        client_obj, assu_obj, \
        categorie)->int:
        """Will create a new instance of BonDeCommand
        according to client dict.
        """
        new_bon = BonDeCommand.objects.create\
            (beneficiaire=client_obj, \
            organization=assu_obj)
        new_bon.categorie = categorie
        # Dealing with uniqueness of num_bon
        if new_bon.organization.name \
            == "Pharmacie Ubuzima" or \
            new_bon.organization.name == "Sans":
            code_8 = GenerateCode(7)
            code_bon = code_8.giveCode()
            new_bon.num_bon = 'P_' + code_bon
            new_bon.is_paid = True
        else:
            new_bon.num_bon = client.get('numero_bon')
        
        if client.get('date_bon'):
            date_arr = stringToDate(client.get('date_bon'))
            new_bon.date_prescri = timezone.datetime(\
                date_arr[0], date_arr[1], date_arr[2])
        new_bon.date_served = timezone.now()

        new_bon.save()
        print(f"Bon de Command created successfully")

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
            qtee = float((str(obj)).replace('[',"").replace(']','').\
                replace("'",",", -1).split(" ")[1].split('}')[0])
            
            data.append([code_med, code, qtee])
        
        orders = self.__place_order(data=data, qte=qte)
        
        return orders
    
    def __place_order_abandonned(self, data:list, qte:int) -> list:
        """ The function takes a list of order and make a repartition of qte
        based on input data of this type:
            data = [['AL123', 'xt10', 2], ['AL123', 'xt11', 5]]

            with: qte = 1

        and return :  [['AL123', 'xt10', 1], ['AL123', 'xt11', 0]]
        """
        print(f"The qte received: {qte} from {data}") 
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
                print("Returned empty")
                return []
        print(f"QteReceived:{qte}, assessed:{data}")
        return data
    
    def __place_order_(self, data:list, qte:int) -> list:
        """ The function takes a list of order and make a repartition of qte
        based on input data of this type:
            data = [['AL123', 'xt10', 2], ['AL123', 'xt11', 5]]

            with: qte = 1

        and return :  [['AL123', 'xt10', 1], ['AL123', 'xt11', 0]]
        """
        # print(f"The qte received: {qte} from {data}") 
        reste = qte
        local_data = []
        if qte < 1:
            return []
        i = 0
        for elm in data:
            if (elm[2] > 0) and (elm[2] <= reste):
                local_data.append(elm)
                reste -= elm[2]
            elif elm[2] > reste:
                cp = elm
                cp[2] = reste
                local_data.append(cp)
                reste = 0
                break
        print(f"Have done: {local_data}")
        if reste:
            return []
        else:
            return local_data
    
    def _place_order(self, code_med:str='000', qte:int=0) -> list:
        """ The function takes a list of order and make a repartition of qte
        based on input data of this type:
            data = [['AL123', 'xt10', 2], ['AL123', 'xt11', 5]]

            with: qte = 1

        and return :  [['AL123', 'xt10', 1], ['AL123', 'xt11', 0]]
        """
        reste = qte
        today = timezone.localdate()

        imiti = UmutiEntree.objects.filter(\
            Q(code_med=code_med) & \
            Q(quantite_restant__gte=1) & \
            Q(date_peremption__gt=today)).order_by('date_peremption')
        local_data = []
        if qte == 0:
            return []
        i = 0
        for elm in imiti:
            if (elm.quantite_restant > 0) and (elm.quantite_restant <= reste):
                to_add = [code_med, elm.code_operation, elm.quantite_restant]
                local_data.append(to_add)
                reste -= elm.quantite_restant
            elif elm.quantite_restant > reste:
                to_add = [code_med, elm.code_operation, reste]
                local_data.append(to_add)
                reste = 0
                break
        if reste:
            return []
        else:
            return local_data
   
    def _imitiSell(self, umuti:UmutiEntree, \
                   qte:int, operator:str, \
                   reference_umuti:ImitiSet,\
                bon_de_commande:BonDeCommand)->str:
        """Will substract the quantite_restante in UmutiEntree and
        write a new instance of UmutiSell"""

        print(f"The umuti to work on is : {umuti} with qte: {qte} found with {umuti.quantite_restant}")
        print(f"To use BonDeCommand: {bon_de_commande}")
        # reference_umuti = ImitiSet.objects.get(code_med=umuti.code_med)
        new_vente = UmutiSold.objects.create(bon_de_commande=bon_de_commande)
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
        # new_vente.bon_de_commande = bon_de_commande
        umuti.quantite_restant -= round(float(qte), 1)

        umuti.save()
        new_vente.save()

        # print("Finished to Sell")
        
        return new_vente.code_operation
    
    @action(methods=['post'], detail=False,\
             permission_classes= [IsAdminUser])
    def cancelSell(self, request):
        """
        Cancel the operation of Sell, for a given 
        ID in umutiSold.
        """
        # data_sent = request.data.get('imiti', {'_value': 0}).get('_value')
        data_sent = request.data.get('imiti')
        umuti_sold_id = int(data_sent)
        umuti_sold = None
        try:
            umuti_sold = UmutiSold.objects.get(id=umuti_sold_id)
        except UmutiSold.DoesNotExist:
            return JsonResponse({
                'response': 404
            })
        retribution = self._retributeBon(umuti_sold)
        if retribution == 200:
            umuti_sold.cancelled = True
            umuti_sold.save()
            recordOperation(who_did_id=request.user,\
                what_operation=f"Annulé vente: {umuti_sold.nom_med[:10]} , qte:{umuti_sold.quantity} , pxV:{umuti_sold.prix_vente}",\
                from_value=" ",\
                to_value=" ")
            GeneralOps._update_code_for_sync(self=GeneralOps, code_med=umuti_sold.code_med)
            return JsonResponse({
                'response': 200
            })
        return JsonResponse({
            'response': 403
        })
    
    def _retributeBon(self, umuti_sold)->int:
        # umuti_sold = UmutiSold.objects.last()
        code_med = umuti_sold.code_med
        qte = umuti_sold.quantity 
        total_cost = qte * umuti_sold.prix_vente
        bon = umuti_sold.bon_de_commande
        assu_rate = bon.assu_rate
        code_operation = umuti_sold.code_operation
        code_operation_entrant = umuti_sold.code_operation_entrant

        meds = str(bon.meds).split(';')
        
        if not(code_operation in meds):
            return 404
        meds.remove(code_operation)
        if bon.total > total_cost:
            bon.total -= total_cost
            bon.cout = bon.total * ((100 - assu_rate) / 100)
            bon.montant_dette = bon.total * (assu_rate / 100)
            medstr = ''
            for med in meds:
                medstr += med + ';'
            bon.meds = medstr[:-1]
        elif bon.total == total_cost:
            bon.cancelled = True
        r_achat = self._retributeAchat(code_med=code_med, \
                        code_operation_entrant=code_operation_entrant, \
                        qte=qte )
        if r_achat != 200:
            return 404
        bon.save()
        
        return 200
    
    def _retributeAchat(self, code_med, code_operation_entrant, qte)->int:
        try:
            umuti_entree = UmutiEntree.objects.get(Q(code_med=code_med) & \
                                Q(code_operation=code_operation_entrant))
        except UmutiEntree.DoesNotExist:
            return 404
        umuti_entree.quantite_restant += qte
        umuti_entree.save()
        return 200

    @action(methods=['post', 'get'], detail=False,\
             permission_classes= [IsAdminUser])
    def add_perte(self, request):
        data = request.data
        print(f"The data sent: {data}")
        code_med = data.get('code_med', '')
        code_operation = data.get('code_operation', '')
        qte = (data.get('qte', 1))
        try:
            qte = int(qte)
        except ValueError:
            qte = 1
        motif = data.get('motif', 'Perime')

        if not (code_operation):
            return Response({
                'response': 0,
                'detail': 'no_code'
            })

        med = None
        prix_vente = 0
        try:
            med = UmutiEntree.objects.get(\
                Q(code_med=code_med) & \
                Q(code_operation=code_operation))
        except UmutiEntree.DoesNotExist:
            return Response({
                'response': 0,
                'detail': 'no_med_found'
            })
        med_set = ImitiSet.objects.get(code_med=code_med)
        prix_vente = med_set.prix_vente
        if (med.quantite_restant >= qte) and (qte > 0):
            med.quantite_restant -= qte
            med.save()
            result = self._record_perte(med=med, qte=qte, \
                                prix_achat=med.prix_achat,\
                                prix_vente=prix_vente,\
                                who_did_it=request.user, \
                                motif=motif)
            if result == 200:
                recordOperation(who_did_id=request.user, what_operation=f"Med ({code_med}, qte:{qte}) Perime", from_value='', to_value='')
                GeneralOps._update_code_for_sync(self=GeneralOps, code_med=code_med)
                return Response({
                    'response': 1
                    })
            return Response({
                'response': 0,
                'detail': 'echoue'
            })
        else:
            return Response({
                'response': 0,
                'detail': 'qte_insuffisant'
            })
    
    def _record_perte(self, med, qte,prix_achat, prix_vente, who_did_it, motif):
        new_perte = PerteMed.objects.create(med=med, \
                        who_did_it=who_did_it)
        new_perte.qte = qte
        new_perte.motif = motif
        new_perte.date_operation = timezone.now()
        new_perte.save()

        return 200

class Rapport(viewsets.ViewSet):
    """
    This class is meant to be of generating reports.
    """
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def report_operations(self, request):
        """
        Tells the critical operations recorded.
        """
        get_data = request.query_params
        begin_date, end_date = self._getDate1()
        dates = None
        if get_data:
            dates = [get_data.get('date_debut'), get_data.get('date_fin')]
            print(f"Dates are: {dates}")
            begin_date, end_date = self._getDate1(date1=dates[0],\
            date2=dates[1])
        end_date = end_date + timedelta(hours=23)\
                     + timedelta(minutes=59) + timedelta(seconds=59)
        
        operations = CriticalOperation.objects.filter(\
            Q(date_time__gte=begin_date) &\
            Q(date_time__lte=end_date)).order_by("-date_time")
        operation_seria = OperationSeria(operations, many=True)
        
        if operation_seria.is_valid:
            return Response({
                "response":operation_seria.data
            })
        return Response({
                'response': []
            })

    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def reportEntree(self, request):
        """making an endpoint that will return all the UmutiEntreeBackup instead of
          UmutiEntree entries."""
        get_data = request.query_params
        begin_date, end_date = self._getDate1()
        dates = None
        if get_data:
            dates = [get_data.get('date_debut'), get_data.get('date_fin')]
            print(f"Dates are: {dates}")
            begin_date, end_date = self._getDate1(date1=dates[0],\
            date2=dates[1])
        end_date = end_date + timedelta(hours=23)\
                     + timedelta(minutes=59) + timedelta(seconds=59)
        imiti = UmutiEntreeBackup.objects.filter(Q(date_entrant__gte=begin_date) &\
                    Q(date_entrant__lte=end_date)).order_by('-date_entrant')
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
        get_data = request.query_params
        begin_date, end_date = self._getDate1()
        dates = None

        if get_data:
            dates = [get_data.get('date_debut'), get_data.get('date_fin')]
            print(f"Dates are: {dates}")
            begin_date, end_date = self._getDate1(date1=dates[0],\
            date2=dates[1])
        end_date = end_date + timedelta(hours=23)\
                     + timedelta(minutes=59) + timedelta(seconds=59)
        
        meds = UmutiSold.objects.filter(Q(date_operation__gte=begin_date) &\
                    Q(date_operation__lte=end_date) & Q(cancelled=False))[::-1]
        meds_built = self._builtVente(meds)
        # imitiSerialized = SoldAsBonSeria(data=meds_built, many=True)
        # if imitiSerialized.is_valid():
        #     return Response(imitiSerialized.data)
        
        return JsonResponse({"response": meds_built})
    
    
    @action(methods=['get'], detail=False,\
             permission_classes= [IsAuthenticated])
    def reportBons(self, request):
        """
        Will return all the instances of BonDeCommand.
        """
        get_data = request.query_params
        begin_date, end_date = self._getDate1()
        dates = None

        if get_data:
            dates = [get_data.get('date_debut'), get_data.get('date_fin')]
            print(f"Dates are: {dates}")
            begin_date, end_date = self._getDate1(date1=dates[0],\
            date2=dates[1])

        bons = BonDeCommand.objects.filter(Q(date_served__gte=begin_date) &\
                    Q(date_served__lte=end_date) & Q(cancelled=False))[::-1]
        bons_serialized = BonDeCommandSeria(bons, many=True)
        if bons_serialized.is_valid:
            return JsonResponse({"response": bons_serialized.data})
        return JsonResponse({"response": []})
    
    def _getDate1(self, date1='', date2=''):
        """Takes two arguments of dates and return
        date_begin , date_end.
        """
        end_date = None
        begin_date = None
        if date1:
            date_arr = shortStr2Date(date1)
            begin_date = timezone.datetime(date_arr[0],\
                    date_arr[1], date_arr[2])
        else:
            # should bring the beginning of today.
            begin_date = timezone.now() - timedelta(hours=timezone.now().hour)
        if date2:
            date_arr = shortStr2Date(date2)
            end_date = timezone.datetime(date_arr[0],\
                    date_arr[1], date_arr[2])
        else:
            end_date = timezone.now()
        if begin_date > end_date:
            tmp = begin_date
            begin_date = end_date
            end_date = tmp
        
        return [begin_date, end_date]

    
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
            record_new.nb_rest = round(current.quantite_restant, 1)
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
          35% of the remaining quantity. for Recommandation"""
        imiti = ImitiSet.objects.all()
        less_35 = []
        for umuti in imiti:
            if (umuti.qte_entrant_big / (umuti.quantite_restant or 1)) < 3.5:
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
    
    @action(methods=['get','post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getStockRed(self, request):
        """
        Returns instances of ImitiSet with less 30%
        """
        meds = ImitiSet.objects.all()
        less_30 = []
        for med in meds:
            if (med.qte_entrant_big / (med.quantite_restant or 1)) > 3:
                less_30.append(med)
        less_30_seria = ImitiSetSeriazer(less_30, many=True)
        if less_30_seria.is_valid:
            return Response(less_30_seria.data)
        return JsonResponse({"none of":"less 30%"})
    
    @action(methods=['get','post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getStockYellow(self, request):
        """
        Returns instances with between 30 and 59 %
        """
        meds = ImitiSet.objects.all()
        yellows = []
        for med in meds:
            if (med.qte_entrant_big / (med.quantite_restant or 1)) < 3.3 \
                and  \
                (med.qte_entrant_big / (med.quantite_restant or 1)) > 1.6:
                yellows.append(med)
        yellow_seria = ImitiSetSeriazer(yellows, many=True)
        if yellow_seria.is_valid:
            return Response(yellow_seria.data)
        return JsonResponse({"None of":"Yellow"})
    
    @action(methods=['get','post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getStockGreen(self, request):
        """
        Returns instances with more than 60 %
        """
        meds = ImitiSet.objects.all()
        yellows = []
        for med in meds:
            if (float(med.qte_entrant_big / (med.quantite_restant or 1))) < 1.6:
                yellows.append(med)
        yellow_seria = ImitiSetSeriazer(yellows, many=True)
        if yellow_seria.is_valid:
            return Response(yellow_seria.data)
        return JsonResponse({"None of":"Yellow"})
    
    @action(methods=['get','post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getStockZero(self, request):
        """
        Returns instances with Zero %
        """
        meds = ImitiSet.objects.filter(quantite_restant=0)
        meds_seria = ImitiSetSeriazer(meds, many=True)
        if meds_seria.is_valid:
            return Response(meds_seria.data)
        return JsonResponse({"None of":"zero"})
    
    @action(methods=['get','post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getMedFuture(self, request):
        """
        Returns instances of UmutiEntree with date peremption
        with 2 years.
        """
        today = timezone.now()
        two_year = today + timedelta(days=720)
        meds = UmutiEntree.objects.filter(\
            quantite_restant__gte=1).filter(\
            date_peremption__gte=two_year)
        meds_seria = UmutiEntreeSeriazer(meds, many=True)
        if meds_seria.is_valid:
            return Response(meds_seria.data)
        return JsonResponse({"status":0})
    
    @action(methods=['get','post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getMedGreen(self, request):
        """
        Returns instances of UmutiEntree with date peremption
        within 1 - 2 years.
        """
        today = timezone.now()
        one_year = today + timedelta(days=360)
        two_year = today + timedelta(days=720)
        meds = UmutiEntree.objects.filter(\
            Q(quantite_restant__gte=1) & Q(date_peremption__gte=one_year) & Q(date_peremption__lte=two_year))
            
        meds_seria = UmutiEntreeSeriazer(meds, many=True)
        if meds_seria.is_valid:
            return Response(meds_seria.data)
        return JsonResponse({"status":0})
    
    @action(methods=['get','post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getMedMedium(self, request):
        """
        Returns instances of UmutiEntree with date peremption
        within 1 - 2 years.
        """
        today = timezone.now()
        six_month = today +timedelta(days=180)
        one_year = today + timedelta(days=360)
        meds = UmutiEntree.objects.filter(\
            Q(quantite_restant__gte=1) & Q(date_peremption__gte=six_month) & Q(date_peremption__lte=one_year))
        meds_seria = UmutiEntreeSeriazer(meds, many=True)
        if meds_seria.is_valid:
            return Response(meds_seria.data)
        return JsonResponse({"status":0})
    
    # @action(methods=['get','post'], detail=False,\
    #          permission_classes= [IsAuthenticated])
    # def getMedYellow(self, request):
    #     """
    #     Returns instance of UmutiEntree with date peremption
    #     with less 1 year and above 6months
    #     """
    #     today = timezone.now()
    #     six_month = today + timedelta(days=180)
    #     one_year = today + timedelta(days=360)
    #     meds = UmutiEntree.objects.filter(\
    #         quantite_restant__gte=1).filter(\
    #         date_peremption__gte=six_month).\
    #         exclude(date_peremption__gte=one_year)
    #     meds_seria = UmutiEntreeSeriazer(meds, many=True)
    #     if meds_seria.is_valid:
    #         return Response(meds_seria.data)
    #     return JsonResponse({"status":0})
    

    @action(methods=['get','post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getMedYellow(self, request):
        """
        Returns instance of UmutiEntree with date peremption
        with less 1 year and above 6months
        """
        today = timezone.now()
        six_month = today + timedelta(days=180)
        meds = UmutiEntree.objects.filter(\
            Q(quantite_restant__gte=1) &\
            Q(date_peremption__lt=six_month) & \
            Q(date_peremption__gte=today))
        meds_seria = UmutiEntreeSeriazer(meds, many=True)
        if meds_seria.is_valid:
            return Response(meds_seria.data)
        return JsonResponse({"status":0})
    
    # @action(methods=['get','post'], detail=False,\
    #          permission_classes= [IsAuthenticated])
    # def getMedRed(self, request):
    #     """Returns instances of UmutiEntree with date peremption
    #     in critical stage, not to serve the patient
    #     """
    #     today = timezone.now()
    #     six_month = today + timedelta(days=180)
    #     meds = UmutiEntree.objects.filter(\
    #         quantite_restant__gte=1).filter(\
    #         date_peremption__lt=six_month)
    #     meds_seria = UmutiEntreeSeriazer(meds, many=True)
    #     if meds_seria.is_valid:
    #         return Response(meds_seria.data)
    #     return JsonResponse({"status":0})
    
    @action(methods=['get','post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def getMedRed(self, request):
        """Returns instances of UmutiEntree with date peremption
        in critical stage, not to serve the patient
        """
        today = timezone.now()
        six_month = today + timedelta(days=180)
        meds = UmutiEntree.objects.filter(\
            quantite_restant__gte=1).filter(\
            date_peremption__lte=today)
        meds_seria = UmutiEntreeSeriazer(meds, many=True)
        if meds_seria.is_valid:
            return Response(meds_seria.data)
        return JsonResponse({"status":0})
        
    
    
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
                    data_sent.get('last_umutiEntree'))
        imiti_sold = UmutiSold.objects.filter(id__gte=\
                    data_sent.get('last_umutiSold'))
        
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
        begin_date, end_date = self._getDate(request.data)
        x = [] # date
        y = [] # quantifiers
        while begin_date <= end_date:
            query = UmutiSold.objects.filter\
                (Q(date_operation__gte=begin_date) & \
                 Q(date_operation__lt=begin_date+timedelta(days=0.8)))
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
            end_date = timezone.now()
        print("THe dates are: ", begin_date, end_date)

        return [begin_date, end_date]
    
    # def _builtVente(self, meds):
    #     """
    #     Will return a mixed info from
    #       UmutiSold, BonDeCommand and Assurance.
    #     needed dict: {
    #         'nom_med', 'qte', 'pa','pv','total','bnf',
    #         'caisse', 'dette', 'assu', 'categ','date',
    #         'id_bon', 'is_paid'
    #     }
    #     """
    #     bons = []
    #     for umuti_sold in meds:
    #         vente = {}
    #         vente['nom_med'] = umuti_sold.nom_med
    #         vente['qte'] = umuti_sold.quantity
    #         vente['prix_achat'] = umuti_sold.prix_achat
    #         vente['prix_vente'] = umuti_sold.prix_vente
    #         vente['total'] = umuti_sold.prix_vente * umuti_sold.quantity
    #         vente['bnf'] = (umuti_sold.prix_vente - umuti_sold.prix_achat)\
    #                         * umuti_sold.quantity
    #         bon = umuti_sold.bon_de_commande
    #         assu = bon.organization
    #         assu_name = assu.name
    #         rate = assu.rate_assure
    #         vente['dette'] = bon.montant_dette
    #         vente['caisse'] = vente['total'] - bon.montant_dette
    #         if bon.montant_dette:
    #             vente['dette'] = vente['total'] - bon.montant_dette
    #             vente['caisse'] = bon.montant_dette
    #         vente['assu'] = assu_name
    #         vente['categ'] = bon.categorie
    #         vente['date_operation'] = bon.date_prescri
    #         vente['date_served'] = bon.date_served
    #         vente['num_bon'] = bon.num_bon
    #         vente['is_paid'] = bon.is_paid

    #         bons.append(vente)
        
    #     return bons
    
    def _builtVente(self, meds):
        """
        Will return a mixed info from
          UmutiSold, BonDeCommand and Assurance.
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
            vente['dette'] = bon.montant_dette
            vente['caisse'] = vente['total'] - bon.montant_dette
            if bon.montant_dette:
                vente['dette'] = vente['total'] * (bon.assu_rate / 100)
                vente['caisse'] = vente['total'] - vente['dette']
            vente['assu'] = assu_name
            vente['categ'] = bon.categorie
            vente['date_operation'] = bon.date_prescri
            vente['date_served'] = bon.date_served
            vente['num_bon'] = bon.num_bon
            vente['is_paid'] = bon.is_paid
            vente['rate'] = bon.assu_rate
            vente['id'] = umuti_sold.id
            vente['caissier'] = umuti_sold.operator

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
        Return UmutiSold instance(s) with the unpaid BonDeCommand.
        default range is 7 days.
        """
        begin_date, end_date = self._getDate(request.data)
        # queryset = BonDeCommand.filter(date_du_bon__gte=begin_date)\
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
    

    @action(methods=['get','post'], detail=False,\
             permission_classes= [AllowAny])
    def getOnNoBon(self, request):
        """
        Will return all two variables: 
        - sum of ones UmutiSold without BonDeCommand
        - sum of ones UmutiSold with BonDeCommand 
        """
        begin_date, end_date = self._getDate(request.data)
        on_bon, no_bon = 0, 0
        x, y = [], []
        c1 = "Ordinary"
        c2 = "Special"
        
        queryset = BonDeCommand.objects.filter\
            (Q(date_served__gte=begin_date) & \
             Q(date_served__lte=end_date))
        query1 = queryset.filter(Q(beneficiaire__beneficiaire=c1) | \
                                 Q(beneficiaire__beneficiaire=c2))
        query2 = queryset.exclude(Q(beneficiaire__beneficiaire=c1) | \
                                 Q(beneficiaire__beneficiaire=c2))
        no_bon = len(query1)
        on_bon = len(query2)

        y = ['Avec_bon', 'Sans_bon']
        x = [on_bon, no_bon]

        return JsonResponse({"X": x, "Y":y})
    

    @action(methods=['get','post'], detail=False,\
             permission_classes= [AllowAny])
    def getCate(self, request):
        """
        Will return the comparison of categories:
        tv, mt, md, au, ord(for simple clients).
        Should source in BonDeCommand
        """
        begin_date, end_date = self._getDate(request.data)
        tv, mt, md, au, ord = 0,0,0,0,0
        x, y = [], []
        queryset = BonDeCommand.objects.filter(date_served__gte=begin_date)\
            .filter(date_served__lte=end_date)
        tv = len(queryset.filter(categorie='tv'))
        mt = len(queryset.filter(categorie='mt'))
        md = len(queryset.filter(categorie='md'))
        au = len(queryset.filter(categorie='au'))
        ord = len(queryset.filter(categorie='no'))

        y = ['Taxi_v','Motar', 'Dom_med', 'Assure', 'Ordinaire']
        x = [tv, mt, md, au, ord]

        return JsonResponse({"X": x, "Y":y})
    


