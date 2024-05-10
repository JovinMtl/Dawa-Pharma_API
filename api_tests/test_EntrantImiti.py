
from rest_framework.test import APITestCase
from datetime import datetime, timedelta
from django.urls import reverse
from django.db.utils import OperationalError

from unittest.mock import MagicMock, Mock

#importing the class to be tested
from api.views import EntrantImiti
from api.code_generator import GenerateCode


class RapportTestCase(APITestCase):
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
        pass
        
    def test_GenerateCode(self):
        generator = GenerateCode(12)
        generator.giveCode = Mock()
        generator.giveCode.side_effect = OperationalError
        self.assertRaises(OperationalError)

        code = generator.gene()
        assert len(code) == 12

    def test_findLastDate(self):
        pass

    def test_compileImitiSet(self):
        pass