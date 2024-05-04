from datetime import datetime
from django.test import TestCase

# from api.views import Rapport
from ..views import Rapport



class RapportTestCase(TestCase):
    """I want to test Rapport viewset"""

    def setUp(self) -> None:
        self.date1 = datetime.now()
    

    def test_reportSell(self):
        obj = Rapport()
        data = {
            'date1': self.date1
        }
        report = obj.reportSell(data)
        print(f"The TEST is done: {report}")

        # self.assertEqual(formatted_name, "thierryjovin")

        return 0