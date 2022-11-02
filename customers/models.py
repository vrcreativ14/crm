import hashlib
import datetime

from dateutil import relativedelta

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from core.mixins import AuditTrailMixin
from core.utils import get_initials_from_the_name
from core.algolia import Algolia

from felix.constants import COUNTRIES
from felix.constants import FIELD_LENGTHS, GENDER_CHOICES, MARITAL_STATUS_LIST
from healthinsurance.models.policy import HealthPolicy

from motorinsurance.models import Deal as MotorDeals, Policy
from mortgage.models import Deal as MortgageDeals
from healthinsurance.models.deal import Deal as HealthDeals


class Customer(AuditTrailMixin, models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_DELETED = 'deleted'
    STATUSES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DELETED, 'Deleted')
    )
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE)

    name = models.CharField(max_length=FIELD_LENGTHS['name'])
    email = models.EmailField(max_length=FIELD_LENGTHS['email'], blank=True)
    phone = models.CharField(max_length=FIELD_LENGTHS['phone'], blank=True)

    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=GENDER_CHOICES, blank=True)
    marital_status = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=MARITAL_STATUS_LIST, blank=True)
    nationality = models.CharField(max_length=2, choices=COUNTRIES, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    notes = GenericRelation('core.Note')
    attachments = GenericRelation('core.Attachment')

    status = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=STATUSES, default=STATUS_ACTIVE)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return "{} - {}".format(self.name, self.email)

    def save(self, entity=None, *args, **kwargs):
        super(Customer, self).save(*args, **kwargs)
        self.entity = entity
        if hasattr( self, 'customer_mortgage_profiles'):
            self.entity = "Mortgage"
        Algolia().upsert_customer_record(self)

    def get_motor_deals(self):
        return MotorDeals.objects.filter(customer=self)

    def get_mortgage_deals(self):
        return MortgageDeals.objects.filter(customer=self)

    def get_health_deals(self):
        return HealthDeals.objects.filter(customer=self)

    def get_whatsapp_formatted_number(self):
        return ''.join([n for n in self.phone if n.isdigit()])

    def get_non_deleted_deals(self):
        return self.get_motor_deals().exclude(is_deleted=True).order_by('-created_on')

    def get_non_deleted_mortgage_deals(self):
        return self.get_mortgage_deals().exclude(status="deleted").order_by('-created_date')

    def get_non_deleted_health_deals(self):
        return self.get_health_deals().exclude(status="deleted").order_by('-created_on')

    def get_open_deals(self):
        return self.get_motor_deals().filter(is_deleted=False).exclude(
            stage__in=[MotorDeals.STAGE_WON, MotorDeals.STAGE_LOST]).order_by('-created_on')

    def get_mortgage_open_deals(self):
        return self.get_mortgage_deals().exclude(status='deleted').order_by('-created_date')

    def get_initials(self):
        return get_initials_from_the_name(self.name or self.email)

    def get_policies(self):
        return Policy.objects.filter(customer=self, status=Policy.STATUS_ACTIVE).order_by('-created_on')

    def get_health_policies(self):
        return HealthPolicy.objects.filter(customer=self, status=Policy.STATUS_ACTIVE).order_by('-created_on')

    def get_active_policies(self):
        return self.get_policies().filter(policy_expiry_date__gte=datetime.date.today()).order_by('-created_on')

    def get_active_health_policies(self):
        return self.get_health_policies().filter(expiry_date__gte=datetime.date.today()).order_by('-created_on')

    def get_attachments(self):
        return self.attachments.order_by('-created_on')

    def get_age(self):
        if self.dob is None:
            return None

        age = relativedelta.relativedelta(datetime.date.today(), self.dob)

        return age.years

    def get_email_hash(self):
        if self.email:
            return hashlib.md5(self.email.encode()).hexdigest()

        return None

    def is_older_than(self, years):
        if self.dob is None:
            return False

        age_diff = relativedelta.relativedelta(datetime.date.today(), self.dob)
        return age_diff.years >= years
