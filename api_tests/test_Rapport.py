from rest_framework.test import APITestCase
from datetime import datetime


class RapportTestCase(APITestCase):
    """I want to test Rapport viewset"""

    def setUp(self) -> None:
        self.data = {
            'date1': datetime.now()
        }
        self.request = self.client.post('http://127.0.0.1:8002/api/rep/reportSell/', data=self.data)
    
    def test_Rapport(self):
        print(f"The result is : {self.request}")