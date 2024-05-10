
from unittest.mock import  Mock
from rest_framework.test import APITestCase
from django.db.utils import OperationalError

from api.code_generator import GenerateCode


class GenerateCodeTestCase(APITestCase):
    """I want to test the code generated that:
    - I get an error when not used on the appropriate mode,
    - that also the code generated has length equal to the number
    initialized
    """

    def test_GenerateCode(self):
        generator = GenerateCode(12)
        generator.giveCode = Mock()
        generator.giveCode.side_effect = OperationalError
        self.assertRaises(OperationalError)

        code = generator.gene()
        assert len(code) == 12