from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import School, Domain

# @admin.register(School)
# class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
#         list_display = ('name',)

# @admin.register(Domain)
# class DomainAdmin(TenantAdminMixin, admin.ModelAdmin):
#         pass


class TenantAdminSite(admin.AdminSite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register(School)
        self.register(Domain)
        
tenant_admin_site = TenantAdminSite(name="tenant_admin_site")