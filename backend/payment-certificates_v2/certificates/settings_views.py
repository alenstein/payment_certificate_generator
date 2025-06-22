import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from django.db import transaction
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.core.management import call_command
from django.conf import settings
import io
import csv
from .settings_models import SystemSettings, UserPreferences, AuditLog
from .settings_forms import SystemSettingsForm, UserPreferencesForm, ProfileUpdateForm
from .models import Project, Certificate

logger = logging.getLogger(__name__)


def is_superuser(user):
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def system_settings(request):
    """System-wide settings (admin only)"""
    settings_obj = SystemSettings.get_settings()
    
    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            try:
                with transaction.atomic():
                    settings_obj = form.save(commit=False)
                    settings_obj.updated_by = request.user
                    settings_obj.save()
                    
                    # Log the action
                    AuditLog.objects.create(
                        user=request.user,
                        action='UPDATE',
                        model_name='SystemSettings',
                        object_id='1',
                        description='System settings updated',
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    messages.success(request, 'System settings updated successfully!')
                    logger.info(f'System settings updated by {request.user.username}')
                    return redirect('system_settings')
            except Exception as e:
                logger.error(f'Error updating system settings: {str(e)}')
                messages.error(request, 'Failed to update system settings. Please try again.')
    else:
        form = SystemSettingsForm(instance=settings_obj)
    
    return render(request, 'certificates/settings/system_settings.html', {
        'form': form,
        'settings': settings_obj
    })


@login_required
def user_preferences(request):
    """User preferences settings"""
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        if 'preferences_form' in request.POST:
            preferences_form = UserPreferencesForm(request.POST, instance=preferences)
            profile_form = ProfileUpdateForm(instance=request.user)
            
            if preferences_form.is_valid():
                try:
                    preferences_form.save()
                    messages.success(request, 'Preferences updated successfully!')
                    logger.info(f'User preferences updated for {request.user.username}')
                    return redirect('user_preferences')
                except Exception as e:
                    logger.error(f'Error updating user preferences: {str(e)}')
                    messages.error(request, 'Failed to update preferences. Please try again.')
        
        elif 'profile_form' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, instance=request.user)
            preferences_form = UserPreferencesForm(instance=preferences)
            
            if profile_form.is_valid():
                try:
                    profile_form.save()
                    messages.success(request, 'Profile updated successfully!')
                    logger.info(f'Profile updated for {request.user.username}')
                    return redirect('user_preferences')
                except Exception as e:
                    logger.error(f'Error updating profile: {str(e)}')
                    messages.error(request, 'Failed to update profile. Please try again.')
    else:
        preferences_form = UserPreferencesForm(instance=preferences)
        profile_form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'certificates/settings/user_preferences.html', {
        'preferences_form': preferences_form,
        'profile_form': profile_form,
        'preferences': preferences
    })


class AuditLogView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AuditLog
    template_name = 'certificates/settings/audit_log.html'
    context_object_name = 'logs'
    paginate_by = 25

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = AuditLog.objects.all()
        
        # Filter by user
        user_filter = self.request.GET.get('user')
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)
        
        # Filter by action
        action_filter = self.request.GET.get('action')
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        
        # Filter by model
        model_filter = self.request.GET.get('model')
        if model_filter:
            queryset = queryset.filter(model_name__icontains=model_filter)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_choices'] = AuditLog.ACTION_CHOICES
        context['filters'] = {
            'user': self.request.GET.get('user', ''),
            'action': self.request.GET.get('action', ''),
            'model': self.request.GET.get('model', ''),
        }
        return context


@login_required
@user_passes_test(is_superuser)
def system_statistics(request):
    """System statistics and analytics"""
    try:
        # Basic statistics
        total_users = User.objects.count()
        total_projects = Project.objects.count()
        total_certificates = Certificate.objects.count()
        
        # Recent activity
        recent_projects = Project.objects.order_by('-created_at')[:5]
        recent_certificates = Certificate.objects.select_related('project').order_by('-created_at')[:5]
        recent_logs = AuditLog.objects.order_by('-timestamp')[:10]
        
        # User activity
        active_users = User.objects.filter(last_login__isnull=False).count()
        
        # Monthly statistics (last 6 months)
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        
        six_months_ago = timezone.now() - timedelta(days=180)
        
        monthly_projects = Project.objects.filter(
            created_at__gte=six_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        monthly_certificates = Certificate.objects.filter(
            created_at__gte=six_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        context = {
            'total_users': total_users,
            'total_projects': total_projects,
            'total_certificates': total_certificates,
            'active_users': active_users,
            'recent_projects': recent_projects,
            'recent_certificates': recent_certificates,
            'recent_logs': recent_logs,
            'monthly_projects': list(monthly_projects),
            'monthly_certificates': list(monthly_certificates),
        }
        
        return render(request, 'certificates/settings/statistics.html', context)
        
    except Exception as e:
        logger.error(f'Error loading system statistics: {str(e)}')
        messages.error(request, 'Failed to load system statistics.')
        return redirect('system_settings')


@login_required
@user_passes_test(is_superuser)
def export_data(request):
    """Export system data"""
    export_type = request.GET.get('type', 'projects')
    
    try:
        response = HttpResponse(content_type='text/csv')
        
        if export_type == 'projects':
            response['Content-Disposition'] = 'attachment; filename="projects.csv"'
            writer = csv.writer(response)
            writer.writerow(['ID', 'Contractor', 'Contract No', 'Vote No', 'Tender Sum', 'Owner', 'Created At'])
            
            for project in Project.objects.select_related('owner'):
                writer.writerow([
                    project.id,
                    project.name_of_contractor,
                    project.contract_no,
                    project.vote_no,
                    project.tender_sum,
                    project.owner.username,
                    project.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        elif export_type == 'certificates':
            response['Content-Disposition'] = 'attachment; filename="certificates.csv"'
            writer = csv.writer(response)
            writer.writerow(['ID', 'Project', 'Currency', 'Current Claim', 'VAT', 'Previous Payment', 'Created At'])
            
            for cert in Certificate.objects.select_related('project'):
                writer.writerow([
                    cert.id,
                    cert.project.name_of_contractor,
                    cert.currency,
                    cert.current_claim_excl_vat,
                    cert.vat_value,
                    cert.previous_payment_excl_vat,
                    cert.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        elif export_type == 'audit_logs':
            response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
            writer = csv.writer(response)
            writer.writerow(['User', 'Action', 'Model', 'Object ID', 'Description', 'IP Address', 'Timestamp'])
            
            for log in AuditLog.objects.select_related('user'):
                writer.writerow([
                    log.user.username if log.user else 'System',
                    log.action,
                    log.model_name,
                    log.object_id,
                    log.description,
                    log.ip_address,
                    log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        # Log the export
        AuditLog.objects.create(
            user=request.user,
            action='EXPORT',
            model_name=export_type.title(),
            description=f'Exported {export_type} data',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return response
        
    except Exception as e:
        logger.error(f'Error exporting data: {str(e)}')
        messages.error(request, 'Failed to export data. Please try again.')
        return redirect('system_statistics')


@login_required
@user_passes_test(is_superuser)
def system_backup(request):
    """Create system backup"""
    if request.method == 'POST':
        try:
            # Create a database backup using Django's dumpdata command
            output = io.StringIO()
            call_command('dumpdata', '--natural-foreign', '--natural-primary', stdout=output)
            
            response = HttpResponse(output.getvalue(), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
            
            # Log the backup
            AuditLog.objects.create(
                user=request.user,
                action='EXPORT',
                model_name='SystemBackup',
                description='System backup created',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return response
            
        except Exception as e:
            logger.error(f'Error creating backup: {str(e)}')
            messages.error(request, 'Failed to create backup. Please try again.')
    
    return redirect('system_settings')


@login_required
def settings_dashboard(request):
    """Settings dashboard - main settings page"""
    context = {
        'is_admin': request.user.is_superuser,
        'user_preferences': getattr(request.user, 'preferences', None),
    }
    
    if request.user.is_superuser:
        context['system_settings'] = SystemSettings.get_settings()
        context['recent_logs'] = AuditLog.objects.order_by('-timestamp')[:5]
    
    return render(request, 'certificates/settings/dashboard.html', context)
