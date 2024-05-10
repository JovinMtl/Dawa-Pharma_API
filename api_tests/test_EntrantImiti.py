
from rest_framework.test import APITestCase
from datetime import datetime, timedelta
from django.urls import reverse
import json


from unittest.mock import Mock

from api.shared.stringToList import StringToList

#importing the class to be tested
from api.views import EntrantImiti


class EntrantImitiTestCase(APITestCase):
    """I want test all the operations done in EntrantImiti viewset"""

    def setUp(self) -> None:
        self.instance = EntrantImiti()

    def test_umutiMushasha(self):
        umuti_entree = Mock()
        umuti_entree.date_winjiriyeko = datetime.today()
        umuti_entree.date_uzohererako = datetime.today() + \
            timedelta(days=360)
        umuti_entree.code_umuti = 'a23et'
        umuti_entree.name_umuti = 'amoxi'
        umuti_entree.description_umuti = 'kuvura malaria'
        umuti_entree.type_umuti = 'Flacon'
        umuti_entree.type_in = 'carton'
        umuti_entree.ratio_type = 1
        umuti_entree.type_out = 'plaquette'
        umuti_entree.price_in = 1200
        umuti_entree.price_out = 1500
        umuti_entree.difference = 300
        umuti_entree.quantite_initial = 8
        umuti_entree.quantite_restant = 8
        umuti_entree.location = 'a1'

        reponse = self.instance._umutiMushasha(umuti=umuti_entree)
        assert reponse.name_umuti == 'amoxi'

    def test_StringToList(self):
        # testing the right format of string to be passed in
        jove = " [{'date': '2025-04', 'qte': 4, 'code_operation': '12dxx9'}, {'date': '2024-08', 'qte': 7, 'code_operation': '23dd'}] "
        obj = StringToList(jove=jove)
        result = obj.toList()
        assert type(result) == list

        # testing the wrong format of string
        jove = "jovie"
        obj = StringToList(jove=jove)
        result = obj.toList()
        assert result == None

        # in case not string is given
        obj = StringToList()
        result = obj.toList()
        assert result == None

        

    def test_findLastDate(self):
        pass

    def test_compileImitiSet(self):
        pass