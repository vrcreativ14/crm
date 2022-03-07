import random
import string
import os
from accounts.models import UserProfile
from core.mixins import AuditTrailMixin
# from customers.models import Customer
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from mortgage.constants import *


def reference_number():
    pk = (
        "".join(random.choices(string.ascii_uppercase, k=4))
        + "".join(random.choices(string.digits, k=4))
        + "".join(random.choices(string.ascii_uppercase, k=4))
    )

    if not Quote.objects.filter(reference_number=pk).exists():
        return pk

    reference_number()


def order_number():
    pk = (
        "OD".join(random.choices(string.ascii_uppercase, k=2))
        + "".join(random.choices(string.digits, k=4))
        + "".join(random.choices(string.ascii_uppercase, k=4))
    )
    if not Order.objects.filter(order_number=pk).exists():
        return pk

    order_number()


def get_govt_fee():
    return GovernmentFee.objects.last()

def get_banksample_upload_path(self, filename):
        return f'{settings.BASE_DIR}/banksamples/'


class SingleInstanceMixin(object):
    """Makes sure that no more than one instance of a given model is created."""

    def clean(self):
        model = self.__class__
        if (model.objects.count() > 0 and self.id != model.objects.get().id):
            raise ValidationError("Can only create 1 %s instance" % model.__name__)
        super(SingleInstanceMixin, self).clean()


class Stage(models.Model):
    title = models.CharField(max_length=10)


class BankManager(models.Manager):
    @staticmethod
    def bank_info(*args, **kwargs):
        bank = Bank.objects.get(pk=kwargs["pk"])
        bank_ins = kwargs.get("bank_ins")
        if not bank_ins:
            bank_ins = Bank.objects.get(pk=kwargs["pk"]).bank_interest_rates.get(is_default=True)
        setattr(bank, "interest_rate", bank_ins.interest_rate)
        setattr(bank, "eibor_rate", bank_ins.eibor_rate)
        setattr(bank, "eibor_duration", bank_ins.eibor_duration)
        setattr(bank, "introduction_period_in_years", bank_ins.introduction_period_in_years)
        setattr(bank, "post_introduction_rate", bank_ins.post_introduction_rate)
        setattr(bank, "eibor_post_duration", bank_ins.eibor_post_duration)

        return bank


class Eibor(SingleInstanceMixin, models.Model):
    eibor_rate_0m = models.FloatField(default=0, help_text="Value must be in percentage", verbose_name="0M")
    eibor_rate_1m = models.FloatField(help_text="Value must be in percentage", verbose_name="1M")
    eibor_rate_3m = models.FloatField(help_text="Value must be in percentage", verbose_name="3M")
    eibor_rate_6m = models.FloatField(help_text="Value must be in percentage", verbose_name="6M")

    def __str__(self):
        return f'{self.eibor_rate_0m}'


class EiborPost(SingleInstanceMixin, models.Model):
    eibor_post_rate_0m = models.FloatField(default=0, help_text="Value must be in percentage", verbose_name="0M")
    eibor_post_rate_1m = models.FloatField(help_text="Value must be in percentage", verbose_name="1M")
    eibor_post_rate_3m = models.FloatField(help_text="Value must be in percentage", verbose_name="3M")
    eibor_post_rate_6m = models.FloatField(help_text="Value must be in percentage", verbose_name="6M")

    def __str__(self):
        return f'{self.eibor_post_rate_0m}'


class GovernmentFee(models.Model):
    trustee_center_fee = models.FloatField(help_text="Do not include the vat here")
    property_fee_rate = models.FloatField(help_text="Land department property registration fee in percentage")
    property_fee_addition = models.IntegerField(help_text="Land department property registration fixed fee in numbers")
    mortgage_fee_rate = models.FloatField(help_text="Land department property registration fee in percentage")
    mortgage_fee_addition = models.IntegerField(help_text="Land department property registration fixed fee in numbers")
    real_state_fee = models.FloatField(help_text="Real estate fee in percentage excluding vat")
    created_date = models.DateField(auto_now_add=True)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        if not self._state.adding:
            if self._loaded_values['trustee_center_fee'] != self.trustee_center_fee:
                self.trustee_center_fee = self.trustee_center_fee + self.trustee_center_fee * VAT_PERCENTAGE 
        else:
            self.trustee_center_fee = self.trustee_center_fee + self.trustee_center_fee * VAT_PERCENTAGE 

        super(GovernmentFee, self).save(*args, **kwargs)

    def __str__(self):
        return "Government Fee"


class Bank(models.Model):
    PUBLIC_STORAGE = default_storage
    bank_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=False)
    logo = models.ImageField(upload_to="", storage=PUBLIC_STORAGE, blank=True, default='upload/insure-nex-logo.png')

    # Property valuation fee
    property_valuation_fee = models.IntegerField()
    # Bank Processing Fee
    bank_processing_fee_rate = models.FloatField(blank=True, null=True, help_text="Value must be in percentage")
    # bank_processing_fee_extra = models.IntegerField()
    # max_bank_processing_fee = models.IntegerField()
    life_insurance_monthly_rate = models.FloatField(help_text="Value must be in percentage")
    property_insurance_yearly_rate = models.FloatField(help_text="Value must be in percentage")
    full_settlement_percentage = models.FloatField(default=0, blank=False)
    full_settlement_max_value = models.FloatField(default=0, blank=False)
    free_partial_payment_per_year = models.IntegerField(default=0, blank=False)
    add_fees_to_loan_amount = models.BooleanField()
    objects = BankManager()
    sample_form = models.FileField(upload_to='upload/', blank=True, null=True, default="upload/sample_word.pdf")
    extra_financing_allowed = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Bank"
        verbose_name_plural = "Banks"

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        super(Bank, self).save(*args, **kwargs)


class BankInterestRate(models.Model):
    is_default = models.BooleanField(default=True)
    interest_rate = models.FloatField(default=0, blank=False)
    eibor_rate = models.FloatField(help_text="Value must be in percentage")
    eibor_duration = models.CharField(max_length=2, choices=EIBOR_DURATIONS, default='0M')
    post_introduction_rate = models.FloatField(blank=True, null=True)
    introduction_period_in_years = models.FloatField(blank=True, null=True)
    eibor_post_rate = models.FloatField(help_text="Value must be in percentage", default=0)
    eibor_post_duration = models.CharField(max_length=2, choices=EIBOR_DURATIONS, default='0M')
    serial_number = models.PositiveIntegerField(editable=False)
    bank = models.ForeignKey(Bank, related_name="bank_interest_rates", on_delete=models.CASCADE)

    # def __str__(self):
    #     return f"{self.bank} - {self.serial_number}"

    def clean(self):
        if hasattr(self, "bank"):
            cc = self.bank.bank_interest_rates.all().filter(is_default=True)
            if self.is_default:
                if cc.count() >= 1:
                    if self.pk not in cc.values_list("pk", flat=True):
                        raise ValidationError(
                            _(
                                "First uncheck Is default for all Bank Interest rate then select only one default rate"
                            )
                        )

    def save(self, *args, **kwargs):
        self.serial_number = self.bank.bank_interest_rates.count() + self.bank.bank_interest_rates.count()
        super(BankInterestRate, self).save(*args, **kwargs)

    @property
    def get_rate(self):
        return f"{self.interest_rate}% + {self.eibor_rate}%"


class CustomerProfile(models.Model):
    customer = models.OneToOneField(
        "customers.Customer",
        related_name="customer_mortgage_profiles",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer}"



class Deal(AuditTrailMixin, models.Model):
    deal_id = models.AutoField(primary_key=True, db_index=True)
    stage = models.CharField(max_length=50, choices=DEAL_STAGES, default=STAGE_NEW)
    deal_type = models.CharField(max_length=50, choices=DEAL_TYPES, default=DEAL_TYPE_NEW)
    quote_sent = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=DEAL_STATUSES, default=STATUS_ACTIVE)
    property_price = models.BigIntegerField(default=0, blank=False)
    loan_amount = models.BigIntegerField(default=0, blank=True)
    down_payment = models.BigIntegerField(default=0, blank=False)
    extra_financing = models.FloatField(blank=True, null=True)
    expat = models.CharField(max_length=50, choices=DEAL_EXPATS, default=EXPATS_NO)
    tenure = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(360)])
    l_tv = models.FloatField(blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)
    processed_status = ArrayField(
        models.CharField(max_length=20, blank=True, null=True, choices=DEAL_STATUSES),
        size=8,
        blank=True, null=True,)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deal_owner",
    )
    referrer = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="deal_user"
    )
    assigned_to = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="deal_assigned_to")
    customer = models.ForeignKey(
        'customers.Customer', null=True, on_delete=models.SET_NULL, related_name="deal_customer"
    )
    govt_fee = models.ForeignKey(
        GovernmentFee, null=True, on_delete=models.SET_DEFAULT, default=get_govt_fee, related_name="deal_govt_fee"
    )
    notes = GenericRelation('core.Note')
    tasks = GenericRelation('core.Task')
    is_property_reg_financed = models.BooleanField(default=False, null=True)
    is_real_estate_fee_financed = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f"{self.customer.name if self.customer else '' } - AED ({int(self.property_price):,})"

    @property
    def passport_files(self):
        return self.dealfiles_set.filter(type='passport').order_by('-pk')

    @property
    def visa_files(self):
        return self.dealfiles_set.filter(type='visa').order_by('-pk')

    @property
    def bank_application_form_files(self):
        return self.dealfiles_set.filter(type='bank-application-form').order_by('-pk')
    
    @property
    def salary_certificate_files(self):
        return self.dealfiles_set.filter(type='salary-certificate').order_by('-pk')

    @property
    def emirates_id_front_files(self):
        return self.dealfiles_set.filter(type='emirates-id-front').order_by('-pk')

    @property
    def bank_statement_files(self):
        return self.dealfiles_set.filter(type='bank-statement').order_by('-pk')

    @property
    def emirates_id_back_files(self):
        return self.dealfiles_set.filter(type='emirates-id-back').order_by('-pk')
    
    @property
    def payslips_files(self):
        return self.dealfiles_set.filter(type='payslips').order_by('-pk')

    @property
    def memorandum_of_understanding_files(self):
        return self.dealfiles_set.filter(type='memorandum-of-understanding').order_by('-pk')

    @property
    def property_title_deed_files(self):
        return self.dealfiles_set.filter(type='property-title-deed').order_by('-pk')

    @property
    def sellers_emirates_id_front_files(self):
        return self.dealfiles_set.filter(type='sellers-emirates-id-front').order_by('-pk')

    @property
    def sellers_emirates_id_back_files(self):
        return self.dealfiles_set.filter(type='sellers-emirates-id-back').order_by('-pk')

    @property
    def sellers_passport_files(self):
        return self.dealfiles_set.filter(type='sellers-passport').order_by('-pk')

    @property
    def sellers_visa_files(self):
        return self.dealfiles_set.filter(type='sellers-visa').order_by('-pk')

    @property
    def general_files(self):
        return self.dealfiles_set.filter(type='general').order_by('-pk')

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def clean(self):
        try:
            if self.property_price < self.down_payment:
                raise ValidationError("Loan Amount can not be greater than property price")
            if not self.down_payment and not self.property_price:
                raise ValidationError("Please provide Property Price and Loan Amount ")
        except Exception as e:
            if type(e) == TypeError:
                raise ValidationError("Invalid character")
            elif type(e) == ValidationError:
                raise e

    def get_attachments(self):
        return self.attachments.order_by("-created_on")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            if self._loaded_values['loan_amount'] != self.loan_amount:
                self.down_payment = self.property_price - self.loan_amount
            if self._loaded_values['down_payment'] != self.down_payment:
                self.loan_amount = self.property_price - self.down_payment
        else:
            self.loan_amount = self.property_price - self.down_payment
        #self.l_tv = round(((self.down_payment / self.property_price) * 100), 2)          
        self.l_tv = round(((abs(self.property_price - self.down_payment) / self.property_price) * 100), 2)           #formula change as suggested for Mortgage Amount (LTV %)
        if hasattr(self, "mortgage_quote_deals"):
            if self.mortgage_quote_deals.is_sent and self.stage == STAGE_QUOTE:
                self.status == STATUS_CLIENT
        if not self.govt_fee:
            self.govt_fee = GovernmentFee.objects.last()

        if self.stage == STAGE_QUOTE and self._loaded_values['stage'] == 'new':
            SubStage.objects.create(deal=self, stage=self.stage, sub_stage=SELECT_BANK)
        super(Deal, self).save(*args, **kwargs)

    @property
    def current_sub_stage(self):
        if SubStage.objects.filter(deal=self,stage=self.stage).exists():
            return SubStage.objects.filter(deal=self,stage=self.stage).last()

    @property
    def extra_financing(self):
        return 0

    def get_title(self):
        return f"{self.property_price}"

    def get_order(self):
        try:
            return Order.objects.filter(deal=self)
        except Order.DoesNotExist:
            return None

    def get_quote(self):
        try:
            return Quote.objects.filter(deal=self)
        except Quote.DoesNotExist:
            return None

    def get_tags(self):
        tags = []
        quote = self.get_quote()

        if quote and self.stage == STAGE_QUOTE:
            if quote.status == Quote.status:
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
        elif self.stage == STAGE_FINAL_OFFER:
            order = self.get_order()
            if order:
                if order.status == order.STATUS_PAID:
                    tags.append('Paid')
                else:
                    tags.append('Unpaid')
        elif self.stage == STAGE_ClosedWON:
            order = self.get_order()
            if order:
                if order.status == STATUS_PAID:
                    tags.append('Paid')
                else:
                    tags.append('Unpaid')

        return tags

class IssuedDeal(models.Model):
    deal = models.OneToOneField(Deal, on_delete=models.CASCADE, related_name="deal_issued")
    property_price = models.BigIntegerField(default=0, blank=False)
    loan_amount = models.BigIntegerField(default=0, blank=True)
    tenure = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(360)])
    l_tv = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.deal.deal_id}"

def deal_files_directory(instance,filename):
    return "deals/" + str(instance.deal.deal_id) + "/" + str(instance.type) + "/" + filename
class DealFiles(models.Model):
    ATTACHMENT_TYPE = [
        ("passport","passport"),
        ("visa","visa"),
        ("bank-application-form","bank-application-form"),
        ("salary-certificate","salary-certificate"),
        ("emirates-id-front","emirates-id-front"),
        ("bank-statement","bank-statement"),
        ("emirates-id-back","emirates-id-back"),
        ('payslips',"payslips"),
        ("memorandum-of-understanding","memorandum-of-understanding"),
        ("property-title-deed","property-title-deed"),
        ("sellers-emirates-id-front","sellers-emirates-id-front"),
        ("sellers-emirates-id-back","sellers-emirates-id-back"),
        ("sellers-visa","sellers-visa"),
        ("sellers-passport","sellers-passport"),
        ("general","general")
    ]
    deal = models.ForeignKey(Deal,on_delete=models.CASCADE)
    type = models.CharField(choices=ATTACHMENT_TYPE,default='passport',max_length=100)
    file = models.FileField(upload_to=deal_files_directory,null=True,blank=True)

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class Order(models.Model):
    order_number = models.CharField(primary_key=True, default=order_number, max_length=15)
    status = models.CharField(max_length=100, choices=PAYMENT_STATUSES, default=STATUS_UNPAID)
    created_by_agent = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_void = models.BooleanField(default=False)

    mortgage_by = models.CharField(max_length=250, default="", blank=True)
    payment_amount = models.FloatField( blank=True, null=True)
    discount = models.FloatField(default=0)
    policy_start_date = models.DateField(blank=True)
    bank_reference_number = models.CharField(max_length=250, default="", blank=True, null=True)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name="order_bank")
    deal = models.OneToOneField(Deal, on_delete=models.CASCADE, related_name="deal_bank")

    def __str__(self):
        return f"{self.order_number}-{self.mortgage_by}"


class Lead(models.Model):
    property_price = models.BigIntegerField()
    load_amount = models.BigIntegerField()
    extra_financing = models.BigIntegerField()
    expat = models.CharField(max_length=45)
    tenure = models.CharField(max_length=45)
    l_tv = models.CharField(max_length=45)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    user = models.ForeignKey(User, related_name="mortgage_lead_user", on_delete=models.CASCADE)
    referrer = models.ForeignKey(UserProfile, related_name="mortgage_lead_user", on_delete=models.CASCADE)
    deals = models.ForeignKey(Deal, related_name="mortgage_leads_deal", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.property_price}-{self.tenure}"


class Quote(models.Model):
    reference_number = models.CharField(max_length=50, default=reference_number)
    number_of_view = models.IntegerField(default=0)
    is_segmented = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    deals = models.OneToOneField(Deal, related_name="mortgage_quote_deals", on_delete=models.CASCADE)
    bank = models.ManyToManyField(Bank, related_name="mortgage_bank_quotes")

    def __str__(self):
        return f"{self.deals}-{self.reference_number}"

    def save(self, *args, **kwargs):
        if not self.number_of_view:
            self.number_of_view = 0
        if self.is_sent and self.deals.stage == STAGE_QUOTE:
            deal = self.deals
            self.deals.status == STATUS_CLIENT
            self.deals.save()
        super(Quote, self).save(*args, **kwargs)

    def payment_and_interests(self):
        temp = []
        for bank in self.bank.all():
            from mortgage.utils import BankHelper
            temp.append(
                BankHelper(
                    bank,
                    self.deals.property_price,
                    self.deals.loan_amount,
                    self.deals.tenure,
                )
            )
        return temp


class SegmentedRate(models.Model):
    quote = models.ForeignKey(
        Quote, related_name="quote_segmented_quote", on_delete=models.CASCADE
    )
    rate = models.ForeignKey(
        BankInterestRate, related_name="quote_segmented_rate", on_delete=models.CASCADE
    )
    bank = models.ForeignKey(
        Bank, related_name="quote_segmented_bank", on_delete=models.CASCADE
    )


class Approval(models.Model):
    
    name = models.CharField(max_length=200, choices=DOCUMENT_NAMES)
    deal = models.ForeignKey(
        Deal,
        related_name="mortgage_quote_approvals",
        on_delete=models.SET_NULL,
        null=True,
    )


class PreApproval(Approval):
    attachments = GenericRelation("core.Attachment")

    def __str__(self) -> str:
        return f"{self.name}"


class PostApproval(Approval):
    attachments = GenericRelation("core.Attachment")

    def __str__(self) -> str:
        return f"{self.deal}"


class ProcessEmail(models.Model):
    from_address = models.EmailField()
    to_address = models.EmailField()
    subject = models.CharField(max_length=2000)
    text = models.TextField()
    attachments = GenericRelation("core.Attachment")
    html = models.TextField()
    cc_addresses = ArrayField(base_field=models.EmailField())
    bcc_addresses = ArrayField(base_field=models.EmailField())
    deal = models.ForeignKey(Deal, related_name='deal_processed_email', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.deal}- {self.deal.stage}"


class SubStage(models.Model):
    deal = models.ForeignKey(Deal, related_name='deal_substages', on_delete=models.CASCADE)
    stage = models.CharField(max_length=50, choices=DEAL_STAGES)
    sub_stage = models.CharField(max_length=50, choices=SUB_STAGES)

    def __str__(self):
        return f"{self.stage}-{self.sub_stage}"

    class Meta:
        unique_together = ['deal', 'stage', 'sub_stage']

