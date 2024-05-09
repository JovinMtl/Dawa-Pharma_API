from rest_framework.test import APITestCase
from datetime import datetime
from django.urls import reverse

from unittest.mock import MagicMock, Mock

#importing the class to be tested
from api.views import Rapport


class RapportTestCase(APITestCase):
    """I want to test Rapport viewset"""

    def setUp(self) -> None:
        self.data = {
            'date1': datetime.now()
        }
        self.url = reverse('rep-reportSell')
        self.request = self.client.post(self.url, data=self.data)
        self.instance_rapport = Rapport()
    
    def test_Rapport(self):
        print(f"The result is : {self.request.json()}")
        self.assertAlmostEquals(self.request.status_code, 200)

    def test_recordNew(self):
        """Testing the record new. umuti_new is of type umutiSold"""
        umuti_sold = MagicMock
        umuti_sold.code_umuti = 1
        umuti_sold.name_umuti = "test 1 umuti"
        umuti_sold.quantity = 3
        umuti_sold.price_out = 1500

        umuti_sold.price_total = 4500
        umuti_sold.price_in = 1200
        umuti_sold.difference = 900

        response = self.instance_rapport._recordNew(umuti=umuti_sold)

        print(f"The response is : {response.name_umuti}")
    
    def test_makeReport(self):
        """Works on umutiSold objects"""
        umuti_sold = MagicMock
        umuti_sold.code_umuti = 1
        umuti_sold.name_umuti = "test 1 umuti"
        umuti_sold.quantity = 3
        umuti_sold.price_out = 1500

        umuti_sold.price_total = 4500
        umuti_sold.price_in = 1200
        umuti_sold.difference = 900
    #     umuti_sold_qs.iterator.return_value = iter((individual_obj1, individual_obj2, individual_obj3))
        response = self.instance_rapport._makeReport([ umuti_sold])
        assert response == 200
    
    def test_updateRecord(self):
        """Will have to use umuti_set:umutiReportSell & umuti:UmutiSold
        umuti_set: nb_rest, nb_vente, px_T_vente, benefice, px_T_rest
        umuti: quantity, price_in, price_out, 
        """
        umuti_set = Mock
        umuti_set.nb_rest = 4
        umuti_set.nb_vente = 3
        umuti_set.px_T_vente = 4500
        umuti_set.benefice = 900
        umuti_set.px_T_rest = 8000
        
        umuti_set.save = Mock()
        umuti_set.save.return_value = 0

        umuti = MagicMock
        umuti.quantity = 3
        umuti.price_in = 1200
        umuti.price_out = 1500

        response = self.instance_rapport._updateRecord(umuti_set=umuti_set\
                                                       , umuti=umuti)
        print(f"umuti_set test: {(response)}")
