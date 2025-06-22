import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.urls import reverse_lazy, reverse
from .models import Project, Certificate, Calculations
from .forms import ProjectForm, CertificateForm
from .auth_forms import CustomUserCreationForm
from .utils import generate_certificate_pdf

logger = logging.getLogger(__name__)


def home(request):
    """Home page view"""
    return render(request, 'certificates/home.html')


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('project_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to Payment Certificates.')
                logger.info(f'New user registered: {user.username}')
                return redirect('project_list')
            except Exception as e:
                logger.error(f'Registration error: {str(e)}')
                messages.error(request, 'Registration failed. Please try again.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'certificates/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user).select_related('owner')


class ProjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Project
    template_name = 'certificates/project_detail.html'
    context_object_name = 'project'

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certificates'] = self.object.certificates.all().select_related('project')
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'certificates/project_form.html'

    def form_valid(self, form):
        try:
            with transaction.atomic():
                form.instance.owner = self.request.user
                response = super().form_valid(form)
                messages.success(self.request, 'Project created successfully!')
                logger.info(f'Project created: {self.object.contract_no} by {self.request.user.username}')
                return response
        except Exception as e:
            logger.error(f'Project creation error: {str(e)}')
            messages.error(self.request, 'Failed to create project. Please try again.')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Project'
        return context


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'certificates/project_form.html'

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Project updated successfully!')
            logger.info(f'Project updated: {self.object.contract_no} by {self.request.user.username}')
            return response
        except Exception as e:
            logger.error(f'Project update error: {str(e)}')
            messages.error(self.request, 'Failed to update project. Please try again.')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Project'
        return context


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'certificates/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

    def delete(self, request, *args, **kwargs):
        try:
            project = self.get_object()
            project_name = project.name_of_contractor
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f'Project "{project_name}" deleted successfully!')
            logger.info(f'Project deleted: {project.contract_no} by {request.user.username}')
            return response
        except Exception as e:
            logger.error(f'Project deletion error: {str(e)}')
            messages.error(request, 'Failed to delete project. Please try again.')
            return redirect('project_detail', pk=self.get_object().pk)


class CertificateCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Certificate
    form_class = CertificateForm
    template_name = 'certificates/certificate_form.html'

    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return project.owner == self.request.user

    def form_valid(self, form):
        try:
            with transaction.atomic():
                project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
                form.instance.project = project
                response = super().form_valid(form)
                messages.success(self.request, 'Certificate created successfully!')
                logger.info(f'Certificate created for project {project.contract_no} by {self.request.user.username}')
                return response
        except Exception as e:
            logger.error(f'Certificate creation error: {str(e)}')
            messages.error(self.request, 'Failed to create certificate. Please try again.')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        context['title'] = 'Create New Certificate'
        return context

    def get_success_url(self):
        return reverse('certificate_detail', kwargs={
            'project_pk': self.kwargs['project_pk'],
            'pk': self.object.pk
        })


class CertificateDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Certificate
    template_name = 'certificates/certificate_detail.html'
    context_object_name = 'certificate'

    def test_func(self):
        certificate = self.get_object()
        return certificate.project.owner == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project
        try:
            context['calculations'] = self.object.calculations
        except Calculations.DoesNotExist:
            logger.warning(f'Calculations not found for certificate {self.object.pk}')
            context['calculations'] = None
        return context


@login_required
def certificate_pdf(request, project_pk, pk):
    """Generate PDF for certificate"""
    try:
        project = get_object_or_404(Project, pk=project_pk)
        certificate = get_object_or_404(Certificate, pk=pk, project=project)
        
        # Check permissions
        if certificate.project.owner != request.user:
            raise PermissionDenied("You don't have permission to access this certificate.")
        
        try:
            calculations = certificate.calculations
        except Calculations.DoesNotExist:
            logger.error(f'Calculations not found for certificate {certificate.pk}')
            messages.error(request, 'Certificate calculations not found.')
            return redirect('certificate_detail', project_pk=project_pk, pk=pk)
        
        # Generate PDF
        response = generate_certificate_pdf(project, certificate, calculations)
        logger.info(f'PDF generated for certificate {certificate.pk} by {request.user.username}')
        return response
        
    except Exception as e:
        logger.error(f'PDF generation error: {str(e)}')
        messages.error(request, 'Failed to generate PDF. Please try again.')
        return redirect('certificate_detail', project_pk=project_pk, pk=pk)


# Function-based views for backward compatibility
project_list = ProjectListView.as_view()
project_detail = ProjectDetailView.as_view()
project_create = ProjectCreateView.as_view()
project_update = ProjectUpdateView.as_view()
project_delete = ProjectDeleteView.as_view()
certificate_create = CertificateCreateView.as_view()
certificate_detail = CertificateDetailView.as_view()
