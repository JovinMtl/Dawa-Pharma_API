from rest_framework.test import APITestCase
from datetime import datetime
from django.urls import reverse

from unittest.mock import MagicMock

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
        """Testing the record new. umuti_new is of type umutiReportSell"""
        umuti_new = MagicMock
        umuti_new.code_umuti = 1
        umuti_new.name_umuti = "test 1 umuti"
        umuti_new.nb_vente = 3
        umuti_new.px_T_vente = 1500
        umuti_new.benefice = 300
        umuti_new.nb_rest = 7
        umuti_new.px_T_rest = 3500

        response = self.instance_rapport._recordNew(umuti=umuti_new)

        print(f"The response is : {response}")
    
    # def test_makeReport(self):
    #     umuti_sold_qs = MagicMock()
    #     umuti_sold_qs.count.return_value = 3
    #     individual_obj1 = MagicMock()
    #     individual_obj1.code_umuti = 1
    #     individual_obj2 = MagicMock()
    #     individual_obj2.code_umuti = 2
    #     individual_obj3 = MagicMock()
    #     individual_obj3.code_umuti = 3
    #     umuti_sold_qs.iterator.return_value = iter((individual_obj1, individual_obj2, individual_obj3))

    #     # response = self.instance_rapport._makeReport(umuti_sold_qs)
    #     response = self.instance_rapport._makeReport([ individual_obj1])
    #     assert response == 200