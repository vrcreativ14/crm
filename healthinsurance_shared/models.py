from email.policy import default
from http.client import PAYMENT_REQUIRED
from locale import currency
from random import choices
from tabnanny import verbose
from django.core.exceptions import ValidationError
from django.db import models
from felix.constants import PUBLIC_STORAGE, FIELD_LENGTHS, COUNTRIES
from django.db.models import JSONField
from django.conf.urls.static import static
from django.utils.text import slugify
import uuid
import datetime
from healthinsurance.constants import COPAY_MODE, VARIABLE, DEAL_STAGES, LEVEL_OF_COVER, COMPREHENSIVE
#from django.contrib.contenttypes.fields import GenericRelation

class PlanManager(models.Manager):
    def get_non_filtered_queryset(self):
        return super(PlanManager, self).get_queryset()

    def get_queryset(self):
        return super(PlanManager, self).get_queryset().filter(is_active=True)

CURRENCIES = (
    ('AED','AED'),
    ('USD','USD'),
)

PAYMENT_FREQUENCY = (
    ('Annual','Annual'),
    ('Quarterly','Quarterly'),
    ('Monthly','Monthly'),
)

def get_document_upload_path(self, filename):
        """Returns a customer specific folder to write the policy document to.

        Defined first because we use it as a field parameter `upload_to`. Saving on a per customer folder allows us
        easy navigation when manually browsing the files."""
        if self.__class__ == Insurer:
            base_path = 'health_insurance_plan_/{}-{}'.format(self.pk, slugify(self.name))
        else:
            base_path = 'health_insurance_plan_/{}-{}'.format(self.insurer.pk, slugify(self.insurer.name))

        date_component = datetime.datetime.utcnow().strftime('%Y-%m-%d')

        return f'{base_path}/{date_component}_{uuid.uuid4().hex}_{filename}'


class PaymentFrequency(models.Model):
    frequency = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.frequency}'

class Area_Of_Cover(models.Model):
    area = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Area Of Cover"
        verbose_name_plural = "Area Of Cover"

    def __str__(self):
        return f'{self.area}'

class PharmacyCopay(models.Model):
    copayment = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.copayment}'

class DiagnosticsCopay(models.Model):
    copayment = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.copayment}'

class ConsultationCopay(models.Model):
    copayment = models.CharField(max_length=200)
    pharmacy_copay = models.ForeignKey(PharmacyCopay, on_delete=models.CASCADE, blank=True, null=True)
    diagnostics_copay = models.ForeignKey(DiagnosticsCopay, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.pharmacy_copay and self.diagnostics_copay:
            return f'{self.copayment};pharmacy_copay-{self.pharmacy_copay.copayment};diagnostics_copay-{self.diagnostics_copay.copayment}'
        else:
            return f'{self.copayment}'

class InpatientDeductible(models.Model):
    deductible = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.deductible}'

class Network(models.Model):
    network = models.CharField(max_length=500)

    def __str__(self):
        return f'{self.network}'

class AnnualLimit(models.Model):
     limit = models.CharField(max_length=200)
     
     def __str__(self):
            return f'{self.limit}'

class Physiotherapy(models.Model):
    sessions = models.CharField(max_length=200)
     
    def __str__(self):
            return f'{self.sessions}'

class PreExistingCover(models.Model):
    cover = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.cover}'

class AlternativeMedicine(models.Model):
    medicine = models.CharField(max_length=200)
    def __str__(self):
            return f'{self.medicine}'

class MaternityBenefits(models.Model):
    benefit = models.CharField(max_length=200)
    def __str__(self):
            return f'{self.benefit}'

class MaternityWaitingPeriod(models.Model):
    period = models.CharField(max_length=200)
    def __str__(self):
            return f'{self.period}'


class DentalBenefit(models.Model):
    benefit = models.CharField(max_length=200)
    def __str__(self):
            return f'{self.benefit}'

class WellnessBenefit(models.Model):
    benefit = models.CharField(max_length=200)
    def __str__(self):
            return f'{self.benefit}'

class OpticalBenefit(models.Model):
    benefit = models.CharField(max_length=200)
    def __str__(self):
            return f'{self.benefit}'

class TPA(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
            return f'{self.name}'
    class Meta:        
        verbose_name_plural = "TPA"


class Insurer(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    country = models.CharField(max_length=2, choices=COUNTRIES)
    name = models.CharField(max_length=FIELD_LENGTHS['name'])
    logo = models.ImageField(upload_to='insurer-logos', storage=PUBLIC_STORAGE)
    is_active = models.BooleanField(default=True)
    maf = models.FileField(upload_to=get_document_upload_path, blank=True)
    census = models.FileField(upload_to=get_document_upload_path, blank=True)
    bor = models.FileField(upload_to=get_document_upload_path, blank=True)


    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Insurer, self).save(*args, **kwargs)

    def get_insurer_logo(self):
        return self.logo.url if self.logo else static("images/avatar.jpg")


class InsurerDetails(models.Model):
    bank_name = models.CharField(max_length=50)
    iban = models.CharField(max_length=100)
    insurer = models.ForeignKey(Insurer, on_delete=models.CASCADE, related_name="insurer_details")
    
    class Meta:
        verbose_name_plural = 'InsurerDetails'
    
    def __str__(self):
        return self.insurer.name


class Emirate(models.Model):
    name = models.CharField(max_length=100)
    geographical_category = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class VisaCategory(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "Visa Categories"
    def __str__(self):
        return self.name
    
class Currency(models.Model):
        name = models.CharField(max_length=30)
        class Meta:
                verbose_name_plural = "Currencies"
        def __str__(self):
            return self.name

# class RepatriationPlan(models.Model):
#     name = models.CharField(max_length=100)
#     individual_expense = models.CharField(max_length=100, help_text="expense for one person accompanying a repatriated person")
#     family_expense = models.CharField(max_length=100, help_text="expense for one person accompanying a repatriated person")



class Plan(models.Model):
    OTHER_BENEFITS = ['repatriation']
    applicable_visa = models.ManyToManyField(VisaCategory)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    coverage_type = models.CharField(max_length=15,choices = LEVEL_OF_COVER, default=COMPREHENSIVE, blank=True)
    basic_plan_url = models.CharField(max_length=500,blank=True, null=True)
    basic_plan_premium = models.CharField(max_length=100,blank=True, null=True)
    insurer = models.ForeignKey(Insurer, on_delete=models.CASCADE, related_name="health_insurance_plan")
    logo = models.ImageField(upload_to='product-logos', storage=PUBLIC_STORAGE, blank = True)
    code = models.CharField(max_length=50, unique=True, blank = True)
    name = models.CharField(max_length=FIELD_LENGTHS['name'])
    display_name = models.CharField(max_length=FIELD_LENGTHS['name'], blank=True)
    payment_frequency = models.ManyToManyField(PaymentFrequency)
    is_payment_frequency_fixed = models.BooleanField(default=False)
    area_of_cover = models.ManyToManyField(Area_Of_Cover)
    is_area_of_cover_fixed = models.BooleanField(default=False)
    inpatient_deductible = models.ManyToManyField(InpatientDeductible)
    is_inpatient_deductible_fixed = models.BooleanField(default=False)
    copay_mode = models.CharField(max_length=30, choices=COPAY_MODE, default=VARIABLE)
    consultation_copay = models.ManyToManyField(ConsultationCopay)
    is_consultation_copay_fixed = models.BooleanField(default=False)
    pharmacy_copay = models.ManyToManyField(PharmacyCopay)
    is_pharmacy_copay_fixed = models.BooleanField(default=False)
    diagnostics_copay = models.ManyToManyField(DiagnosticsCopay)      
    is_diagnostics_copay_fixed = models.BooleanField(default=False)
    network = models.ManyToManyField(Network)
    is_network_fixed = models.BooleanField(default=False)
    tpa = models.ForeignKey(TPA, on_delete=models.SET_NULL, related_name="plan_tpa", null=True)
    annual_limit = models.ManyToManyField(AnnualLimit)
    is_annual_limit_fixed = models.BooleanField(default=False)
    physiotherapy = models.ManyToManyField(Physiotherapy)
    is_physiotherapy_session_fixed = models.BooleanField(default=False)
    pre_existing_cover = models.ManyToManyField(PreExistingCover)
    is_pre_existing_cover_fixed = models.BooleanField(default=True)
    alternative_medicine = models.ManyToManyField(AlternativeMedicine)
    is_alternative_medicine_fixed = models.BooleanField(default=False)
    maternity_benefits = models.ManyToManyField(MaternityBenefits)
    is_maternity_benefits_fixed = models.BooleanField(default=False)
    maternity_waiting_period = models.ManyToManyField(MaternityWaitingPeriod)
    is_maternity_waiting_period_fixed = models.BooleanField(default=False)
    dental_benefits = models.ManyToManyField(DentalBenefit)
    is_dental_benefit_fixed = models.BooleanField(default=False)
    wellness_benefits = models.ManyToManyField(WellnessBenefit)
    is_wellness_benefit_fixed = models.BooleanField(default=False)
    optical_benefits = models.ManyToManyField(OpticalBenefit)
    is_optical_benefit_fixed = models.BooleanField(default=False)
    can_auto_quote = models.BooleanField(default=False)
    currency = models.CharField(max_length=20, choices=CURRENCIES, default='AED')
    currencies = models.ManyToManyField(Currency)
    network_list_outpatient = models.FileField(upload_to=get_document_upload_path, blank=True)
    network_list_inpatient = models.FileField(upload_to=get_document_upload_path, blank=True)
    policy_wording = models.FileField(upload_to=get_document_upload_path, blank=True)
    table_of_benefits = models.FileField(upload_to=get_document_upload_path, blank=True)
    maf = models.FileField(upload_to=get_document_upload_path, blank=True)
    census = models.FileField(upload_to=get_document_upload_path, blank=True)
    bor = models.FileField(upload_to=get_document_upload_path, blank=True)
    is_repatriation_benefit_enabled = models.BooleanField(default=False)
    repatriation_benefits = JSONField(help_text='repatriation_benefits', blank = True, null=True)
    popup_template = models.TextField(blank=True, null=True)
    #objects = PlanManager()
    
    class Meta:
        ordering = ['-created_on']

    @classmethod
    def validate_product_attribute(cls, attribute):
        if len({'available', 'add_on', 'description'} - set(attribute.keys())) != 0:
            return False, 'Attribute value missing one of available, add_on, and description'

        if attribute['add_on'] and 'price' not in attribute:
            return False, 'Attribute value missing a price when add_on is True'

        return True, ''

    def __str__(self):
        return f'{self.code}'


    def save(self, *args, **kwargs):
        from_insurer_admin_save = kwargs.pop('from_insurer_admin', None)
        if not from_insurer_admin_save:
            self.maf = self.insurer.maf if not self.maf else self.maf
            self.census = self.insurer.census if not self.census else self.census
            self.bor = self.insurer.bor if not self.bor else self.bor
        if not self.logo:
            self.logo = self.insurer.logo
        if not self.code:
            self.code = f'{self.insurer.name}-{self.name}-{uuid.uuid4().hex[:5]}'
        self.clean()
        super(Plan, self).save(*args, **kwargs)

    def get_logo(self):
        return self.insurer.logo.url

    def get_add_ons(self):
        addons = []
        for product_attribute in self.PRODUCT_ATTRIBUTES:
            if getattr(self, product_attribute)['available'] and getattr(self, product_attribute)['add_on']:
                field_meta = self._meta.get_field(product_attribute)
                label = field_meta.help_text
                price = getattr(self, product_attribute).get('price', 0)
                addons.append({product_attribute: {'label': label, 'price': price}})

        return addons

    def get_display_name(self):
        return self.display_name or self.name

class MessageType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class MessageTemplates(models.Model):
    type = models.ForeignKey(MessageType, on_delete=models.CASCADE)
    insurer = models.ForeignKey(Insurer, on_delete=models.CASCADE, blank = True, null = True)
    subject = models.CharField(max_length=500)
    email_content = models.TextField()
    sms_content = models.TextField(blank=True, null=True)
    whatsapp_msg_content = models.TextField(blank=True, null=True)
    waiting_period_before_next_mail = models.IntegerField(default=3, help_text="waiting period before next mail in days")
    created_on = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.insurer:
            return f'{self.type.name} - {self.subject} - {self.insurer}'
        else:
            return f'{self.type.name} - {self.subject}'