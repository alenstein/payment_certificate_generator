from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.urls import reverse


class Project(models.Model):
    name_of_contractor = models.CharField(max_length=200)
    contract_no = models.CharField(max_length=100, unique=True)
    vote_no = models.CharField(max_length=100)
    tender_sum = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name_of_contractor} - {self.contract_no}"

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['contract_no']),
        ]


class Certificate(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('ZIG', 'ZIG'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='certificates')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    current_claim_excl_vat = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    vat_value = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    previous_payment_excl_vat = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-calculate VAT (15% of current claim)
        self.vat_value = self.current_claim_excl_vat * Decimal('0.15')
        super().save(*args, **kwargs)

        # Create or update calculations
        calculations, created = Calculations.objects.get_or_create(
            certificate=self,
            defaults=self._calculate_values()
        )
        if not created:
            for key, value in self._calculate_values().items():
                setattr(calculations, key, value)
            calculations.save()

    def _calculate_values(self):
        retention = self.current_claim_excl_vat * Decimal('0.10')
        value_of_workdone_incl_vat = self.current_claim_excl_vat + self.vat_value
        total_value_of_workdone_excl_vat = self.current_claim_excl_vat
        total_amount_payable = self.current_claim_excl_vat + self.vat_value - retention

        return {
            'value_of_workdone_incl_vat': value_of_workdone_incl_vat,
            'total_value_of_workdone_excl_vat': total_value_of_workdone_excl_vat,
            'retention': retention,
            'total_amount_payable': total_amount_payable,
        }

    def __str__(self):
        return f"Certificate {self.id} - {self.project.name_of_contractor}"

    def get_absolute_url(self):
        return reverse('certificate_detail', kwargs={
            'project_pk': self.project.pk,
            'pk': self.pk
        })

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
        ]


class Calculations(models.Model):
    certificate = models.OneToOneField(Certificate, on_delete=models.CASCADE, related_name='calculations')
    value_of_workdone_incl_vat = models.DecimalField(max_digits=12, decimal_places=2)
    total_value_of_workdone_excl_vat = models.DecimalField(max_digits=12, decimal_places=2)
    retention = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount_payable = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Calculations for Certificate {self.certificate.id}"

    class Meta:
        verbose_name_plural = "Calculations"
