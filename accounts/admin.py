from django.contrib import admin
from django.utils.safestring import mark_safe

import felix.admin as felix_admin
from accounts.models import UserProfile, Company, CompanySettings, WorkspaceMotorSettings, AlgoDrivenUsage
from core.intercom import Intercom
from felix.admin import global_admin


class CompanyAdmin(admin.ModelAdmin):
    list_filter = ('available_motor_insurance_products', 'status',)
    list_display = ('company_logo', 'name', 'status', 'created_on', 'updated_on',)

    def company_logo(self, obj):
        return mark_safe(
            '<img src="{}" width="50" />'.format(
                obj.companysettings.get_company_logo(),
            )
        )

    def save_model(self, request, obj, form, change):
        super(CompanyAdmin, self).save_model(request, obj, form, change)

        try:
            company_settings = CompanySettings.objects.get(company=obj)
        except CompanySettings.DoesNotExist:
            company_settings = CompanySettings(
                company=obj,
                displayed_name=obj.name
            )
            company_settings.save()

    company_logo.short_description = 'Logo'
    company_logo.allow_tags = True


class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ('company', 'displayed_name', 'phone', 'email', 'updated_on')


class CompanyWorkspaceMotorSettingsAdmin(admin.ModelAdmin):
    list_display = ('company_logo', 'company', 'algodriven_credits', 'updated_on')

    def company_logo(self, obj):
        return mark_safe(
            '<img src="{}" width="50" />'.format(
                obj.company.companysettings.get_company_logo(),
            )
        )


class AlgoDrivenUsageAdmin(admin.ModelAdmin):
    list_filter = ('company',)
    list_display = ('company', 'year', 'month', 'count', 'updated_on')


class DomainAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'domain')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'user_companies',
                    'is_active', 'is_superuser', 'is_staff', 'last_login',)
    list_filter = ('is_superuser', 'is_staff', 'is_active',)
    search_fields = ('username', 'email', 'first_name', 'last_name',)

    def user_companies(self, obj):
        companies = []

        for company in Company.objects.all().exclude(schema_name='public'):
            company.activate()

            if company.userprofile_set.filter(user=obj).count():
                companies.append(company.name)

            company.deactivate()

        return ', '.join(companies)

    user_companies.short_description = 'Company'

    def save_model(self, request, obj, form, change):
        if obj.is_active != form.cleaned_data['is_active']:
            intercom = Intercom()

            intercom_user_data = intercom.get_contact_by_email_and_id(obj.username, obj.pk)

            if intercom_user_data:
                intercom.update_contact(
                    intercom_user_data['id'], {'custom_attributes': {'Deleted': form.cleaned_data['is_active']}})

        super(UserAdmin, self).save_model(request, obj, form, change)


felix_admin.tenant_admin.register(UserProfile)
# global_admin.register(Company, CompanyAdmin)
global_admin.register(WorkspaceMotorSettings, CompanyWorkspaceMotorSettingsAdmin)
global_admin.register(CompanySettings, CompanySettingsAdmin)
global_admin.register(AlgoDrivenUsage, AlgoDrivenUsageAdmin)
