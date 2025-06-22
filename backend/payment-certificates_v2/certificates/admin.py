from django.contrib import admin
from .models import Project, Certificate, Calculations

# Register your models here (for future database use)
admin.site.register(Project)
admin.site.register(Certificate)
admin.site.register(Calculations)
