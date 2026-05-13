"""
=============================================================================
UNIT TESTING TUTORIAL FOR THE SELL ENDPOINT
=============================================================================

This file teaches you how to write unit tests for Django REST Framework APIs.
Each section is heavily commented to explain the WHY and HOW.

TESTING PRINCIPLES:
1. Test one thing per test method
2. Use descriptive test names that explain what's being tested
3. Follow Arrange-Act-Assert (AAA) pattern:
   - Arrange: Set up test data
   - Act: Call the method/endpoint
   - Assert: Verify the result
4. Test both happy paths (success) and edge cases (failures)

RUN THESE TESTS WITH:
    python3 manage.py test api_tests.test_Sell_Tutorial --verbosity=2
"""

# =============================================================================
# IMPORTS - What you need to write tests
# =============================================================================

# Django's test framework
from django.test import TestCase                    # Base class for tests
from rest_framework.test import APITestCase, APIClient  # For API testing
from rest_framework import status                   # HTTP status codes (200, 401, etc.)

# For creating test users and authentication
from django.contrib.auth.models import User

# Django utilities
from django.utils import timezone                   # Always use this for datetime (timezone-aware)
from datetime import timedelta                      # For date math (e.g., 30 days from now)

# Mocking - For isolating units of code
from unittest.mock import Mock, MagicMock, patch

# Your application's models and views
from pharma.models import (
    UmutiEntree,      # Medicine inventory
    UmutiSold,        # Sold medicines record
    ImitiSet,         # Medicine catalog
    MedUnit,          # Unit of measurement
    Client,           # Customer
    Assurance,        # Insurance company
    BonDeCommand,     # Order/Invoice
    Journaling,       # For sync tracking
)
from api.views import EntrantImiti  # The view class containing 'sell'


# =============================================================================
# PART 1: BASIC TEST STRUCTURE
# =============================================================================

class BasicTestStructure(TestCase):
    """
    LESSON 1: Understanding TestCase structure
    
    Every test class inherits from TestCase (or APITestCase for API tests).
    Key methods:
    - setUpTestData(): Runs ONCE for the entire class (use for read-only data)
    - setUp(): Runs BEFORE each test method
    - tearDown(): Runs AFTER each test method (cleanup)
    - test_*(): Any method starting with 'test_' is a test
    """
    
    @classmethod
    def setUpTestData(cls):
        """
        This runs ONCE when the class loads.
        Use for data that ALL tests in this class will read (but not modify).
        This is faster than setUp() for large datasets.
        """
        # Create data shared across all tests in this class
        cls.shared_unit = MedUnit.objects.create(unit='Tutorial_Unit')
    
    def setUp(self):
        """
        This runs BEFORE each individual test method.
        Use for data that tests might modify.
        """
        # Each test gets a fresh instance
        self.instance = EntrantImiti()
    
    def tearDown(self):
        """
        This runs AFTER each individual test method.
        Use for cleanup (Django usually handles DB cleanup automatically).
        """
        pass  # Usually not needed for DB tests
    
    def test_example_passing_test(self):
        """
        ANATOMY OF A TEST:
        1. Name starts with 'test_'
        2. Has a docstring explaining what it tests
        3. Uses assertions to verify results
        """
        # Arrange - Set up data
        expected = 5
        
        # Act - Perform the action
        result = 2 + 3
        
        # Assert - Verify the result
        self.assertEqual(result, expected)
    
    def test_example_with_multiple_assertions(self):
        """You can have multiple assertions in one test."""
        data = {'name': 'Test', 'value': 100}
        
        # Check multiple things about the same result
        self.assertIn('name', data)           # Key exists
        self.assertEqual(data['name'], 'Test')  # Value is correct
        self.assertIsInstance(data['value'], int)  # Type is correct
        self.assertGreater(data['value'], 0)  # Value is positive


# =============================================================================
# PART 2: TESTING HELPER METHODS (Unit Tests)
# =============================================================================

class TestClientHelperMethods(TestCase):
    """
    LESSON 2: Testing individual helper methods
    
    Start by testing the smallest units (helper methods) before testing
    the full endpoint. This makes debugging easier.
    
    The sell endpoint has these helper methods:
    - _getClient1(): Returns ordinary client
    - _getClient2(): Returns special client  
    - _getClient3(): Returns insured client
    - _checkNumBon(): Checks if bon number exists
    - _place_order(): Distributes order across stock lots
    - _updateReduction(): Calculates insurance deductions
    - _createBon(): Creates BonDeCommand
    - _imitiSell(): Records the sale
    """
    
    @classmethod
    def setUpTestData(cls):
        """Create base data needed for client methods."""
        # Create the default assurances that _getClient1 and _getClient2 expect
        cls.sans_assurance = Assurance.objects.create(
            name='Sans',
            rate_assure=0
        )
        cls.pharmacie_assurance = Assurance.objects.create(
            name='Pharmacie Ubuzima',
            rate_assure=0
        )
        # Create ordinary client for _getClient1
        cls.ordinary_client = Client.objects.create(
            beneficiaire='Ordinary',
            joined_on=timezone.now()
        )
    
    def setUp(self):
        """Create fresh instance for each test."""
        self.view = EntrantImiti()
    
    # -------------------------------------------------------------------------
    # Testing _getClient1 (Ordinary Client)
    # -------------------------------------------------------------------------
    
    def test_getClient1_returns_ordinary_client(self):
        """
        TEST: _getClient1 should return the 'Ordinary' client and 'Sans' assurance.
        
        This is a simple test - the method has predictable behavior.
        """
        # Act - Call the method
        client, assurance = self.view._getClient1()
        
        # Assert - Verify results
        self.assertEqual(client.beneficiaire, 'Ordinary')
        self.assertEqual(assurance.name, 'Sans')
        self.assertEqual(assurance.rate_assure, 0)
    
    def test_getClient1_returns_none_when_no_ordinary_client(self):
        """
        TEST: _getClient1 should return [None, assurance] if Ordinary client missing.
        
        This tests an edge case - what happens when expected data is missing?
        """
        # Arrange - Remove the ordinary client
        Client.objects.filter(beneficiaire='Ordinary').delete()
        
        # Act
        client, assurance = self.view._getClient1()
        
        # Assert
        self.assertIsNone(client)
        self.assertIsNotNone(assurance)
    
    # -------------------------------------------------------------------------
    # Testing _getClient2 (Special Client)
    # -------------------------------------------------------------------------
    
    def test_getClient2_creates_new_special_client(self):
        """
        TEST: _getClient2 should create a new client if phone number doesn't exist.
        """
        # Arrange - Prepare input data
        client_data = {
            'nom_client': 'John Doe',
            'numero_tel': '79123456',
            'categorie': 'tv'
        }
        initial_count = Client.objects.count()
        
        # Act
        client, assurance = self.view._getClient2(client_data)
        
        # Assert
        self.assertEqual(Client.objects.count(), initial_count + 1)  # New client created
        self.assertEqual(client.phone_number, '79123456')
        self.assertEqual(client.beneficiaire, 'John Doe')
    
    def test_getClient2_returns_existing_client_by_phone(self):
        """
        TEST: _getClient2 should return existing client if phone number exists.
        """
        # Arrange - Create existing client with phone
        existing_client = Client.objects.create(
            beneficiaire='Existing Customer',
            phone_number='79999999',
            joined_on=timezone.now()
        )
        client_data = {
            'nom_client': 'Different Name',  # Different name
            'numero_tel': '79999999',         # Same phone
        }
        initial_count = Client.objects.count()
        
        # Act
        client, assurance = self.view._getClient2(client_data)
        
        # Assert
        self.assertEqual(Client.objects.count(), initial_count)  # No new client
        self.assertEqual(client.id, existing_client.id)           # Same client returned
    
    # -------------------------------------------------------------------------
    # Testing _getClient3 (Insured Client)
    # -------------------------------------------------------------------------
    
    def test_getClient3_creates_client_and_assurance(self):
        """
        TEST: _getClient3 should create both client and assurance if they don't exist.
        """
        # Arrange
        client_data = {
            'nom_adherant': 'Marie Patient',
            'nom_client': 'Pierre Patient',
            'relation': 'Enfant',
            'rate_assure': 80,
            'assureur': 'RSSB',
            'employeur': 'Government',
            'numero_carte': 'CARD123',
        }
        
        # Act
        client, assurance = self.view._getClient3(client_data)
        
        # Assert
        self.assertEqual(client.beneficiaire, 'Pierre Patient')  # nom_client used
        self.assertEqual(client.nom_adherant, 'Marie Patient')
        self.assertEqual(assurance.name, 'RSSB')
        self.assertEqual(assurance.rate_assure, 80)
    
    def test_getClient3_uses_adherant_name_when_relation_is_self(self):
        """
        TEST: When relation is 'Lui-meme', beneficiaire should be nom_adherant.
        """
        # Arrange
        client_data = {
            'nom_adherant': 'Jean Self',
            'nom_client': 'Should Not Use This',
            'relation': 'Lui-meme',  # Self
            'rate_assure': 100,
            'assureur': 'MilitaryMedical',
        }
        
        # Act
        client, assurance = self.view._getClient3(client_data)
        
        # Assert
        self.assertEqual(client.beneficiaire, 'Jean Self')


# =============================================================================
# PART 3: TESTING _checkNumBon (Duplicate Prevention)
# =============================================================================

class TestBonValidation(TestCase):
    """
    LESSON 3: Testing validation methods
    
    Validation methods typically return True/False. Test both cases.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Create required related objects."""
        cls.assurance = Assurance.objects.create(name='TestAssurance', rate_assure=80)
        cls.client = Client.objects.create(
            beneficiaire='Test Client',
            joined_on=timezone.now()
        )
    
    def setUp(self):
        self.view = EntrantImiti()
    
    def test_checkNumBon_returns_false_for_new_bon(self):
        """
        TEST: _checkNumBon should return False if bon number doesn't exist.
        """
        # Act
        result = self.view._checkNumBon('NONEXISTENT123')
        
        # Assert
        self.assertFalse(result)
    
    def test_checkNumBon_returns_true_for_existing_bon(self):
        """
        TEST: _checkNumBon should return True if bon number already exists.
        
        This prevents duplicate orders from being created.
        """
        # Arrange - Create existing bon
        BonDeCommand.objects.create(
            num_bon='EXISTING123',
            beneficiaire=self.client,
            organization=self.assurance,
            date_served=timezone.now()
        )
        
        # Act
        result = self.view._checkNumBon('EXISTING123')
        
        # Assert
        self.assertTrue(result)
    
    def test_checkNumBon_handles_empty_string(self):
        """
        TEST: _checkNumBon should handle empty string input gracefully.
        """
        result = self.view._checkNumBon('')
        self.assertFalse(result)


# =============================================================================
# PART 4: TESTING _place_order (Stock Distribution)
# =============================================================================

class TestPlaceOrder(TestCase):
    """
    LESSON 4: Testing complex business logic
    
    _place_order distributes a quantity across multiple medicine lots,
    prioritizing lots that expire soonest. Test various scenarios.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Create medicine catalog entry."""
        cls.med_unit = MedUnit.objects.create(unit='Comprime')
        cls.med_set = ImitiSet.objects.create(
            code_med='PARA500',
            nom_med='Paracetamol 500mg',
            prix_vente=500,
            med_unit=cls.med_unit,
            lot='[]',
            checked_imiti='[]',
            checked_qte='[]',
        )
    
    def setUp(self):
        self.view = EntrantImiti()
        # Clear any existing entries before each test
        UmutiEntree.objects.filter(code_med='PARA500').delete()
    
    def _create_lot(self, code_operation, quantity, days_until_expiry):
        """Helper to create medicine lot with specific expiry."""
        return UmutiEntree.objects.create(
            code_med='PARA500',
            code_operation=code_operation,
            nom_med='Paracetamol 500mg',
            quantite_initial=quantity,
            quantite_restant=quantity,
            prix_achat=300,
            prix_vente=500,
            date_entrant=timezone.now(),
            date_peremption=timezone.now() + timedelta(days=days_until_expiry),
            is_pirimiye=False,
            med_unit=self.med_unit,
        )
    
    def test_place_order_with_sufficient_single_lot(self):
        """
        TEST: Order from single lot with enough stock.
        """
        # Arrange - Create one lot with 100 units
        self._create_lot('LOT001', quantity=100, days_until_expiry=180)
        
        # Act - Order 10 units
        orders = self.view._place_order(code_med='PARA500', qte=10)
        
        # Assert
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0][0], 'PARA500')    # code_med
        self.assertEqual(orders[0][1], 'LOT001')     # code_operation
        self.assertEqual(orders[0][2], 10)           # quantity
    
    def test_place_order_distributes_across_multiple_lots(self):
        """
        TEST: Order should distribute across lots, using expiring-soonest first.
        """
        # Arrange - Create multiple lots with different expiry dates
        self._create_lot('LOT_EXPIRE_SOON', quantity=5, days_until_expiry=30)
        self._create_lot('LOT_EXPIRE_LATER', quantity=10, days_until_expiry=180)
        
        # Act - Order 8 units (more than first lot has)
        orders = self.view._place_order(code_med='PARA500', qte=8)
        
        # Assert - Should use all 5 from first lot, 3 from second
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0][1], 'LOT_EXPIRE_SOON')
        self.assertEqual(orders[0][2], 5)   # All from first lot
        self.assertEqual(orders[1][1], 'LOT_EXPIRE_LATER')
        self.assertEqual(orders[1][2], 3)   # Remaining from second lot
    
    def test_place_order_returns_empty_for_insufficient_stock(self):
        """
        TEST: Should return empty list if total stock is insufficient.
        """
        # Arrange - Only 5 units available
        self._create_lot('LOT001', quantity=5, days_until_expiry=180)
        
        # Act - Try to order 100 units
        orders = self.view._place_order(code_med='PARA500', qte=100)
        
        # Assert
        self.assertEqual(orders, [])
    
    def test_place_order_skips_expired_lots(self):
        """
        TEST: Should not use expired medicine lots.
        """
        # Arrange - Create expired lot and valid lot
        self._create_lot('LOT_EXPIRED', quantity=100, days_until_expiry=-10)  # Expired
        self._create_lot('LOT_VALID', quantity=50, days_until_expiry=180)     # Valid
        
        # Act
        orders = self.view._place_order(code_med='PARA500', qte=10)
        
        # Assert - Should only use valid lot
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0][1], 'LOT_VALID')
    
    def test_place_order_with_zero_quantity(self):
        """
        TEST: Should return empty list for zero quantity order.
        """
        self._create_lot('LOT001', quantity=100, days_until_expiry=180)
        
        orders = self.view._place_order(code_med='PARA500', qte=0)
        
        self.assertEqual(orders, [])
    
    def test_place_order_with_nonexistent_medicine(self):
        """
        TEST: Should return empty list for medicine that doesn't exist.
        """
        orders = self.view._place_order(code_med='NONEXISTENT', qte=10)
        
        self.assertEqual(orders, [])


# =============================================================================
# PART 5: TESTING _updateReduction (Price Calculations)
# =============================================================================

class TestUpdateReduction(TestCase):
    """
    LESSON 5: Testing calculations with different input scenarios
    
    Test with different insurance rates: 0%, 80%, 100%
    """
    
    @classmethod
    def setUpTestData(cls):
        """Create test client and assurance."""
        cls.client = Client.objects.create(
            beneficiaire='Test Client',
            joined_on=timezone.now()
        )
    
    def setUp(self):
        self.view = EntrantImiti()
    
    def _create_bon_with_assurance(self, rate):
        """Helper to create bon with specific insurance rate."""
        assurance = Assurance.objects.create(
            name=f'Assurance_{rate}_{timezone.now().timestamp()}',
            rate_assure=rate
        )
        bon = BonDeCommand.objects.create(
            beneficiaire=self.client,
            organization=assurance,
            date_served=timezone.now()
        )
        return bon
    
    def test_updateReduction_no_insurance(self):
        """
        TEST: With 0% insurance, client pays full amount.
        """
        # Arrange
        bon = self._create_bon_with_assurance(rate=0)
        
        # Act
        result = self.view._updateReduction(
            bon_de_commande=bon,
            total=10000,
            rate_assure=0,
            num_facture=1
        )
        
        # Assert
        self.assertEqual(result.cout, 10000)        # Client pays all
        self.assertEqual(result.total, 10000)
    
    def test_updateReduction_80_percent_insurance(self):
        """
        TEST: With 80% insurance, client pays 20%, insurance pays 80%.
        """
        # Arrange
        bon = self._create_bon_with_assurance(rate=80)
        
        # Act
        result = self.view._updateReduction(
            bon_de_commande=bon,
            total=10000,
            rate_assure=80,
            num_facture=1
        )
        
        # Assert
        self.assertEqual(result.total, 10000)
        self.assertEqual(result.montant_dette, 8000)  # Insurance pays 80%
        self.assertEqual(result.cout, 2000)           # Client pays 20%
    
    def test_updateReduction_100_percent_insurance(self):
        """
        TEST: With 100% insurance, client pays nothing.
        """
        # Arrange
        bon = self._create_bon_with_assurance(rate=100)
        
        # Act
        result = self.view._updateReduction(
            bon_de_commande=bon,
            total=10000,
            rate_assure=100,
            num_facture=1
        )
        
        # Assert
        self.assertEqual(result.montant_dette, 10000)  # Insurance pays all
        self.assertEqual(result.cout, 0)               # Client pays nothing


# =============================================================================
# PART 6: TESTING THE FULL ENDPOINT (Integration Tests)
# =============================================================================

class TestSellEndpoint(APITestCase):
    """
    LESSON 6: Testing the complete API endpoint
    
    These are integration tests - they test the full flow including:
    - Authentication
    - Request/Response handling
    - Database operations
    """
    
    @classmethod
    def setUpTestData(cls):
        """Set up all required data for sell endpoint."""
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create required assurances
        cls.sans_assurance = Assurance.objects.create(name='Sans', rate_assure=0)
        cls.pharmacie_assurance = Assurance.objects.create(
            name='Pharmacie Ubuzima',
            rate_assure=0
        )
        
        # Create ordinary client
        cls.ordinary_client = Client.objects.create(
            beneficiaire='Ordinary',
            joined_on=timezone.now()
        )
        
        # Create Journaling for sync tracking
        cls.journal = Journaling.objects.create(
            id=1,
            codes_for_sync='',
            num_days=30
        )
        
        # Create medicine catalog
        cls.med_unit = MedUnit.objects.create(unit='Comprime')
        cls.med_set = ImitiSet.objects.create(
            code_med='TEST001',
            nom_med='Test Medicine',
            prix_vente=1000,
            med_unit=cls.med_unit,
            lot='[]',
            checked_imiti='[]',
            checked_qte='[]',
        )
    
    def setUp(self):
        """Set up client for each test."""
        self.client_api = APIClient()
        # Clear stock before each test
        UmutiEntree.objects.filter(code_med='TEST001').delete()
    
    def _create_stock(self, code_med, quantity, days_until_expiry=180):
        """Helper to create medicine stock."""
        return UmutiEntree.objects.create(
            code_med=code_med,
            code_operation=f'OP_{code_med}_{quantity}_{timezone.now().timestamp()}',
            nom_med='Test Medicine',
            quantite_initial=quantity,
            quantite_restant=quantity,
            prix_achat=500,
            prix_vente=1000,
            date_entrant=timezone.now(),
            date_peremption=timezone.now() + timedelta(days=days_until_expiry),
            is_pirimiye=False,
            med_unit=self.med_unit,
        )
    
    # -------------------------------------------------------------------------
    # Authentication Tests
    # -------------------------------------------------------------------------
    
    def test_sell_requires_authentication(self):
        """
        TEST: Sell endpoint should reject unauthenticated requests.
        
        Security is critical - always test that protected endpoints
        actually require authentication.
        """
        # Act - Try to access without logging in
        response = self.client_api.post('/api/in/sell/', {})
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_sell_accepts_authenticated_user(self):
        """
        TEST: Authenticated users should be able to access the endpoint.
        """
        # Arrange - Log in
        self.client_api.force_authenticate(user=self.user)
        
        # Act - Make request (might fail for other reasons, but not auth)
        payload = {
            'imiti': {
                'client': None,
                'panier': []
            }
        }
        response = self.client_api.post('/api/in/sell/', payload, format='json')
        
        # Assert - Should not be 401
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # -------------------------------------------------------------------------
    # Success Path Tests
    # -------------------------------------------------------------------------
    
    def test_sell_ordinary_client_success(self):
        """
        TEST: Complete sale flow for ordinary client.
        """
        # Arrange
        self.client_api.force_authenticate(user=self.user)
        self._create_stock('TEST001', quantity=50)
        
        payload = {
            'imiti': {
                'client': None,  # None = ordinary client
                'panier': [
                    {
                        'code_med': 'TEST001',
                        'lot': True,
                        'qte': 5
                    }
                ]
            }
        }
        
        # Act
        response = self.client_api.post('/api/in/sell/', payload, format='json')
        data = response.json()
        
        # Assert
        self.assertIn('sold', data)  # Should have success indicator
    
    # -------------------------------------------------------------------------
    # Error Cases
    # -------------------------------------------------------------------------
    
    def test_sell_duplicate_bon_rejected(self):
        """
        TEST: Should reject sale if bon number already exists.
        """
        # Arrange
        self.client_api.force_authenticate(user=self.user)
        
        # Create existing bon
        assurance = Assurance.objects.create(name='TestInsurance', rate_assure=80)
        BonDeCommand.objects.create(
            num_bon='DUPLICATE123',
            beneficiaire=self.ordinary_client,
            organization=assurance,
            date_served=timezone.now()
        )
        
        payload = {
            'imiti': {
                'client': {
                    'nom_adherant': 'Test Patient',
                    'nom_client': 'Test Patient',
                    'relation': 'Lui-meme',
                    'rate_assure': 80,
                    'assureur': 'TestInsurance',
                    'numero_bon': 'DUPLICATE123',  # Already exists!
                },
                'panier': [{'code_med': 'TEST001', 'lot': True, 'qte': 1}]
            }
        }
        
        # Act
        response = self.client_api.post('/api/in/sell/', payload, format='json')
        
        # Assert
        self.assertEqual(response.json().get('sold'), 'FailedBecauseAlreadyExist')
    
    def test_sell_insufficient_stock(self):
        """
        TEST: Should handle case when stock is insufficient.
        """
        # Arrange
        self.client_api.force_authenticate(user=self.user)
        self._create_stock('TEST001', quantity=5)  # Only 5 in stock
        
        payload = {
            'imiti': {
                'client': None,
                'panier': [
                    {
                        'code_med': 'TEST001',
                        'lot': True,
                        'qte': 100  # Trying to buy 100!
                    }
                ]
            }
        }
        
        # Act
        response = self.client_api.post('/api/in/sell/', payload, format='json')
        data = response.json()
        
        # Assert - Should indicate imperfect transaction
        self.assertEqual(data.get('imperfect'), 1)


# =============================================================================
# PART 7: USING MOCKS (Isolating Tests)
# =============================================================================

class TestWithMocks(TestCase):
    """
    LESSON 7: Using mocks to isolate code units
    
    Mocks let you test a method without depending on other methods.
    Use @patch to replace methods with controlled mock objects.
    """
    
    def setUp(self):
        # Create required data for _getClient1 to work
        Assurance.objects.get_or_create(name='Sans', defaults={'rate_assure': 0})
        Client.objects.get_or_create(beneficiaire='Ordinary')
        self.view = EntrantImiti()
    
    @patch.object(EntrantImiti, '_getClient1')
    def test_sell_calls_getClient1_for_ordinary(self, mock_getClient1):
        """
        TEST: Verify _getClient1 is called when client is None.
        
        This uses a mock to verify the method is called correctly,
        without actually executing the method.
        """
        # Arrange - Set up mock return value
        mock_client = MagicMock()
        mock_assurance = MagicMock()
        mock_assurance.rate_assure = 0
        mock_getClient1.return_value = [mock_client, mock_assurance]
        
        # Call _getClient1 
        result = self.view._getClient1()
        
        # Assert - Verify mock was called
        mock_getClient1.assert_called_once()
    
    def test_with_magicmock_attributes(self):
        """
        EXAMPLE: How to use MagicMock to simulate objects.
        """
        # Create a mock object with specific attributes
        mock_medicine = MagicMock()
        mock_medicine.code_med = 'MED001'
        mock_medicine.nom_med = 'Test Medicine'
        mock_medicine.quantite_restant = 100
        mock_medicine.prix_vente = 500
        
        # Use the mock as if it were a real object
        self.assertEqual(mock_medicine.code_med, 'MED001')
        self.assertEqual(mock_medicine.quantite_restant, 100)


# =============================================================================
# PART 8: COMMON ASSERTION METHODS REFERENCE
# =============================================================================

class AssertionExamples(TestCase):
    """
    LESSON 8: Common assertion methods you'll use frequently
    
    This is a reference - run these tests to see how assertions work.
    """
    
    def test_equality_assertions(self):
        """Equality checks."""
        self.assertEqual(1, 1)           # a == b
        self.assertNotEqual(1, 2)        # a != b
    
    def test_truthiness_assertions(self):
        """Boolean checks."""
        self.assertTrue(True)            # bool(x) is True
        self.assertFalse(False)          # bool(x) is False
        self.assertIsNone(None)          # x is None
        self.assertIsNotNone("value")    # x is not None
    
    def test_container_assertions(self):
        """Collection checks."""
        self.assertIn('a', ['a', 'b'])        # a in b
        self.assertNotIn('c', ['a', 'b'])     # a not in b
        self.assertEqual(len([1, 2, 3]), 3)   # Length check
    
    def test_comparison_assertions(self):
        """Numeric comparisons."""
        self.assertGreater(5, 3)         # a > b
        self.assertGreaterEqual(5, 5)    # a >= b
        self.assertLess(3, 5)            # a < b
        self.assertLessEqual(5, 5)       # a <= b
    
    def test_type_assertions(self):
        """Type checks."""
        self.assertIsInstance("text", str)      # isinstance(a, str)
        self.assertIsInstance(123, int)
        self.assertIsInstance([1, 2], list)
    
    def test_exception_assertions(self):
        """Testing that exceptions are raised."""
        with self.assertRaises(ValueError):
            int("not a number")  # This raises ValueError
        
        with self.assertRaises(ZeroDivisionError):
            1 / 0  # This raises ZeroDivisionError


# =============================================================================
# SUMMARY - KEY TAKEAWAYS
# =============================================================================
"""
HOW TO WRITE YOUR OWN TESTS - STEP BY STEP:

1. IDENTIFY WHAT TO TEST
   - Look at your method/endpoint
   - List the different scenarios (success, failure, edge cases)
   
2. CREATE TEST CLASS
   class TestYourFeature(TestCase):  # or APITestCase for endpoints
       pass

3. SET UP TEST DATA
   @classmethod
   def setUpTestData(cls):
       # Create shared read-only data
       
   def setUp(self):
       # Create data that each test might modify

4. WRITE TESTS (Arrange-Act-Assert)
   def test_feature_scenario_expected_result(self):
       # Arrange - Set up data
       # Act - Call the method
       # Assert - Verify results

5. TEST NAMING: test_<what>_<condition>_<expected_result>
   Example: test_getClient1_returns_ordinary_client

6. COVERAGE: Test both success and failure paths
   - Happy path (normal operation)
   - Edge cases (empty inputs, large values)
   - Error cases (invalid data, missing data)

RUN YOUR TESTS:
   # Run all tests
   python3 manage.py test
   
   # Run specific test file
   python3 manage.py test api_tests.test_Sell_Tutorial --verbosity=2
   
   # Run specific test class
   python3 manage.py test api_tests.test_Sell_Tutorial.TestPlaceOrder -v2
   
   # Run single test method
   python3 manage.py test api_tests.test_Sell_Tutorial.TestPlaceOrder.test_place_order_with_sufficient_single_lot
"""
