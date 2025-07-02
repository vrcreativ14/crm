import logging
from datetime import date

from algoliasearch.helpers import AlgoliaException
from dateutil import relativedelta
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now as tz_now

from core.algolia import Algolia
from core.mixins import AuditTrailMixin
from felix.constants import COUNTRIES, FIELD_LENGTHS, CAR_YEARS_LIST, EMIRATES_LIST
from motorinsurance.constants import (
    LEAD_TYPES, TOP_TIER_INSURERS, INSURANCE_TYPES, NO_CLAIMS,
    LICENSE_AGE_LIST, LEAD_TYPES_NEW_CAR, NO_CLAIMS_THIS_YEAR, NO_CLAIMS_CANT_REMEMBER
)
from motorinsurance.models.policy import Policy
from motorinsurance.models.quote import Quote, Order
from motorinsurance_shared.models import CarMake, CarTrim


class CustomerProfile(AuditTrailMixin, models.Model):
    customer = models.OneToOneField('customers.Customer', on_delete=models.CASCADE,
                                    related_name="motorinsurancecustomerprofile")

    first_license_age = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=LICENSE_AGE_LIST, blank=True)
    uae_license_age = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=LICENSE_AGE_LIST, blank=True)

    first_license_country = models.CharField(
        max_length=2, choices=COUNTRIES, blank=True)
    first_license_issue_date = models.DateField(null=True)
    uae_license_issue_date = models.DateField(null=True)

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)


class Deal(AuditTrailMixin, models.Model):
    STAGE_NEW = 'new'
    STAGE_QUOTE = 'quote'
    STAGE_ORDER = 'order'
    STAGE_HOUSEKEEPING = 'housekeeping'
    STAGE_WON = 'won'
    STAGE_LOST = 'lost'

    STATUS_DELETED = 'yes'

    STAGES = (
        (STAGE_NEW, 'New Deal'),
        (STAGE_QUOTE, 'Quote'),
        (STAGE_ORDER, 'Order'),
        (STAGE_HOUSEKEEPING, 'Housekeeping'),
        (STAGE_WON, 'Won'),
        (STAGE_LOST, 'Lost')
    )

    DEAL_TYPE_NEW = 'new'
    DEAL_TYPE_RENEWAL = 'renewal'
    DEAL_TYPE_DUPLICATE = 'duplicate'

    TYPES = (
        ('new', 'New'),
        ('duplicate', 'Duplicate'),
        ('renewal', 'Renewal')
    )
    stage = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=STAGES, default=STAGE_NEW)

    deal_type = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=TYPES, default=DEAL_TYPE_NEW)

    is_deleted = models.BooleanField(default=False)
    # Tracks if an email was EVER sent to the customer from the portal about the quote in this deal
    quote_sent = models.BooleanField(default=False)

    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.CASCADE)

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE)
    lead = models.ForeignKey('motorinsurance.Lead',
                             on_delete=models.SET_NULL, null=True, blank=True)

    assigned_to = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)

    # Initially was created to check if deal is a producer's deal.
    # But now using this fields to set "Referrer" or owner of the deal.
    producer = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='deal_producer')

    lead_type = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=LEAD_TYPES)

    car_year = models.CharField(max_length=4, choices=CAR_YEARS_LIST)
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    car_trim = models.ForeignKey(CarTrim, null=True, on_delete=models.SET_NULL)
    custom_car_name = models.CharField(
        max_length=FIELD_LENGTHS['name'], blank=True)

    chassis_number = models.CharField(max_length=20, blank=True)

    # This field holds the full car name so we can do a text search on the car name
    cached_car_name = models.CharField(
        max_length=FIELD_LENGTHS['name'], blank=True, editable=False)

    current_insurer = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=TOP_TIER_INSURERS, blank=True)
    current_insurance_type = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=INSURANCE_TYPES, blank=True)

    date_of_first_registration = models.DateField(null=True, blank=True)
    place_of_registration = models.CharField(
        max_length=2, choices=EMIRATES_LIST, blank=True)

    vehicle_insured_value = models.DecimalField(
        max_digits=10, decimal_places=2)

    years_without_claim = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=NO_CLAIMS, blank=True)
    claim_certificate_available = models.BooleanField(default=False, null=True)

    number_of_passengers = models.PositiveSmallIntegerField(default=0)

    # Car details
    private_car = models.BooleanField(default=True, null=True)
    car_unmodified = models.BooleanField(default=True, null=True)
    car_gcc_spec = models.BooleanField(default=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    notes = GenericRelation('core.Note')
    tasks = GenericRelation('core.Task')

    # Allow up to 3 email addresses
    cc_emails = models.CharField(
        max_length=FIELD_LENGTHS['email'] * 3, blank=True)
    # Allow up to 3 email addresses
    bcc_emails = models.CharField(
        max_length=FIELD_LENGTHS['email'] * 3, blank=True)

    renewal_for_policy = models.ForeignKey(
        Policy, null=True, blank=True, on_delete=models.SET_NULL, related_name='deal_policy_renewed_for')

    attachments = GenericRelation('core.Attachment')

    def get_order(self):
        try:
            return self.order_set.get(is_void=False)
        except Order.DoesNotExist:
            return None

    @property
    def quote(self):
        try:
            return self.quote_set.get(is_deleted=False)
        except Quote.DoesNotExist:
            return None

    def validate_ownership(self):
        if self.assigned_to and self.assigned_to.userprofile.company != self.company:
            raise ValidationError(
                'You can not assign a deal belonging to company {} to an agent of another company'.format(
                    self.company
                )
            )

        if self.customer.company != self.company:
            raise ValidationError(
                'You can not assign a deal belonging to company {} to a customer of another company'.format(
                    self.company
                )
            )

        if self.lead and self.lead.company != self.company:
            raise ValidationError(
                'You can not attach a deal belonging to company {} to a lead from another company'.format(
                    self.company
                )
            )

    def save(self, *args, **kwargs):
        no_algolia_update = kwargs.pop('no_algolia_update', False)

        self.validate_ownership()

        if self.car_trim:
            self.cached_car_name = self.car_trim.get_full_title()
        else:
            self.cached_car_name = f'{self.car_year} {self.car_make.name} {self.custom_car_name}'

        super(Deal, self).save(*args, **kwargs)

        if not no_algolia_update:
            self.update_in_algolia()

    def update_in_algolia(self):
        try:
            Algolia().upsert_motor_deal_record(self)
        except AlgoliaException as e:
            logger = logging.getLogger('api.algolia')
            logger.error('Error while updating deal %d, in algolia. Error %s', self.pk, str(e))

    def get_car_title(self):
        if self.custom_car_name:
            car_title = "{} - {} - {}".format(self.car_make.name,
                                              self.custom_car_name, self.car_year)
        else:
            car_title = str(self.car_trim)

        return car_title

    def get_car_trim(self):
        return self.custom_car_name or self.car_trim.get_title_with_model()

    def is_new_car(self):
        return self.lead_type == LEAD_TYPES_NEW_CAR

    def __str__(self):
        return self.get_title()

    def get_title(self):
        return f'{self.customer.name} ({self.get_car_title()})'

    def get_quotes(self):
        return Quote.objects.filter(deal=self)

    def get_policies(self):
        return Policy.objects.filter(deal=self)

    def get_active_policies(self):
        return self.get_policies().filter(status=Policy.STATUS_ACTIVE).order_by('-created_on')

    def get_payments(self):
        return Order.objects.filter(deal=self).order_by('-created_on')

    def get_non_deleted_payments(self):
        return self.get_payments().exclude(status=Order.STATUS_DELETED).order_by('-created_on')

    def get_paid_payments(self):
        return self.get_payments().filter(status=Order.STATUS_PAID).order_by('-created_on')

    def get_unpaid_payments(self):
        return self.get_payments().filter(status=Order.STATUS_UNPAID).order_by('-created_on')

    def get_attachments(self):
        return self.attachments.order_by('-created_on')

    def is_publicly_modifiable(self):
        """The deal can only be modified from the public frontend (quote comparison page, etc) if it is in certain
        stages."""
        return self.stage == self.STAGE_QUOTE

    def is_active(self):
        return not self.is_deleted and self.stage not in [self.STAGE_WON, self.STAGE_LOST]

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

    def get_tags(self):
        tags = []
        quote = self.quote

        if self.is_deleted:
            tags.append('Deleted')

        if quote and self.stage == self.STAGE_QUOTE:
            if quote.status == Quote.STATUS_PUBLISHED:
                tags.append('Published')
            else:
                tags.append('Unpublished')

            if quote.number_of_views > 0:
                tags.append(f'Viewed {quote.number_of_views} time(s)')
            else:
                if self.quote_sent:
                    tags.append('Sent')
                else:
                    tags.append('Not sent')
        elif self.stage == self.STAGE_ORDER:
            order = self.get_order()
            if order:
                if order.status == order.STATUS_PAID:
                    tags.append('Paid')
                else:
                    tags.append('Unpaid')

            try:
                self.policy
                tags.append('Policy issued')
            except Policy.DoesNotExist:
                tags.append('Policy unissued')
        elif self.stage == self.STAGE_HOUSEKEEPING:
            order = self.get_order()
            if order:
                if order.status == order.STATUS_PAID:
                    tags.append('Paid')
                else:
                    tags.append('Unpaid')
        elif self.stage == self.STAGE_WON:
            order = self.get_order()
            if order:
                if order.status == order.STATUS_PAID:
                    tags.append('Paid')
                else:
                    tags.append('Unpaid')

        return tags

    def get_age_of_car_since_registration(self):
        if self.is_new_car():
            return 1

        if self.date_of_first_registration is None:
            return None

        today = date.today()
        car_age = relativedelta.relativedelta(today, self.date_of_first_registration)
        return car_age.years + 1

    def has_no_claims_history(self):
        return (self.years_without_claim and
                self.years_without_claim not in [NO_CLAIMS_CANT_REMEMBER, NO_CLAIMS_THIS_YEAR])
