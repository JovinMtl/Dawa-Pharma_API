

import unittest
from datetime import datetime
from unittest import mock
from django.test import TestCase
from yourapp.models import UmutiSold
from yourapp.yourmodule import YourClass

class YourClassTestCase(TestCase):
    def test_findLastDate_mock(self):
        with mock.patch('yourapp.models.UmutiSold.objects.filter().last') as mock_filter_last:
            mock_filter_last.return_value = type('obj', (object,), {'date_operation': datetime.today()})
            your_instance = YourClass()  # Instantiate the class containing _findLastDate method
            result = your_instance._findLastDate('your_code_umuti')
            self.assertEqual(result, datetime.today().date())  # Assert the result
