from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http.response import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse
from django.views.generic import FormView, TemplateView, View
from rolepermissions.mixins import HasPermissionsMixin

from accounts.forms import CompanySettingsAccountForm, CompanySettingsMotorCRMForm
from accounts.forms import CompanySettingsIntegrationsForm
from accounts.forms import CompanySettingsNotificationsMotorForm
from accounts.models import UserProfile
from core.email.constants import MOTORINSURANCE_EMAIL_SUBJECTS
from core.utils import log_user_activity
from felix.constants import WORKSPACES


class SettingsBaseView(LoginRequiredMixin, HasPermissionsMixin, FormView):
    template_name = None
    required_permission = 'company_settings'
    form_class = None

    def get_object(self, queryset=None):
        return self.request.company.companysettings

    def get(self, request, *args, **kwargs):
        company_settings = self.get_object()
        ctx = {
            'companysettings': company_settings,
            'settings_form': self.form_class(instance=company_settings),
        }

        log_user_activity(request.user, self.request.path)

        return render(request, self.template_name, ctx)

    def form_invalid(self, form, **kwargs):
        return JsonResponse({'success': False, 'errors': form.errors})


class SettingsAccountView(SettingsBaseView):
    template_name = "accounts/settings_account.djhtml"
    form_class = CompanySettingsAccountForm

    def form_valid(self, form, **kwargs):
        cs = self.get_object()

        cs.displayed_name = form.cleaned_data['displayed_name']
        cs.phone = form.cleaned_data['phone']
        cs.address = form.cleaned_data['address']
        cs.website = form.cleaned_data['website']
        cs.currency = form.cleaned_data['currency']

        cs.save()

        log_user_activity(self.request.user, self.request.path, action='U')

        return JsonResponse({'success': True})


class SettingsMotorCRMView(SettingsBaseView):
    template_name = "accounts/settings_crm_motor.djhtml"
    form_class = CompanySettingsMotorCRMForm

    def get_object(self, queryset=None):
        return self.request.company.workspacemotorsettings

    def get(self, request, *args, **kwargs):
        company_settings = self.get_object()
        ctx = {
            'settings_form': self.form_class(instance=company_settings),
            'lead_form_url': "https://{}{}".format(
                settings.DOMAIN,
                reverse("motorinsurance:lead-form")
            )
        }

        log_user_activity(request.user, self.request.path)

        return render(request, self.template_name, ctx)

    def form_valid(self, form, **kwargs):
        cs = self.get_object()

        cs.quote_expiry_days = form.cleaned_data['quote_expiry_days'] or 30
        cs.auto_close_quoted_deals_in_days = form.cleaned_data['auto_close_quoted_deals_in_days'] or 0

        cs.save()

        log_user_activity(self.request.user, self.request.path, action='U')

        return JsonResponse({'success': True})


class SettingsNotificationsMotorView(SettingsBaseView):
    template_name = "accounts/settings_notifications_motor.djhtml"
    form_class = CompanySettingsNotificationsMotorForm

    def get_object(self, queryset=None):
        return self.request.company.workspacemotorsettings

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['company'] = self.request.company
        ctx['workspace_shortcode'] = 'mt'

        return ctx

    def form_valid(self, form, **kwargs):
        cs = self.get_object()
        cd = form.cleaned_data

        cs.email = cd['email']
        cs.bcc_all_emails = cd['bcc_all_emails']
        cs.reply_to_company_email = form.data['reply_to_company_email'] == 'company'

        cs.lead_notification_email_list = cd['lead_notification_email_list']
        cs.order_notification_email_list = cd['order_notification_email_list']

        cs.send_company_email_on_lead_form_submission = cd['send_company_email_on_lead_form_submission']
        cs.send_company_email_on_order_created_online = cd['send_company_email_on_order_created_online']

        cs.save()

        log_user_activity(self.request.user, self.request.path, action='U')

        return JsonResponse({'success': True})


class SettingsIntegrationsView(SettingsBaseView):
    template_name = "accounts/settings_integrations.djhtml"
    form_class = CompanySettingsIntegrationsForm

    def form_valid(self, form, **kwargs):
        cs = self.get_object()

        cs.helpscout_client_id = form.cleaned_data['helpscout_client_id']
        cs.helpscout_client_secret = form.cleaned_data['helpscout_client_secret']
        cs.helpscout_mailbox_id = form.cleaned_data['helpscout_mailbox_id']

        cs.save()

        log_user_activity(self.request.user, self.request.path, action='U')

        return JsonResponse({'success': True})


class SettingsEmailTemplatesListView(LoginRequiredMixin, HasPermissionsMixin, TemplateView):
    template_name = "accounts/settings_email_templates.djhtml"
    required_permission = 'company_settings'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['company'] = self.request.company
        ctx['workspace_shortcode'] = kwargs['workspace']

        return ctx


class SettingsEmailTemplatesDetailView(LoginRequiredMixin, HasPermissionsMixin, View):
    required_permission = 'company_settings'

    def get(self, request, *args, **kwargs):
        template_type = kwargs['type']
        cs = self.request.company.companysettings

        # All Motor Insurance Email Templates
        if template_type == 'motor_lead':
            title = 'Motor Insurance New Deal Template'
            subject = cs.motor_email_subject_lead_submitted or MOTORINSURANCE_EMAIL_SUBJECTS['NEW_DEAL']
            body = cs.motor_email_content_lead_submitted or self.get_rendered_template('email/motor_insurance_lead_received.html')
        elif template_type == 'motor_quote_new':
            title = 'Motor Insurance New Quote Template'
            subject = cs.motor_email_subject_quote_generated or MOTORINSURANCE_EMAIL_SUBJECTS['QUOTE_NEW']
            body = cs.motor_email_content_quote_generated or self.get_rendered_template('email/motor_insurance_quote_generated.html')
        elif template_type == 'motor_quote_updated':
            title = 'Motor Insurance Quote Updated Template'
            subject = cs.motor_email_subject_quote_updated or MOTORINSURANCE_EMAIL_SUBJECTS['QUOTE_UPDATED']
            body = cs.motor_email_content_quote_updated or self.get_rendered_template('email/motor_insurance_quote_updated.html')
        elif template_type == 'motor_order_summary':
            title = 'Motor Insurance Order Summary Template'
            subject = cs.motor_email_subject_order_summary or MOTORINSURANCE_EMAIL_SUBJECTS['ORDER_SUMMARY']
            body = cs.motor_email_content_order_summary or self.get_rendered_template('email/motor_insurance_order_confirmation.html')
        elif template_type == 'motor_policy_issued':
            title = 'Motor Insurance Policy Issued Template'
            subject = cs.motor_email_subject_policy_issued or MOTORINSURANCE_EMAIL_SUBJECTS['POLICY_ISSUED']
            body = cs.motor_email_content_policy_issued or self.get_rendered_template('email/motor_insurance_policy_issued.html')

        return JsonResponse({'title': title, 'subject': subject, 'body': body}, safe=False)

    def get_rendered_template(self, template_path):
        template = get_template(template_path)

        return template.template.source


class SettingsWorkspaceUsersView(LoginRequiredMixin, HasPermissionsMixin, TemplateView):
    template_name = "accounts/workspace_users.djhtml"
    required_permission = 'company_settings'
    form_class = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['company'] = self.request.company

        workspaces = dict(WORKSPACES)
        workspace_shortcode = kwargs['workspace'].upper()

        if workspace_shortcode not in workspaces:
            raise Http404()

        ctx['workspace'] = workspaces[workspace_shortcode]
        ctx['workspace_shortcode'] = workspace_shortcode.lower()

        company_users = UserProfile.objects.filter(company=self.request.company, user__is_active=True)

        ctx['workspace_users'] = company_users.filter(allowed_workspaces__icontains=workspace_shortcode)
        ctx['remaining_users'] = company_users.exclude(pk__in=ctx['workspace_users'])

        return ctx


class SettingsWorkspaceUsersAddEditView(LoginRequiredMixin, HasPermissionsMixin, View):
    template_name = "accounts/workspace_users.djhtml"
    required_permission = 'company_settings'
    form_class = None

    def get(self, request, *args, **kwargs):
        uid = kwargs['pk']
        workspace = kwargs['workspace']

        try:
            userprofile = UserProfile.objects.get(user__id=uid)

            if workspace.upper() not in userprofile.allowed_workspaces:
                userprofile.allowed_workspaces.append(workspace.upper())
            else:
                userprofile.allowed_workspaces.remove(workspace.upper())

            userprofile.save()
        except UserProfile.DoesNotExist:
            raise Http404()

        return JsonResponse({'success': True})
