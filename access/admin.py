from django.contrib import admin

from .models import Module, OrganizationModuleAccess, UserModuleAccess


admin.site.register([Module, OrganizationModuleAccess, UserModuleAccess])
