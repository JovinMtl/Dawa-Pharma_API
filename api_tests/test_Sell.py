"""
Critical Unit Tests for the Sell Endpoint in EntrantImiti ViewSet.

These tests cover:
1. Authentication requirements
2. Different client types (ordinary, special, insured)
3. Inventory validation (stock availability, expired meds)
4. BonDeCommand creation and duplicate prevention
5. Order placement and quantity distribution
6. Edge cases and error handling
"""

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from api.views import EntrantImiti
from pharma.models import (
    UmutiEntree, ImitiSet, UmutiSold, BonDeCommand, 
    Assurance, Client, Journaling, MedUnit
)


class SellEndpointTestCase(APITestCase):
    """Test cases for the sell endpoint in EntrantImiti ViewSet"""

    def setUp(self):
        """Set up test fixtures"""
        self.client_api = APIClient()
        self.instance = EntrantImiti()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=False
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass123',
            is_staff=True
        )
        
        # Create MedUnit
        self.med_unit = MedUnit.objects.create(
            unit='Plaquette',
            level=1
        )
        
        # Create Assurance objects
        self.assurance_sans = Assurance.objects.create(
            name='Sans',
            rate_assure=0
        )
        
        self.assurance_pharma = Assurance.objects.create(
            name='Pharmacie Ubuzima',
            rate_assure=0
        )
        
        self.assurance_mutuelle = Assurance.objects.create(
            name='Mutuelle',
            rate_assure=80
        )
        
        # Create Client objects
        self.ordinary_client = Client.objects.create(
            beneficiaire='Ordinary',
            nom_adherant='Ordinary Client'
        )
        
        self.special_client = Client.objects.create(
            beneficiaire='SpecialClient',
            nom_adherant='Special Client',
            phone_number=79123456
        )
        
        self.insured_client = Client.objects.create(
            beneficiaire='InsuredBeneficiary',
            nom_adherant='InsuredAdherant',
            numero_carte=12345,
            employeur='TestEmployer',
            relation='Lui-même'
        )
        
        # Create Journaling for sync tracking
        self.journal = Journaling.objects.create(
            codes_for_sync='[]'
        )
        
        # Create ImitiSet (medicine reference)
        self.imiti_set = ImitiSet.objects.create(
            code_med='AMX01',
            nom_med='Amoxicillin 500mg',
            classe_med='Antibiotics',
            sous_classe_med='Penicillins',
            forme='Capsule',
            prix_achat=1000,
            prix_vente=1500,
            quantite_restant=100,
            lot='[]',
            checked_imiti='[]',
            checked_qte='[]',
            med_unit=self.med_unit
        )
        
        # Create UmutiEntree (stock entry) with future expiration
        self.umuti_entree = UmutiEntree.objects.create(
            code_med='AMX01',
            nom_med='Amoxicillin 500mg',
            code_operation='OP12345',
            prix_achat=1000,
            prix_vente=1500,
            quantite_initial=50,
            quantite_restant=50,
            date_peremption=timezone.now().date() + timedelta(days=365),
            med_unit=self.med_unit
        )
        
        # Create expired UmutiEntree for testing
        self.expired_umuti = UmutiEntree.objects.create(
            code_med='EXP01',
            nom_med='Expired Medicine',
            code_operation='OPEXP01',
            prix_achat=500,
            prix_vente=800,
            quantite_initial=20,
            quantite_restant=20,
            date_peremption=timezone.now().date() - timedelta(days=30),
            med_unit=self.med_unit
        )

    # ==================== AUTHENTICATION TESTS ====================
    
    def test_sell_requires_authentication(self):
        """Test that sell endpoint requires authentication"""
        # Not logged in
        response = self.client_api.post('/api/in/sell/', {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_sell_with_authenticated_user(self):
        """Test that authenticated user can access sell endpoint"""
        self.client_api.force_authenticate(user=self.user)
        
        payload = {
            'imiti': {
                'panier': [],
                'client': None
            }
        }
        response = self.client_api.post('/api/in/sell/', payload, format='json')
        # Should not return 401/403 - even if sale fails, auth passed
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ==================== CLIENT TYPE TESTS ====================
    
    def test_getClient1_ordinary_client(self):
        """Test _getClient1 returns ordinary client and Sans assurance"""
        client_obj, assurance_obj = self.instance._getClient1()
        
        self.assertIsNotNone(assurance_obj)
        self.assertEqual(assurance_obj.name, 'Sans')
        self.assertEqual(assurance_obj.rate_assure, 0)
    
    def test_getClient2_special_client_new(self):
        """Test _getClient2 creates new special client when not exists"""
        data_client = {
            'nom_client': 'NewSpecialClient',
            'numero_tel': 79999999,
            'categorie': 'tv'
        }
        
        client_obj, assurance_obj = self.instance._getClient2(data_client)
        
        self.assertIsNotNone(client_obj)
        self.assertEqual(client_obj.phone_number, 79999999)
        self.assertEqual(assurance_obj.name, 'Pharmacie Ubuzima')
    
    def test_getClient2_special_client_existing(self):
        """Test _getClient2 returns existing client by phone number"""
        data_client = {
            'nom_client': 'SpecialClient',
            'numero_tel': 79123456,
            'categorie': 'tv'
        }
        
        client_obj, assurance_obj = self.instance._getClient2(data_client)
        
        self.assertIsNotNone(client_obj)
        self.assertEqual(client_obj.id, self.special_client.id)
    
    def test_getClient3_insured_client_new(self):
        """Test _getClient3 creates new insured client"""
        data_client = {
            'nom_adherant': 'NewAdherant',
            'nom_client': 'NewBeneficiary',
            'relation': 'Conjoint',
            'rate_assure': 80,
            'assureur': 'NewAssurance',
            'employeur': 'TestCompany',
            'numero_carte': 54321,
            'categorie': 'au'
        }
        
        client_obj, assurance_obj = self.instance._getClient3(data_client)
        
        self.assertIsNotNone(client_obj)
        self.assertEqual(client_obj.beneficiaire, 'NewBeneficiary')
        self.assertIsNotNone(assurance_obj)
        self.assertEqual(assurance_obj.name, 'NewAssurance')
        self.assertEqual(assurance_obj.rate_assure, 80)
    
    def test_getClient3_insured_self_beneficiary(self):
        """Test _getClient3 when relation is 'Lui-même' uses nom_adherant as beneficiary"""
        data_client = {
            'nom_adherant': 'SelfAdherant',
            'nom_client': 'ShouldNotBeUsed',
            'relation': 'Lui-même',
            'rate_assure': 70,
            'assureur': 'TestAssurance',
            'employeur': 'TestCompany',
            'numero_carte': 99999,
            'categorie': 'au'
        }
        
        client_obj, assurance_obj = self.instance._getClient3(data_client)
        
        # When relation is 'Lui-même', beneficiaire should be nom_adherant
        self.assertEqual(client_obj.beneficiaire, 'SelfAdherant')

    # ==================== BON DE COMMANDE TESTS ====================
    
    def test_checkNumBon_existing(self):
        """Test _checkNumBon returns True for existing bon number"""
        # Create a BonDeCommand
        bon = BonDeCommand.objects.create(
            beneficiaire=self.ordinary_client,
            organization=self.assurance_sans,
            meds='',
            num_bon='BON12345'
        )
        
        result = self.instance._checkNumBon('BON12345')
        self.assertTrue(result)
    
    def test_checkNumBon_non_existing(self):
        """Test _checkNumBon returns False for non-existing bon number"""
        result = self.instance._checkNumBon('NONEXISTENT')
        self.assertFalse(result)
    
    def test_sell_fails_with_duplicate_bon_number(self):
        """Test that sell fails when bon number already exists (for insured clients)"""
        self.client_api.force_authenticate(user=self.user)
        
        # Create existing bon
        BonDeCommand.objects.create(
            beneficiaire=self.insured_client,
            organization=self.assurance_mutuelle,
            meds='',
            num_bon='DUPLICATE123'
        )
        
        payload = {
            'imiti': {
                'panier': [{'code_med': 'AMX01', 'lot': [], 'qte': 5}],
                'client': {
                    'nom_adherant': 'TestAdherant',
                    'nom_client': 'TestBeneficiary',
                    'relation': 'Lui-même',
                    'rate_assure': 80,
                    'assureur': 'Mutuelle',
                    'numero_bon': 'DUPLICATE123',
                    'categorie': 'au'
                }
            }
        }
        
        response = self.client_api.post('/api/in/sell/', payload, format='json')
        
        self.assertEqual(response.json().get('sold'), 'FailedBecauseAlreadyExist')

    # ==================== PLACE ORDER TESTS ====================
    
    def test_place_order_sufficient_stock(self):
        """Test _place_order with sufficient stock in single lot"""
        orders = self.instance._place_order(code_med='AMX01', qte=10)
        
        self.assertIsNotNone(orders)
        self.assertIsInstance(orders, list)
        self.assertGreater(len(orders), 0)
        
        # Check total quantity matches requested
        total_qte = sum(order[2] for order in orders)
        self.assertEqual(total_qte, 10)
    
    def test_place_order_zero_quantity(self):
        """Test _place_order with zero quantity returns empty list"""
        orders = self.instance._place_order(code_med='AMX01', qte=0)
        
        self.assertEqual(orders, [])
    
    def test_place_order_insufficient_stock(self):
        """Test _place_order with insufficient stock returns empty list"""
        # Request more than available
        orders = self.instance._place_order(code_med='AMX01', qte=1000)
        
        self.assertEqual(orders, [])
    
    def test_place_order_excludes_expired(self):
        """Test _place_order excludes expired medicines"""
        # Create ImitiSet for expired med
        ImitiSet.objects.create(
            code_med='EXP01',
            nom_med='Expired Medicine',
            prix_achat=500,
            prix_vente=800,
            quantite_restant=20,
            lot='[]',
            checked_imiti='[]',
            checked_qte='[]',
            med_unit=self.med_unit
        )
        
        orders = self.instance._place_order(code_med='EXP01', qte=5)
        
        # Should return empty list as all stock is expired
        self.assertEqual(orders, [])
    
    def test_place_order_multiple_lots(self):
        """Test _place_order distributes across multiple lots"""
        # Create second lot entry
        UmutiEntree.objects.create(
            code_med='AMX01',
            nom_med='Amoxicillin 500mg',
            code_operation='OP12346',
            prix_achat=1000,
            prix_vente=1500,
            quantite_initial=30,
            quantite_restant=30,
            date_peremption=timezone.now().date() + timedelta(days=180),  # Earlier expiry
            med_unit=self.med_unit
        )
        
        # Request 60 (more than single lot has)
        orders = self.instance._place_order(code_med='AMX01', qte=60)
        
        self.assertIsNotNone(orders)
        # Should use both lots
        self.assertGreaterEqual(len(orders), 1)
        
        total_qte = sum(order[2] for order in orders)
        self.assertEqual(total_qte, 60)

    # ==================== UPDATE REDUCTION TESTS ====================
    
    def test_updateReduction_with_insurance(self):
        """Test _updateReduction calculates correctly with insurance rate"""
        bon = BonDeCommand.objects.create(
            beneficiaire=self.insured_client,
            organization=self.assurance_mutuelle,
            meds='',
            num_bon='TEST123'
        )
        
        # Total 10000, insurance covers 80%
        result = self.instance._updateReduction(
            bon_de_commande=bon,
            total=10000,
            rate_assure=80,
            num_facture=1
        )
        
        self.assertEqual(result.total, 10000)
        self.assertEqual(result.assu_rate, 80)
        # Patient pays 20% = 2000
        self.assertEqual(result.cout, 2000)
        # Insurance pays 80% = 8000
        self.assertEqual(result.montant_dette, 8000)
    
    def test_updateReduction_without_insurance(self):
        """Test _updateReduction with no insurance (rate_assure=0)"""
        bon = BonDeCommand.objects.create(
            beneficiaire=self.ordinary_client,
            organization=self.assurance_sans,
            meds='',
            num_bon='TEST456'
        )
        
        result = self.instance._updateReduction(
            bon_de_commande=bon,
            total=5000,
            rate_assure=0,
            num_facture=2
        )
        
        self.assertEqual(result.total, 5000)
        self.assertEqual(result.cout, 5000)  # Patient pays full amount

    # ==================== ADD FOR SYNC TESTS ====================
    
    def test_add_for_sync_new_code(self):
        """Test _add_for_sync adds new code to list"""
        codes = ['ABC01', 'DEF02']
        result = self.instance._add_for_sync(codes_for_sync=codes, code_med='GHI03')
        
        self.assertIn('GHI03', result)
        self.assertEqual(len(result), 3)
    
    def test_add_for_sync_existing_code(self):
        """Test _add_for_sync does not duplicate existing code"""
        codes = ['ABC01', 'DEF02']
        result = self.instance._add_for_sync(codes_for_sync=codes, code_med='ABC01')
        
        self.assertEqual(len(result), 2)  # No change in length

    # ==================== COMPLETE BON TESTS ====================
    
    def test_completeBon_adds_code(self):
        """Test _completeBon appends code_operation to meds field"""
        bon = BonDeCommand.objects.create(
            beneficiaire=self.ordinary_client,
            organization=self.assurance_sans,
            meds='',
            num_bon='COMPTEST'
        )
        
        result = self.instance._completeBon(
            bon_de_commande=bon,
            code_operation='SOLD123'
        )
        
        self.assertIn('SOLD123', result.meds)

    # ==================== IMITI SELL TESTS ====================
    
    def test_imitiSell_creates_record(self):
        """Test _imitiSell creates UmutiSold record and updates stock"""
        bon = BonDeCommand.objects.create(
            beneficiaire=self.ordinary_client,
            organization=self.assurance_sans,
            meds='',
            num_bon='SELLTEST'
        )
        
        initial_qty = self.umuti_entree.quantite_restant
        
        code_operation = self.instance._imitiSell(
            umuti=self.umuti_entree,
            qte=5,
            operator=self.user,
            reference_umuti=self.imiti_set,
            bon_de_commande=bon
        )
        
        # Refresh from database
        self.umuti_entree.refresh_from_db()
        
        # Check stock was reduced
        self.assertEqual(self.umuti_entree.quantite_restant, initial_qty - 5)
        
        # Check UmutiSold record was created
        sold = UmutiSold.objects.filter(code_operation=code_operation).first()
        self.assertIsNotNone(sold)
        self.assertEqual(sold.quantity, 5)
        self.assertEqual(sold.code_med, 'AMX01')
    
    def test_imitiSell_records_correct_prices(self):
        """Test _imitiSell records correct pricing from ImitiSet"""
        bon = BonDeCommand.objects.create(
            beneficiaire=self.ordinary_client,
            organization=self.assurance_sans,
            meds='',
            num_bon='PRICETEST'
        )
        
        code_operation = self.instance._imitiSell(
            umuti=self.umuti_entree,
            qte=2,
            operator=self.user,
            reference_umuti=self.imiti_set,
            bon_de_commande=bon
        )
        
        sold = UmutiSold.objects.filter(code_operation=code_operation).first()
        
        self.assertEqual(sold.prix_achat, self.imiti_set.prix_achat)
        self.assertEqual(sold.prix_vente, self.imiti_set.prix_vente)
        self.assertEqual(sold.difference, self.imiti_set.prix_vente - self.imiti_set.prix_achat)

    # ==================== INTEGRATION TESTS ====================
    
    def test_sell_ordinary_client_success(self):
        """Test complete sell flow for ordinary client"""
        self.client_api.force_authenticate(user=self.user)
        
        payload = {
            'imiti': {
                'panier': [
                    {'code_med': 'AMX01', 'lot': [{'code_operation': 'OP12345', 'qte': 5}], 'qte': 5}
                ],
                'client': None  # Ordinary client
            }
        }
        
        response = self.client_api.post('/api/in/sell/', payload, format='json')
        data = response.json()
        
        # Should return success with sold info
        self.assertIn('sold', data)
    
    def test_sell_empty_panier(self):
        """Test sell with empty panier"""
        self.client_api.force_authenticate(user=self.user)
        
        payload = {
            'imiti': {
                'panier': [],
                'client': None
            }
        }
        
        response = self.client_api.post('/api/in/sell/', payload, format='json')
        # Should handle gracefully - not crash

    def test_sell_nonexistent_medicine(self):
        """Test sell with non-existent medicine code"""
        self.client_api.force_authenticate(user=self.user)
        
        payload = {
            'imiti': {
                'panier': [
                    {'code_med': 'INVALID999', 'lot': [], 'qte': 5}
                ],
                'client': None
            }
        }
        
        response = self.client_api.post('/api/in/sell/', payload, format='json')
        data = response.json()
        
        # Should indicate imperfect transaction
        self.assertEqual(data.get('imperfect'), 1)


class SellEdgeCasesTestCase(APITestCase):
    """Edge cases and boundary condition tests for sell endpoint"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client_api = APIClient()
        self.instance = EntrantImiti()
        
        self.user = User.objects.create_user(
            username='edgeuser',
            password='edgepass123'
        )
        
        self.med_unit = MedUnit.objects.create(unit='Plaquette', level=1)
        
        self.assurance_sans = Assurance.objects.create(name='Sans', rate_assure=0)
        
        self.ordinary_client = Client.objects.create(
            beneficiaire='Ordinary',
            nom_adherant='Ordinary'
        )
        
        self.journal = Journaling.objects.create(codes_for_sync='[]')
    
    def test_sell_decimal_quantity(self):
        """Test selling decimal quantities (e.g., 0.5 tablets)"""
        # Create medicine that allows decimal selling
        ImitiSet.objects.create(
            code_med='DEC01',
            nom_med='Decimal Med',
            prix_achat=100,
            prix_vente=150,
            quantite_restant=10,
            is_decimal=True,
            lot='[]',
            checked_imiti='[]',
            checked_qte='[]',
            med_unit=self.med_unit
        )
        
        UmutiEntree.objects.create(
            code_med='DEC01',
            nom_med='Decimal Med',
            code_operation='OPDEC01',
            prix_achat=100,
            prix_vente=150,
            quantite_initial=10,
            quantite_restant=10,
            date_peremption=timezone.now().date() + timedelta(days=365),
            med_unit=self.med_unit
        )
        
        orders = self.instance._place_order(code_med='DEC01', qte=2.5)
        
        # Should handle decimal quantities
        self.assertIsNotNone(orders)
    
    def test_sell_exact_stock_amount(self):
        """Test selling exactly what's in stock"""
        ImitiSet.objects.create(
            code_med='EXA01',
            nom_med='Exact Med',
            prix_achat=100,
            prix_vente=150,
            quantite_restant=5,
            lot='[]',
            checked_imiti='[]',
            checked_qte='[]',
            med_unit=self.med_unit
        )
        
        UmutiEntree.objects.create(
            code_med='EXA01',
            nom_med='Exact Med',
            code_operation='OPEXA01',
            prix_achat=100,
            prix_vente=150,
            quantite_initial=5,
            quantite_restant=5,
            date_peremption=timezone.now().date() + timedelta(days=365),
            med_unit=self.med_unit
        )
        
        orders = self.instance._place_order(code_med='EXA01', qte=5)
        
        self.assertIsNotNone(orders)
        total = sum(o[2] for o in orders)
        self.assertEqual(total, 5)
    
    def test_insurance_rate_100_percent(self):
        """Test insurance with 100% coverage"""
        assurance_full = Assurance.objects.create(
            name='FullCoverage',
            rate_assure=100
        )
        
        client = Client.objects.create(
            beneficiaire='FullCoverageClient',
            nom_adherant='Full Coverage'
        )
        
        bon = BonDeCommand.objects.create(
            beneficiaire=client,
            organization=assurance_full,
            meds='',
            num_bon='FULL100'
        )
        
        result = self.instance._updateReduction(
            bon_de_commande=bon,
            total=10000,
            rate_assure=100,
            num_facture=1
        )
        
        # Patient pays 0%
        self.assertEqual(result.cout, 0)
        # Insurance pays 100%
        self.assertEqual(result.montant_dette, 10000)


class SellConcurrencyTestCase(APITestCase):
    """Tests for concurrent sell operations"""
    
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username='concuser', password='concpass')
        self.med_unit = MedUnit.objects.create(unit='Plaquette', level=1)
        self.assurance = Assurance.objects.create(name='Sans', rate_assure=0)
        Client.objects.create(beneficiaire='Ordinary', nom_adherant='Ordinary')
        Journaling.objects.create(codes_for_sync='[]')
    
    def test_stock_validation_before_sale(self):
        """Test that stock is validated at sale time"""
        instance = EntrantImiti()
        
        ImitiSet.objects.create(
            code_med='CON01',
            nom_med='Concurrent Med',
            prix_achat=100,
            prix_vente=150,
            quantite_restant=10,
            lot='[]',
            checked_imiti='[]',
            checked_qte='[]',
            med_unit=self.med_unit
        )
        
        umuti = UmutiEntree.objects.create(
            code_med='CON01',
            nom_med='Concurrent Med',
            code_operation='OPCON01',
            prix_achat=100,
            prix_vente=150,
            quantite_initial=10,
            quantite_restant=10,
            date_peremption=timezone.now().date() + timedelta(days=365),
            med_unit=self.med_unit
        )
        
        # First order should succeed
        orders1 = instance._place_order(code_med='CON01', qte=8)
        self.assertEqual(len(orders1), 1)
        
        # Simulate stock reduction
        umuti.quantite_restant = 2
        umuti.save()
        
        # Second order for 5 should fail (only 2 left)
        orders2 = instance._place_order(code_med='CON01', qte=5)
        self.assertEqual(orders2, [])
