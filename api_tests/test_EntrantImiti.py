
from rest_framework.test import APITestCase
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
import json


from unittest.mock import Mock, patch

from api.shared.stringToList import StringToList

#importing the class to be tested
from api.views import EntrantImiti

#importing a model to mock about its operation
from pharma.models import UmutiSold, UsdToBif


class EntrantImitiTestCase(APITestCase):
    """I want test all the operations done in EntrantImiti viewset"""

    def setUp(self) -> None:
        self.instance = EntrantImiti()
        # Create required UsdToBif record for _umutiMushasha
        UsdToBif.objects.get_or_create(id=1, defaults={'actualExchangeRate': 2800})

    def test_umutiMushasha(self):
        umuti_entree = Mock()
        umuti_entree.date_winjiriyeko = timezone.now()
        umuti_entree.date_peremption = timezone.now() + \
            timedelta(days=360)
        umuti_entree.code_umuti = 'a23et'
        umuti_entree.name_umuti = 'amoxi'
        umuti_entree.description_umuti = 'kuvura malaria'
        umuti_entree.type_umuti = 'Flacon'
        umuti_entree.type_in = 'carton'
        umuti_entree.ratio = 1
        umuti_entree.type_out = 'plaquette'
        umuti_entree.prix_achat = 1200
        umuti_entree.prix_vente = 1500
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

        # in case no string is given
        obj = StringToList()
        result = obj.toList()
        assert result == None

    
    def give_date(self):
        with patch('EntrantImiti._findLastDate') as date_patched:
            date_patched.return_value = {'date_operation': timezone.now()}

    def test_findLastDate(self):
        code_med = 'jo33'
        UmutiSold = Mock()
        # UmutiSold.objects.filter.side_effect = self._give_umutiSold()
        UmutiSold.objects.filter().last.return_value = type('obj', (object,), {'date_operation': timezone.now()})
        # umuti.date_operation = datetime.today()
        reponse = self.instance._findLastDate(code_med=code_med)

        print(f"The response is {reponse}")

        # assert reponse.date_operation == datetime.today()
    
    # def test_findLastDate_mock(self):
    #     with patch('UmutiSold.objects.filter().last') as mock_filter_last:
    #         mock_filter_last.return_value = type('obj', (object,), {'date_operation': datetime.today()})
    #         my_instance = EntrantImiti()  # Instantiate the class containing _findLastDate method
    #         result = my_instance._findLastDate('your_code_umuti')
    #         self.assertEqual(result, datetime.today().date())  # Assert the result
    
    def _give_umutiSold(self):
        print("We need to return the object")
        return {'date_operation': 'datetime.today()'}

    def test_compileImitiSet(self):
        pass
