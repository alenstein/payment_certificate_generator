from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Project, Certificate, Calculations
from .forms import ProjectForm, CertificateForm


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name_of_contractor='Test Contractor',
            contract_no='TEST-001',
            vote_no='V-001',
            tender_sum=Decimal('100000.00'),
            owner=self.user
        )

    def test_project_creation(self):
        self.assertEqual(self.project.name_of_contractor, 'Test Contractor')
        self.assertEqual(self.project.owner, self.user)
        self.assertEqual(str(self.project), 'Test Contractor - TEST-001')

    def test_project_unique_contract_no(self):
        with self.assertRaises(Exception):
            Project.objects.create(
                name_of_contractor='Another Contractor',
                contract_no='TEST-001',  # Duplicate contract number
                vote_no='V-002',
                tender_sum=Decimal('50000.00'),
                owner=self.user
            )

    def test_certificate_creation_and_calculations(self):
        certificate = Certificate.objects.create(
            project=self.project,
            currency='USD',
            current_claim_excl_vat=Decimal('10000.00'),
            previous_payment_excl_vat=Decimal('0.00')
        )
        
        # Check VAT calculation
        self.assertEqual(certificate.vat_value, Decimal('1500.00'))  # 15% of 10000
        
        # Check calculations were created
        self.assertTrue(hasattr(certificate, 'calculations'))
        calculations = certificate.calculations
        
        # Check calculation values
        self.assertEqual(calculations.retention, Decimal('1000.00'))  # 10% of 10000
        self.assertEqual(calculations.value_of_workdone_incl_vat, Decimal('11500.00'))  # 10000 + 1500
        self.assertEqual(calculations.total_amount_payable, Decimal('10500.00'))  # 10000 + 1500 - 1000


class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_project_form_valid(self):
        form_data = {
            'name_of_contractor': 'Test Contractor',
            'contract_no': 'TEST-001',
            'vote_no': 'V-001',
            'tender_sum': '100000.00'
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_project_form_invalid_tender_sum(self):
        form_data = {
            'name_of_contractor': 'Test Contractor',
            'contract_no': 'TEST-001',
            'vote_no': 'V-001',
            'tender_sum': '0.00'  # Invalid: must be > 0
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_certificate_form_valid(self):
        form_data = {
            'currency': 'USD',
            'current_claim_excl_vat': '10000.00',
            'previous_payment_excl_vat': '0.00'
        }
        form = CertificateForm(data=form_data)
        self.assertTrue(form.is_valid())


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name_of_contractor='Test Contractor',
            contract_no='TEST-001',
            vote_no='V-001',
            tender_sum=Decimal('100000.00'),
            owner=self.user
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_project_list_requires_login(self):
        response = self.client.get(reverse('project_list'))
        self.assertRedirects(response, '/login/?next=/projects/')

    def test_project_list_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Contractor')

    def test_project_detail_permission(self):
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Login as other user
        self.client.login(username='otheruser', password='otherpass123')
        
        # Try to access project owned by different user
        response = self.client.get(reverse('project_detail', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_project_create(self):
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'name_of_contractor': 'New Contractor',
            'contract_no': 'NEW-001',
            'vote_no': 'V-NEW-001',
            'tender_sum': '50000.00'
        }
        
        response = self.client.post(reverse('project_create'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check project was created
        self.assertTrue(Project.objects.filter(contract_no='NEW-001').exists())

    def test_certificate_create(self):
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'currency': 'USD',
            'current_claim_excl_vat': '10000.00',
            'previous_payment_excl_vat': '0.00'
        }
        
        response = self.client.post(
            reverse('certificate_create', kwargs={'project_pk': self.project.pk}),
            data=form_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check certificate was created
        self.assertTrue(Certificate.objects.filter(project=self.project).exists())


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_registration(self):
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('login'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
