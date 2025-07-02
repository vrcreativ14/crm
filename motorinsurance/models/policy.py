import datetime
import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils.timezone import now as tz_now

from core.algolia import Algolia
from core.mixins import AuditTrailMixin
from felix.constants import FIELD_LENGTHS, CAR_YEARS_LIST
from motorinsurance.constants import INSURANCE_TYPES
from motorinsurance_shared.models import CarMake, CarTrim


class Policy(AuditTrailMixin, models.Model):
    """Stores details of a motor policy issues to a customer. May have an associated deal"""
    STATUS_ACTIVE = 'active'
    STATUS_DELETED = 'deleted'
    STATUSES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DELETED, 'Deleted')
    )
    ignored_fields = ['policy_document', 'invoice_document']

    def get_policy_upload_path(self, filename):
        """Returns a customer specific folder to write the policy document to.

        Defined first because we use it as a field parameter `upload_to`. Saving on a per customer folder allows us
        easy navigation when manually browsing the files."""
        base_path = 'policies/{}-{}/{}-{}'.format(self.company.pk, slugify(self.company.name), self.customer.pk,
                                                  slugify(self.customer.name))

        date_component = datetime.datetime.utcnow().strftime('%Y-%m-%d')

        return f'{base_path}/{date_component}_{uuid.uuid4().hex}_{filename}'

    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='motor_policies')
    product = models.ForeignKey('motorinsurance_shared.Product', on_delete=models.CASCADE, null=True)

    deal = models.OneToOneField('motorinsurance.Deal', null=True, on_delete=models.SET_NULL, blank=True)
    owner = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL, blank=True)

    reference_number = models.CharField(max_length=FIELD_LENGTHS['reference_numbers'])
    invoice_number = models.CharField(max_length=FIELD_LENGTHS['reference_numbers'], blank=True)

    policy_document = models.FileField(max_length=FIELD_LENGTHS['file'], upload_to=get_policy_upload_path)
    invoice_document = models.FileField(max_length=FIELD_LENGTHS['file'], upload_to=get_policy_upload_path, blank=True)

    attachments = GenericRelation('core.Attachment')

    policy_start_date = models.DateField(blank=True)
    policy_expiry_date = models.DateField(blank=True)

    # New Fields to de-couple policy model from others
    custom_product_name = models.CharField(max_length=FIELD_LENGTHS['name'], blank=True)

    car_year = models.CharField(max_length=4, choices=CAR_YEARS_LIST, blank=True)
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, null=True)
    car_trim = models.ForeignKey(CarTrim, on_delete=models.SET_NULL, null=True)
    custom_car_name = models.CharField(max_length=FIELD_LENGTHS['name'], blank=True)

    insurance_type = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=INSURANCE_TYPES, blank=True)

    agency_repair = models.BooleanField(default=False)
    ncd_required = models.BooleanField(default=False)

    premium = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductible = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductible_extras = models.TextField(blank=True)
    insured_car_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mortgage_by = models.CharField(max_length=FIELD_LENGTHS['address'], blank=True)

    default_add_ons = ArrayField(
        models.CharField(max_length=FIELD_LENGTHS['char_choices'], default=list, null=True, blank=True)
    )
    paid_add_ons = ArrayField(
        models.CharField(max_length=FIELD_LENGTHS['char_choices'], default=list, null=True, blank=True)
    )
    # End new fields

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=STATUSES, default=STATUS_ACTIVE)

    def get_title(self):
        if self.product:
            return self.product.name

        return self.custom_product_name

    def get_car_title(self):
        if self.custom_car_name:
            car_title = "{} - {}".format(self.custom_car_name, self.car_year)
            if self.car_make:
                car_title = "{} - {}".format(self.car_make.name, car_title)

        else:
            car_title = str(self.car_trim or '-')

        return car_title

    def get_car_trim(self):
        return self.custom_car_name or self.car_trim.get_title_with_model()

    def get_product_logo(self):
        if self.product:
            return self.product.get_logo()

        return None

    def validate_ownership(self):
        if self.customer.company != self.company:
            raise ValidationError('The selected customer does not belong to this company')

        if self.deal and self.deal.customer != self.customer:
            raise ValidationError('Deal belongs to a different customer than is selected')

    def save(self, *args, **kwargs):
        self.validate_ownership()
        super(Policy, self).save(*args, **kwargs)

        if self.deal:
            Algolia().upsert_motor_deal_record(self.deal)
        else:
            Algolia().upsert_motor_policy_record(self)

    def __str__(self):
        return '{} - {} - {}'.format(self.reference_number, self.get_title(), self.customer.name)

    def get_policy_expiry_status(self):
        return 'active' if self.get_policy_expires_in() >= 0 else 'expired'

    def get_policy_expires_in(self):
        if not self.policy_expiry_date:
            return 0

        return (self.policy_expiry_date - datetime.date.today()).days

    def get_selected_product_premium(self):
        if self.deal:
            product = self.deal.quote.get_least_quoted_product()

            if product:
                return product.get_sale_price()

        return None

    def formatted_created_on(self):
        diff = (tz_now() - self.created_on).days

        if diff:
            return '{} {} ago'.format(
                diff, 'day' if diff == 1 else 'days')
        else:
            return naturaltime(self.created_on)

    def formatted_updated_on(self):
        diff = (tz_now() - self.updated_on).days

        if diff:
            return '{} {} ago'.format(
                diff, 'day' if diff == 1 else 'days')
        else:
            return naturaltime(self.updated_on)

    def get_attachments(self):
        return self.attachments.order_by('created_on')

    def get_policy_document_url(self):
        return '{}{}'.format(self.policy_document.url, settings.AZURE_STORAGE_SHARED_TOKEN) if self.policy_document else ''

    def get_policy_document_name(self):
        if self.policy_document:
            return self.policy_document.name.split('/')[-1]

    def get_invoice_document_name(self):
        if self.policy_document:
            return self.policy_document.name.split('/')[-1]

    def get_invoice_document_url(self):
        return '{}{}'.format(self.invoice_document.url, settings.AZURE_STORAGE_SHARED_TOKEN) if self.invoice_document else ''

    def get_renewal_deal(self):
        try:
            return self.deal_policy_renewed_for.order_by('-id')[0]
        except IndexError:
            return None
