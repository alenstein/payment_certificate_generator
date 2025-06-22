from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class SystemSettings(models.Model):
    # Company Information
    company_name = models.CharField(max_length=200, default="Your Company Name")
    company_address = models.TextField(default="Company Address")
    company_phone = models.CharField(max_length=50, blank=True)
    company_email = models.EmailField(blank=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # Certificate Settings
    default_currency = models.CharField(
        max_length=3,
        choices=[('USD', 'USD'), ('ZIG', 'ZIG'), ('EUR', 'EUR'), ('GBP', 'GBP')],
        default='USD'
    )
    vat_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('15.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    retention_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('10.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    
    # PDF Settings
    pdf_header_text = models.CharField(max_length=200, default="PAYMENT CERTIFICATE")
    pdf_footer_text = models.TextField(
        default="This certificate is issued without prejudice to the rights and obligations of the parties under the Contract."
    )
    include_company_logo_in_pdf = models.BooleanField(default=True)
    
    # Approval Settings
    require_dual_approval = models.BooleanField(default=True)
    approval_title_1 = models.CharField(max_length=100, default="Project Manager")
    approval_title_2 = models.CharField(max_length=100, default="Finance Officer")
    
    # Notification Settings
    email_notifications_enabled = models.BooleanField(default=True)
    notify_on_certificate_creation = models.BooleanField(default=True)
    notify_on_project_creation = models.BooleanField(default=False)
    
    # Security Settings
    session_timeout_minutes = models.IntegerField(
        default=60,
        validators=[MinValueValidator(5), MaxValueValidator(480)]
    )
    max_login_attempts = models.IntegerField(
        default=5,
        validators=[MinValueValidator(3), MaxValueValidator(10)]
    )
    
    # System Preferences
    items_per_page = models.IntegerField(
        default=12,
        validators=[MinValueValidator(5), MaxValueValidator(50)]
    )
    default_date_format = models.CharField(
        max_length=20,
        choices=[
            ('%B %d, %Y', 'January 01, 2024'),
            ('%d/%m/%Y', '01/01/2024'),
            ('%m/%d/%Y', '01/01/2024'),
            ('%Y-%m-%d', '2024-01-01'),
        ],
        default='%B %d, %Y'
    )
    
    # Backup Settings
    auto_backup_enabled = models.BooleanField(default=False)
    backup_frequency_days = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    
    # Advanced Settings
    enable_audit_trail = models.BooleanField(default=True)
    enable_data_export = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(
        default="System is under maintenance. Please try again later.",
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return f"System Settings - {self.company_name}"

    @classmethod
    def get_settings(cls):
        """Get or create system settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Display Preferences
    theme = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='light'
    )
    language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('es', 'Spanish'), ('fr', 'French')],
        default='en'
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        choices=[
            ('UTC', 'UTC'),
            ('America/New_York', 'Eastern Time'),
            ('America/Chicago', 'Central Time'),
            ('America/Denver', 'Mountain Time'),
            ('America/Los_Angeles', 'Pacific Time'),
            ('Europe/London', 'London'),
            ('Europe/Paris', 'Paris'),
            ('Asia/Tokyo', 'Tokyo'),
        ]
    )
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    browser_notifications = models.BooleanField(default=False)
    weekly_summary = models.BooleanField(default=True)
    
    # Dashboard Preferences
    show_recent_projects = models.BooleanField(default=True)
    show_statistics = models.BooleanField(default=True)
    projects_per_page = models.IntegerField(
        default=12,
        validators=[MinValueValidator(5), MaxValueValidator(50)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('EXPORT', 'Export'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} - {self.timestamp}"
