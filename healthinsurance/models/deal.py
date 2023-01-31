from django.db import models
from django.core.files.storage import default_storage
from accounts.models import *
from healthinsurance.constants import *
from felix.constants import FIELD_LENGTHS, GENDER_CHOICES, MARITAL_STATUS_LIST, COUNTRIES
# Create your models here.
from datetime import datetime, timedelta
from core.utils import get_initials_from_the_name
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from core.mixins import AuditTrailMixin
import os

PUBLIC_STORAGE = default_storage

class AdditionalMember(models.Model):
    relation = models.CharField(max_length=15, blank=False)
    name = models.CharField(max_length=FIELD_LENGTHS['name'])
    dob = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=10, choices=COUNTRIES, blank=True)
    country_of_stay = models.CharField(max_length=10, choices=COUNTRIES, blank=True)
    order = models.IntegerField(blank=True)
    premium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    def __str__(self):
        return self.name

    def get_nationality(self):
        if self.nationality.lower() == 'other':
            return 'other'
        if self.nationality:
            searched_list = list(filter(lambda country: country[0] in self.nationality, COUNTRIES))
            return searched_list[0][1]
        else:
            return ''
            
    def get_residence_country(self):
        if self.country_of_stay.lower() == 'other':
            return 'other'
        if self.country_of_stay:
            searched_list = list(filter(lambda country: country[0] in self.country_of_stay, COUNTRIES))
            return searched_list[0][1]
        else:
            return ''

UAE = 'AE'
OTHER = 'other'
COUNTRY_OF_STAY = (
    (UAE, 'United Arab Emirates'),
    (OTHER, 'Other')
)

class PrimaryMember(models.Model):
    name = models.CharField(max_length=FIELD_LENGTHS['name'])
    email = models.EmailField(max_length=FIELD_LENGTHS['email'], blank=True)
    phone = models.CharField(max_length=FIELD_LENGTHS['phone'], blank=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=GENDER_CHOICES, blank=True)
    marital_status = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=MARITAL_STATUS_LIST, blank=True, null=True)
    nationality = models.CharField(max_length=10, choices=COUNTRIES, blank=True)
    country_of_stay = models.CharField(max_length=10, choices=COUNTRIES, blank=True)
    visa = models.CharField(max_length=20, choices=EMIRATES_LIST, blank=True)
    salary_band = models.CharField(max_length=20, choices=SALARY_BAND, blank=True)    
    additional_members = models.ManyToManyField(AdditionalMember, blank=True)        
    preferred_hospitals = models.CharField(max_length=200, blank=True)
    premium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    def __str__(self):
        return self.name

    def get_initial(self):
        return get_initials_from_the_name(self.name or self.email)

    def get_nationality(self):
        if self.nationality.lower() == 'other':
            return 'other'
        if self.nationality:
            searched_list = list(filter(lambda country: country[0] in self.nationality, COUNTRIES))
            return searched_list[0][1]
        else:
            return ''
    def get_residence_country(self):
        if self.country_of_stay.lower() == 'other':
            return 'other'
        if self.country_of_stay:
            searched_list = list(filter(lambda country: country[0] in self.country_of_stay, COUNTRIES))
            return searched_list[0][1]
        else:
            return ''

# class Insurer(models.Model):
#     name = models.CharField(max_length=50, blank=False)
#     logo = models.ImageField(upload_to="", storage=PUBLIC_STORAGE, blank=True, default='upload/insure-nex-logo.png')
#     maf = models.FileField(upload_to="", storage=PUBLIC_STORAGE, blank=True, null=True, default="upload/sample_word.pdf")
#     network_list = models.FileField(upload_to="", storage=PUBLIC_STORAGE, blank=True, null=True, default="upload/sample_word.pdf")
#     policy_wordings = models.FileField(upload_to="", storage=PUBLIC_STORAGE, blank=True, null=True, default="upload/sample_word.pdf")
#     table_of_benefits = models.FileField(upload_to="", storage=PUBLIC_STORAGE, blank=True, null=True, default="upload/sample_word.pdf")
#     plan = models.CharField(max_length=100, blank=False)
#     area_of_cover = models.CharField(max_length=100, blank=False)
#     annual_limit = models.FloatField(blank=False)
#     deductable = models.FloatField(blank=False)
#     dental_cover = models.FloatField(blank=False)
#     maternity_cover = models.FloatField(blank=False)
#     maternity_cover = models.FloatField(blank=False)


class AdditionalBenefit(models.Model):
    benefit = models.CharField(max_length=50)

    def __str__(self):
        return self.benefit


class Deal(AuditTrailMixin, models.Model):
    deal_id = models.AutoField(primary_key=True, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True)
    stage = models.CharField(max_length=50, choices=DEAL_STAGES, default=STAGE_NEW)
    status = models.CharField(max_length=50, choices=DEAL_STATUSES, default=STATUS_NEW)
    deal_type = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=DEAL_TYPES, default=DEAL_TYPE_NEW, blank=True)
    quote_sent = models.BooleanField(default=False)
    total_premium = models.FloatField(blank=True, default=0.00)
    is_customer_insurance = models.BooleanField(default=True)
    primary_member = models.OneToOneField(PrimaryMember, on_delete=models.CASCADE, related_name="deal_member")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="health_deal_user")
    referrer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="health_deal_referrer")
    start_date = models.DateField(null=True, blank=True)
    geographical_coverage = models.CharField(max_length=30, choices=GEOGRAPHICAL_COVERAGE, blank=True)    
    additional_benefits = models.ManyToManyField(AdditionalBenefit, blank=True)
    other_benefits = ArrayField(models.CharField(max_length=500), blank=True, null=True)
    indicative_budget = models.CharField(max_length=30, choices=BUDGET, blank=True)
    level_of_cover = models.CharField(max_length=15,choices = LEVEL_OF_COVER, default=BASIC, blank=True)
    notes = GenericRelation('core.Note')
    tasks = GenericRelation('core.Task')
    customer = models.ForeignKey('customers.Customer', null=True, on_delete=models.SET_NULL, related_name="health_deal_customer")
    renewal_for_policy = models.ForeignKey(
        'healthinsurance.HealthPolicy', null=True, blank=True, on_delete=models.SET_NULL, related_name='deal_policy_renewed_for')
    def __str__(self):
        return self.primary_member.name
  
    @property
    def deal_timeinfo(self):
            created_on = self.created_on.replace(tzinfo=None)
            if created_on.date() == datetime.now().date():
                return 'Today'
            elif created_on.date() >= (timezone.now() - timedelta(hours=24)).date():
                return 'Yesterday'
            else:
                return self.created_on.date()

    @property
    def deal_stage_text(self):
        stage={
            'new':'New',
            'quote':'Quote',
            'final_quote':'Final Quote',
            'documents':'Documents',
            'payment':'Payment',
            'policy_issuance':'Policy Issuance',
            'housekeeping':'Housekeeping',
            'won':'Won',
            'lost':'Lost',
        }
        return stage.get(self.stage, "")

    @property
    def geographical_coverage_text(self):
        coverage = {
            'local':'Local',
            'regional':'Regional',
            'worldwide_except_us':'Worldwide Except US',
            'local':'Worldwide',
        }
        return coverage.get(self.geographical_coverage, self.geographical_coverage)

    @property
    def additional_benefits_text(self):
        coverage = {
            'health_screen':'Health Screen',
            'dental':'Dental',
            'other':'Other',            
        }
        return coverage.get(self.additional_benefits, self.additional_benefits)
    
    @property
    def indicative_budget_text(self):
        coverage = {
            'below4k':'Below 4k',
            'from4to8k':'4-8k',
            'above8k':'Above 8k',
            'notsure':'Not Sure',
        }
        return coverage.get(self.indicative_budget, self.indicative_budget)

    @property
    def status_text(self):
        coverage = {
            'active':'Active',
            'new':'New Deal',
            'deleted':'Deleted',
            'waiting for client':'Waiting for client',
            'waiting for us':'Waiting for us',
            'waiting for insurer':'Waiting for insurer',
            'waiting for compliance':'Waiting for compliance',
        }
        return coverage.get(self.status, self.status)

    @property
    def status_badge(self): 
        if self.status == 'new':
            return 'new-deal'
        return self.status.replace(' ','-')
    
    @property
    def selected_plan(self):
        from healthinsurance.models.quote import Order
        order = Order.objects.filter(deal = self)
        if order.exists():
            return order[0].selected_plan.plan
        else:
            return None

    @property
    def current_sub_stage(self):
        if SubStage.objects.filter(deal=self,stage=self.stage).exists():
            return SubStage.objects.filter(deal=self,stage=self.stage).last()

    def get_current_sub_stage(self, **kwargs):
        substage_name = kwargs.get('substage', None)
        if substage_name:
            substage_obj = SubStage.objects.filter(deal=self,stage=self.stage, sub_stage = substage_name)
        else:
            substage_obj = SubStage.objects.filter(deal=self,stage=self.stage)
        if substage_obj.exists():
            return substage_obj.last()
    
    def get_title(self):
        if self.selected_plan:
            return '{}-{}-{}-{}-{:.2f}'.format(self.primary_member.name, self.selected_plan.name,self.selected_plan.insurer.name, self.selected_plan.currency,self.total_premium)
        else:
            return '{}-{:.2f}'.format(self.primary_member.name, self.total_premium)

    def get_tags(self):
        tags = []
        if self.status == STATUS_DELETED:
            tags.append('Deleted')
        if self.stage == STAGE_LOST:
            tags.append('Lost')
        if self.deal_type == DEAL_TYPE_RENEWAL:
            tags.append('Renewal Deal')
        # if quote and self.stage == self.STAGE_QUOTE:
        #     if quote.status == Quote.STATUS_PUBLISHED:
        #         tags.append('Published')
        #     else:
        #         tags.append('Unpublished')

            # if quote.number_of_views > 0:
            #     tags.append(f'Viewed {quote.number_of_views} time(s)')
            # else:
            #     if self.quote_sent:
            #         tags.append('Sent')
            #     else:
            #         tags.append('Not sent')
        # elif self.stage == self.STAGE_ORDER:
        #     order = self.get_order()
        #     if order:
        #         if order.status == order.STATUS_PAID:
        #             tags.append('Paid')
        #         else:
        #             tags.append('Unpaid')
        return tags

    def get_order(self):
        from healthinsurance.models.quote import Order
        try:
            return Order.objects.filter(deal = self).first()
        except Order.DoesNotExist:
            return None

    def get_quote(self):
        from healthinsurance.models.quote import Quote
        try:
            return Quote.objects.filter(deal = self).first()
        except Quote.DoesNotExist:
            return None

    def get_payment_details(self):
        from healthinsurance.models.quote import PaymentDetails
        try:
            return PaymentDetails.objects.filter(deal = self).first()
        except PaymentDetails.DoesNotExist:
            return None

    def get_policy(self):
        from healthinsurance.models.policy import HealthPolicy
        try:
            return HealthPolicy.objects.filter(deal = self).first()
        except HealthPolicy.DoesNotExist:
            return None

def deal_files_directory(instance,filename):
    return "deals/" + str(instance.deal.deal_id) + "/" + str(instance.type) + "/" + filename
class DealFiles(models.Model):
    ATTACHMENT_TYPE = [
        ("world_check_proof","world_check_proof"),
        ("receipt_of_payment","receipt_of_payment"),
        ("tax_invoice","tax_invoice"),
        ("certificate_of_insurance","certificate_of_insurance"),
        ("medical_card","medical_card"),
        ("confirmation_of_cover","confirmation_of_cover"),
        ("credit_note","credit_note"),
        ("other_document","other_document"),
        ("primary_passport","primary_passport"),
        ("primary_visa","primary_visa"),
        ("primary_emiratesid","primary_emiratesid"),
        ("primary_maf","primary_maf"),
        ("primary_previousinsurance","primary_previousinsurance"),
        ("primary_other","primary_other"),
        ("final_quote","final_quote"),
        ("final_quote_additional_document","final_quote_additional_document"),
        ("signed_final_quote","signed_final_quote"),
        ("signed_final_quote_additional_document","signed_final_quote_additional_document"),
        ("payment_proof","payment_proof"),
        ("other_documents","other_documents"),
        ("additional_document","additional_document"),
        ("order_confirmation","order_confirmation"),
        ("plan_census","plan_census"),
        ("plan_bor","plan_bor"),
    ]
    deal = models.ForeignKey(Deal,on_delete=models.CASCADE)
    type = models.CharField(choices=ATTACHMENT_TYPE,default='final-quote',max_length=100)
    file = models.FileField(upload_to=deal_files_directory,null=True,blank=True)
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)

class MemberDocuments(models.Model):
    DOCUMENT_TYPE = [        
        ("other_documents","other_documents"),     
        ("passport","passport"),
        ("visa","visa"),        
        ("emiratesid","emiratesid"),
        ("maf","maf"),
        ("previousinsurance","previousinsurance"),                
        ("other","other"),
    ]
    deal = models.ForeignKey(Deal,on_delete=models.CASCADE)
    type = models.CharField(choices=DOCUMENT_TYPE,default='other',max_length=100)
    file = models.FileField(upload_to=deal_files_directory,null=True,blank=True)
    member = models.ForeignKey(AdditionalMember, on_delete=models.CASCADE)

    @property
    def filename(self):
        return os.path.basename(self.file.name)

class ProcessEmail(models.Model):
    from_address = models.EmailField()
    to_address = models.EmailField()
    subject = models.CharField(max_length=2000)
    text = models.TextField()
    attachments = GenericRelation("core.Attachment")
    html = models.TextField()
    cc_addresses = ArrayField(base_field=models.EmailField())
    bcc_addresses = ArrayField(base_field=models.EmailField())
    deal = models.ForeignKey(Deal, related_name='health_deal_processed_email', on_delete=models.SET_NULL, null=True)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.deal} - {self.subject}"


class SubStage(models.Model):
    deal = models.ForeignKey(Deal, related_name='deal_substages', on_delete=models.CASCADE, null=True)
    stage = models.CharField(max_length=50, choices=DEAL_STAGES)
    sub_stage = models.CharField(max_length=50, choices=SUB_STAGES)
    world_check_hit = models.BooleanField(blank=True, null=True)
    world_check_approved = models.CharField(max_length=50, choices = WORLD_CHECK_APPROVED, blank=True, null=True)

    def __str__(self):
        return f"{self.deal}-{self.deal.pk}-{self.stage}-{self.sub_stage}"

    def save(self, *args, **kwargs):
        self.clean()
        super(SubStage, self).save(*args, **kwargs)

    class Meta:
        unique_together = ['deal','stage', 'sub_stage']

