from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import settings_views
from .auth_forms import CustomAuthenticationForm

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/new/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_update, name='project_update'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Certificates
    path('projects/<int:project_pk>/certificates/new/', views.certificate_create, name='certificate_create'),
    path('projects/<int:project_pk>/certificates/<int:pk>/', views.certificate_detail, name='certificate_detail'),
    path('projects/<int:project_pk>/certificates/<int:pk>/pdf/', views.certificate_pdf, name='certificate_pdf'),
    
    # Settings
    path('settings/', settings_views.settings_dashboard, name='settings_dashboard'),
    path('settings/system/', settings_views.system_settings, name='system_settings'),
    path('settings/preferences/', settings_views.user_preferences, name='user_preferences'),
    path('settings/statistics/', settings_views.system_statistics, name='system_statistics'),
    path('settings/audit-log/', settings_views.AuditLogView.as_view(), name='audit_log'),
    path('settings/export/', settings_views.export_data, name='export_data'),
    path('settings/backup/', settings_views.system_backup, name='system_backup'),
]
