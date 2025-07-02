import datetime
import hashlib
import random
import re

import yaml
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import now
from rolepermissions.checkers import get_user_roles
from tinymce.models import HTMLField

from core.mixins import AuditTrailMixin
from core.utils import get_initials_from_the_name
from core.utils import is_valid_number, normalize_phone_number
from felix.constants import COUNTRIES, FIELD_LENGTHS, PUBLIC_STORAGE, CURRENCIES, EMIRATES_LIST
from felix.constants import GENDER_CHOICES, USER_ROLES, WORKSPACES
from felix.constants import INVITATION_EXPIRE_DAYS, INVITATION_SECRET_KEY


def get_user_full_name(self):
    return self.get_full_name() or self.username


User.add_to_class("__str__", get_user_full_name)


class Company(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_DELETED = 'deleted'

    STATUSES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_DELETED, 'Deleted')
    )

    country_code = models.CharField(max_length=2, default='AE', choices=COUNTRIES)
    status = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=STATUSES)

    name = models.CharField(max_length=FIELD_LENGTHS['name'])

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    available_motor_insurance_products = models.ManyToManyField('motorinsurance_shared.Product',
                                                                related_name='+', blank=True)
    quotable_motor_insurers = models.ManyToManyField('insurers.Insurer', related_name='+', blank=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name

    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def get_motor_insurance_products(self):
        return self.available_motor_insurance_products.filter(is_active=True)

    def get_algodrive_usage_for_current_month(self):
        try:
            record = self.algodrivenusage_set.get(year=timezone.now().year, month=timezone.now().month)
            return record.count
        except AlgoDrivenUsage.DoesNotExist:
            pass

        return 0


class WorkspaceMotorSettings(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    email = models.EmailField(max_length=FIELD_LENGTHS['email'], blank=True)

    quote_expiry_days = models.PositiveSmallIntegerField(default=30)
    auto_close_quoted_deals_in_days = models.PositiveSmallIntegerField(default=30, blank=True)
    bcc_all_emails = models.BooleanField(default=False)

    lead_notification_email_list = models.TextField(blank=True)
    order_notification_email_list = models.TextField(blank=True)

    send_company_email_on_lead_form_submission = models.BooleanField(default=True)
    send_company_email_on_order_created_online = models.BooleanField(default=True)

    reply_to_company_email = models.BooleanField(default=False)

    algodriven_credits = models.PositiveSmallIntegerField(default=20)

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Company Motor Workspace Setting'
        verbose_name_plural = 'Companies Motor Workspace Settings'

    def __str__(self):
        return self.company.name


class CompanySettings(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)

    displayed_name = models.CharField(max_length=FIELD_LENGTHS['name'])
    phone = models.CharField(max_length=FIELD_LENGTHS['phone'], blank=True)
    email = models.EmailField(max_length=FIELD_LENGTHS['email'])
    address = models.CharField(max_length=FIELD_LENGTHS['address'], blank=True)
    city_name = models.CharField(max_length=FIELD_LENGTHS['address'], blank=True)
    website = models.URLField(max_length=FIELD_LENGTHS['website'], blank=True)

    logo = models.ImageField(upload_to='company-logos', storage=PUBLIC_STORAGE, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCIES, blank=True)

    footer_message = models.TextField(blank=True)
    company_timings = models.TextField(blank=True)

    # terms_and_conditions_url is deprecated in favor of a more configurable order_terms field.
    terms_and_conditions_url = models.URLField(max_length=FIELD_LENGTHS['website'], blank=True, editable=False)
    order_terms = HTMLField(blank=True)

    quote_expiry_days = models.PositiveSmallIntegerField(default=30)

    auto_close_quoted_deals_in_days = models.PositiveSmallIntegerField(default=30, blank=True)

    auto_quote_allowed = models.BooleanField(default=False)
    lead_source_allowed = models.BooleanField(default=True)
    doc_parser_allowed = models.BooleanField(default=False)

    bcc_all_emails = models.BooleanField(default=False)
    motor_promo_code_allowed = models.BooleanField(default=False)

    lead_notification_email_list = models.TextField(blank=True)
    order_notification_email_list = models.TextField(blank=True)

    motor_email_subject_lead_submitted = models.CharField(max_length=FIELD_LENGTHS['email_subject'], blank=True)
    motor_email_content_lead_submitted = models.TextField(blank=True)

    motor_email_subject_quote_generated = models.CharField(max_length=FIELD_LENGTHS['email_subject'], blank=True)
    motor_email_content_quote_generated = models.TextField(blank=True)

    motor_email_subject_quote_updated = models.CharField(max_length=FIELD_LENGTHS['email_subject'], blank=True)
    motor_email_content_quote_updated = models.TextField(blank=True)

    motor_email_subject_order_summary = models.CharField(max_length=FIELD_LENGTHS['email_subject'], blank=True)
    motor_email_content_order_summary = models.TextField(blank=True)

    motor_email_subject_policy_issued = models.CharField(max_length=FIELD_LENGTHS['email_subject'], blank=True)
    motor_email_content_policy_issued = models.TextField(blank=True)

    motor_lead_form_title = models.CharField(max_length=FIELD_LENGTHS['title'], blank=True)
    motor_lead_form_subtitle = models.CharField(max_length=FIELD_LENGTHS['title'], blank=True)

    motor_lead_form_thankyou_content = models.TextField(blank=True)

    motor_lead_form_meta_title = models.CharField(max_length=FIELD_LENGTHS['meta'], blank=True)
    motor_lead_form_meta_keywords = models.CharField(max_length=FIELD_LENGTHS['meta'], blank=True)
    motor_lead_form_meta_description = models.CharField(max_length=FIELD_LENGTHS['meta'], blank=True)

    motor_quote_comparison_meta_title = models.CharField(max_length=FIELD_LENGTHS['meta'], blank=True)
    motor_quote_comparison_meta_keywords = models.CharField(max_length=FIELD_LENGTHS['meta'], blank=True)
    motor_quote_comparison_meta_description = models.CharField(max_length=FIELD_LENGTHS['meta'], blank=True)

    helpscout_client_id = models.CharField(max_length=FIELD_LENGTHS['api_keys'], blank=True)
    helpscout_client_secret = models.CharField(max_length=FIELD_LENGTHS['api_keys'], blank=True)
    helpscout_mailbox_id = models.CharField(max_length=FIELD_LENGTHS['api_keys'], blank=True)

    from_email = models.CharField(max_length=FIELD_LENGTHS['email'], blank=True)
    mailgun_api_key = models.CharField(max_length=FIELD_LENGTHS['api_keys'], blank=True)
    mailgun_api_url = models.CharField(max_length=FIELD_LENGTHS['website'], blank=True)
    postmark_api_key = models.CharField(max_length=FIELD_LENGTHS['api_keys'], blank=True)

    reply_to_company_email = models.BooleanField(default=False)

    send_company_email_on_motor_lead_form_submission = models.BooleanField(default=True)
    send_company_email_on_motor_order_created_online = models.BooleanField(default=True)

    access_motor_insurance_module = models.BooleanField(
        help_text="If checked, company users can access Motor Insurance module", default=True)

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Companies Settings'

    def __str__(self):
        return "{} [{}]".format(self.company.name, self.displayed_name)

    def helpscout_enabled(self):
        return self.helpscout_client_id != '' and self.helpscout_client_secret != '' and self.helpscout_mailbox_id != ''

    def get_company_logo(self):
        return self.logo.url if self.logo else static("images/avatar.jpg")

    def get_company_logo_for_frontend(self):
        return self.logo.url if self.logo else None

    def get_order_terms_as_list(self):
        return re.findall(r'<li>(.*?)</li>', self.order_terms)


class AlgoDrivenUsage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()

    count = models.PositiveIntegerField(default=0)

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Algo Driven Usage'
        verbose_name_plural = 'Algo Driven Usages'

    def __str__(self):
        return self.company.name


class UserProfile(AuditTrailMixin, models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    gender = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=GENDER_CHOICES, blank=True, null=True)
    nationality = models.CharField(max_length=2, choices=COUNTRIES, blank=True, null=True)
    phone = models.CharField(max_length=FIELD_LENGTHS['phone'], blank=True, default='')
    designation = models.CharField(max_length=50, blank=True, default='')
    image = models.ImageField(upload_to='user-profile-images', storage=PUBLIC_STORAGE, blank=True)

    bcc_all_emails = models.BooleanField(default=False)
    whatsapp_widget_for_ecommerce = models.BooleanField(default=False)

    email_if_lead_created_using_personal_link = models.BooleanField(default=False)
    email_when_new_order_placed = models.BooleanField(default=False)

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    allowed_workspaces = ArrayField(
        models.CharField(max_length=FIELD_LENGTHS['workspace'], choices=WORKSPACES),
        blank=True,
        default=list,
        help_text='Comma separated list of values from: {}'.format(', '.join(
            map(lambda x: x[0], WORKSPACES)
        ))
    )

    ignored_fields = ['image']

    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'user profiles'

    def __unicode__(self):
        return u"%s" % self.user.get_full_name()

    def __str__(self):
        return u"{} - {}".format(self.user.get_full_name(), self.user.username)

    def get_profile_image(self):
        return self.image.url if self.image else False

    def get_initials(self):
        return get_initials_from_the_name(self.user.get_full_name() or self.user.username[:2])

    def get_assigned_role(self):
        roles = get_user_roles(self.user)

        if len(roles):
            return roles[0].__name__.lower()

        return None

    def has_admin_role(self):
        return self.get_assigned_role() == 'admin'

    def has_producer_role(self):
        return self.get_assigned_role() == 'producer'

    def has_user_role(self):
        return self.get_assigned_role() == 'user'

    def get_motor_lead_form_url(self):
        user_first_name = slugify(self.user.first_name or self.user.username)

        return "https://{}{}".format(
            settings.DOMAIN,
            reverse("motorinsurance:lead-form-for-user", kwargs={
                "user_id": self.user.pk, "username": user_first_name
            })
        )

    def get_mortgage_lead_form_url(self):

        return "https://{}{}".format(
            'nexusmortgagebrokers.com/nmb/',
            f'?email={self.user.email}&source={self.user.first_name}_{self.user.last_name}'
        )

    def get_health_lead_form_url(self):
        user_first_name = slugify(self.user.first_name or self.user.username)
        return f"https://{settings.DOMAIN}/health-insurance-form/get-quotes/start/{user_first_name}/{self.user.pk}/"        

    def get_normalized_whatsapp_number(self):
        if self.whatsapp_widget_for_ecommerce and is_valid_number(self.phone):
            return normalize_phone_number(self.phone)

        return None

    def get_allowed_workspaces_count(self):
        return len(self.allowed_workspaces)


class InvitationManager(models.Manager):
    def invite(self, values):
        invitation = None
        try:
            invitation = self.filter(email=values['email'])[0]
            if not invitation.is_valid():
                invitation = None
        except (Invitation.DoesNotExist, IndexError):
            pass

        if invitation is None:
            key = '%s%0.16f%s' % (INVITATION_SECRET_KEY, random.random(), values['email'])
            values['key'] = hashlib.sha1(key.encode('utf-8')).hexdigest()

            invitation = self.create(**values)

        return invitation

    def find(self, invitation_key):
        try:
            invitation = self.get(key=invitation_key)
        except IndexError:
            raise Invitation.DoesNotExist

        if not invitation.is_valid():
            invitation.delete()
            raise Invitation.DoesNotExist

        if invitation.accepted:
            raise Invitation.DoesNotExist

        return invitation

    def accepted(self):
        return self.get_query_set().filter(accepted=True)

    def valid(self):
        expiration = now() - datetime.timedelta(INVITATION_EXPIRE_DAYS)

        return self.get_query_set().filter(created_on__gte=expiration)

    def expired(self):
        expiration = now() - datetime.timedelta(INVITATION_EXPIRE_DAYS)

        return self.get_query_set().filter(created_on__le=expiration)


class Invitation(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitation_sender', null=True)
    email = models.EmailField(max_length=FIELD_LENGTHS['email'])
    first_name = models.CharField(max_length=FIELD_LENGTHS['name'], blank=True)

    role = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=USER_ROLES)
    key = models.CharField(max_length=FIELD_LENGTHS['api_keys'], unique=True)

    accepted = models.BooleanField(default=False)

    allowed_workspaces = ArrayField(
        models.CharField(max_length=FIELD_LENGTHS['workspace'], choices=WORKSPACES),
        blank=True, default=list
    )

    created_on = models.DateTimeField(auto_now_add=True)
    accepted_on = models.DateTimeField(auto_now=True)

    objects = InvitationManager()

    class Meta:
        verbose_name = 'invitation'
        verbose_name_plural = 'invitations'

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('accounts:invitation-register', kwargs={'key': self.key})

    @property
    def expires_at(self):
        return self.created_on + datetime.timedelta(INVITATION_EXPIRE_DAYS)

    def is_valid(self):
        return now() < self.expires_at

    def expiration_date(self):
        return self.expires_at.date()
