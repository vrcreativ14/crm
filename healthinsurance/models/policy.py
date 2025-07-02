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
from felix.constants import FIELD_LENGTHS
from healthinsurance.models.deal import Deal
from accounts.models import User
import os

def deal_files_directory(instance,filename):
    return "policy/" + str(instance.policy.id) + "/" + str(instance.type) + "/" + filename




class HealthPolicy(AuditTrailMixin, models.Model):
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

    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, related_name='health_policy_company')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='health_policy_customer')
    plan = models.ForeignKey('healthinsurance_shared.Plan', on_delete=models.CASCADE, null=True, blank=True)
    referrer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="health_policy_referrer")
    policy_number = models.CharField(max_length=100)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    basmah_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    total_premium_vat_inc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deal = models.OneToOneField(Deal, null=True, on_delete=models.SET_NULL, blank=True, related_name='health_policy_deal')
    user = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL, blank=True)
    reference_number = models.CharField(max_length=FIELD_LENGTHS['reference_numbers'], blank=True)
    invoice_number = models.CharField(max_length=FIELD_LENGTHS['reference_numbers'], blank=True)
    attachments = GenericRelation('core.Attachment')
    start_date = models.DateField(blank=True)
    expiry_date = models.DateField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=STATUSES, default=STATUS_ACTIVE)
    is_policy_link_active = models.BooleanField(default=True)
    policy_link_reactivated_on = models.DateTimeField(blank=True, null=True)

    def get_product_logo(self):
        if self.plan:
            return self.plan.get_logo()

        return None

    def get_title(self):
        if self.deal.selected_plan:
            return self.deal.selected_plan.name

        return self.plan.name

    def validate_ownership(self):
        if self.customer.company != self.company:
            raise ValidationError('The selected customer does not belong to this company')

        if self.deal and self.deal.customer != self.customer:
            raise ValidationError('Deal belongs to a different customer than is selected')

    def __str__(self):
        return '{} - {}'.format(self.reference_number, self.customer.name)

    def get_policy_expiry_status(self):
        return 'active' if self.get_policy_expires_in() >= 0 else 'expired'

    def get_policy_expires_in(self):
        if not self.expiry_date:
            return 0

        return (self.expiry_date - datetime.date.today()).days

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

    def get_policy_link_status(self):
        if (tz_now() - self.created_on).days > 14:  #inactive after 14 days
                if(self.policy_link_reactivated_on):
                    if (tz_now() - self.policy_link_reactivated_on).days > 14:
                        return False
                    else:
                        return self.is_policy_link_active
                else:
                    return False
        else:
            return True                        #active

    def set_policy_link_status(self):
        if (tz_now() - self.created_on).days > 14:
            self.is_policy_link_active = False                        #inactive after 14 days
            self.save()
        else:
            self.is_policy_link_active = True
            self.save()
    # def get_renewal_deal(self):
    #     try:
    #         return self.deal_policy_renewed_for.order_by('-id')[0]
    #     except IndexError:
    #         return None



class PolicyFiles(models.Model):
    ATTACHMENT_TYPE = [
        ("receipt_of_payment","receipt_of_payment"),
        ("tax_invoice","tax_invoice"),
        ("certificate_of_insurance","certificate_of_insurance"),
        ("medical_card","medical_card"),
        ("confirmation_of_cover","confirmation_of_cover"),               
        ("credit_note","credit_note"),     
        ("other_document","other_document"),     
    ]
    policy = models.ForeignKey(HealthPolicy,on_delete=models.CASCADE)
    type = models.CharField(choices=ATTACHMENT_TYPE,default='receipt-of-payment',max_length=100)
    file = models.FileField(upload_to=deal_files_directory,null=True,blank=True)

    @property
    def filename(self):
        return os.path.basename(self.file.name)
