from django import forms
from django.core.exceptions import ValidationError
from .models import Project, Certificate
from decimal import Decimal


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name_of_contractor', 'contract_no', 'vote_no', 'tender_sum']
        widgets = {
            'name_of_contractor': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter contractor name'
            }),
            'contract_no': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter contract number'
            }),
            'vote_no': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter vote number'
            }),
            'tender_sum': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Enter tender sum'
            })
        }

    def clean_contract_no(self):
        contract_no = self.cleaned_data['contract_no']
        if Project.objects.filter(contract_no=contract_no).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError("A project with this contract number already exists.")
        return contract_no


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['currency', 'current_claim_excl_vat', 'previous_payment_excl_vat']
        widgets = {
            'currency': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'current_claim_excl_vat': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Enter current claim amount'
            }),
            'previous_payment_excl_vat': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter previous payment amount'
            })
        }

    def clean_current_claim_excl_vat(self):
        amount = self.cleaned_data['current_claim_excl_vat']
        if amount <= 0:
            raise ValidationError("Current claim amount must be greater than zero.")
        return amount
