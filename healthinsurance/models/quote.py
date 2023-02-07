from datetime import datetime, timedelta
from email.quoprimime import quote
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.urls import reverse
from django.utils.timezone import now as tz_now
from urlshortening.models import get_short_url
from core.mixins import AuditTrailMixin
from core.algolia import Algolia
from felix.constants import FIELD_LENGTHS, PAYMENT_MODES
from healthinsurance_shared.models import *
from healthinsurance.models.deal import *

def default_expiry_date():
    """Function needed because lambda can't be used in the `default` argument to a Field"""
    return tz_now().date() + timedelta(days=30)

class PaymentDetails(models.Model):
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    payment_url = models.CharField(max_length=300, blank=True, null=True)
    iban = models.CharField(max_length=100, blank=True, null=True)
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True)
    payment_mode = models.CharField(choices=PAYMENT_MODES, max_length=50, blank=True, null=True)

    def __str__(self):
        return self.deal.primary_member.name if self.deal else ''


class Quote(AuditTrailMixin, models.Model):
    STATUS_PUBLISHED = 'published'
    STATUS_UNPUBLISHED = 'unpublished'
    STATUSES = (
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_UNPUBLISHED, 'Unpublished'),
    )
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, related_name='health_insurance_company')
    deal = models.OneToOneField(Deal, on_delete=models.CASCADE, related_name="health_quote_deals")
    status = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=STATUSES)
    outdated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    reference_number = models.CharField(max_length=FIELD_LENGTHS['reference_numbers'])
    selected_plan_details = JSONField(default=None, null=True)
    note = models.TextField(blank=True)
    number_of_views = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(default=default_expiry_date)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    insurer_quote_reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "Quote: " + str(self.reference_number)

    def validate_ownership(self):
        if self.company != self.deal.company:
            raise ValidationError(
                'You can not assign a quote belonging to company {} to a deal of another company'.format(
                    self.company
                )
            )

    def save(self, *args, **kwargs):
        #self.validate_ownership()

        if self.pk is None:  # If this is a new quote, generate a reference number to use
            self.reference_number = int(tz_now().timestamp())
        if not SubStage.objects.filter(deal=self.deal).exists():
            SubStage.objects.create(deal = self.deal, stage = self.deal.stage, sub_stage = "quote")
        super(Quote, self).save(*args, **kwargs)

        

    def is_active(self):
        if self.status == self.STATUS_UNPUBLISHED:
            return False
        # elif deal_stages_to_number(self.deal.stage) > 6:      #policy stage or further
        #     policy = self.deal.health_policy_deal if self.deal and self.deal.health_policy_deal else None
        #     #days_diff =                             
            

        return self.expiry_date >= tz_now().date()

    def is_expired(self):
        return self.expiry_date < tz_now().date()

    # def get_quoted_product_by_id(self, pk):
    #     try:
    #         quoted_product = self.get_active_quoted_products().get(pk=pk)
    #     except QuotedProduct.DoesNotExist:
    #         quoted_product = None

        return quoted_product

    def get_all_quoted_products(self):
        return self.products.all()

    def get_editable_quoted_plans(self):
        qp = QuotedPlan.objects.filter(quote = self).order_by('-is_renewal_plan')
        return qp.exclude(status=QuotedPlan.STATUS_DELETED)

    def get_active_quoted_products(self):
        return self.products.filter(status=QuotedPlan.STATUS_PUBLISHED)

    def get_unpublished_quoted_products(self):
        return self.products.filter(status=QuotedPlan.STATUS_UNPUBLISHED)

    def get_quote_url(self):
        return reverse(
            "health-insurance:quote-comparison", kwargs={
                "reference_number": self.reference_number,
                "pk": self.pk
            })

    def get_quote_short_url(self):
        return "https://{}{}".format(
            settings.DOMAIN,
            reverse("short-url", kwargs={'short_id': get_short_url(self.get_quote_url()).short_id})
        )

    def get_document_upload_url(self):
        return reverse(
            "healthinsurance:quote-upload-documents", kwargs={
                "reference_number": self.reference_number,
                "pk": self.pk
            })

    def get_pdf_url(self):
        return "https://{}{}".format(
            settings.DOMAIN,
            reverse("healthinsurance:quote-pdf-view", kwargs={
                "reference_number": self.reference_number, "pk": self.pk
            })
        )

    def get_download_pdf_url(self, source='agent'):
        return "https://{}{}?source={}".format(
            settings.DOMAIN,
            reverse("healthinsurance:quote-pdf-download", kwargs={
                "reference_number": self.reference_number, "pk": self.pk
            }), source
        )

    def get_document_upload_short_url(self):
        return "https://{}{}".format(
            settings.DOMAIN,
            reverse("short-url", kwargs={'short_id': get_short_url(self.get_document_upload_url()).short_id})
        )

    def handle_payment_recorded(self, payment_record, by_user=None):
        self.deal.handle_payment_recorded_for_quote(self, payment_record, by_user)

    # def get_least_quoted_product(self):
    #     product = None
    #     products = self.get_active_quoted_products().all()

    #     if products.count():
    #         sorted_products = sorted(products, key=lambda v: v.get_sale_price())
    #         product = sorted_products[0]

    #     return product

def get_document_upload_path(self, filename):
        """Returns a customer specific folder to write the policy document to.

        Defined first because we use it as a field parameter `upload_to`. Saving on a per customer folder allows us
        easy navigation when manually browsing the files."""
        base_path = 'health_insurance_plan_/{}-{}'.format(self.plan.insurer.pk, slugify(self.plan.insurer.name))

        date_component = datetime.utcnow().strftime('%Y-%m-%d')

        return "renewal/" + str(self.pk) + "/" + str(self.plan.name) + "/" + filename


class QuotedPlan(AuditTrailMixin, models.Model):
    STATUS_UNPUBLISHED = 'unpublished'
    STATUS_PUBLISHED = 'published'
    STATUS_DELETED = 'deleted'
    STATUSES = (
        (STATUS_UNPUBLISHED, 'Unpublished'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_DELETED, 'Deleted')
    )
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='health_insurance_quote')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='health_quoted_plan')
    total_premium = models.DecimalField(max_digits=10, decimal_places=2, blank = True, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    #insurer_quote_reference = models.CharField(max_length=FIELD_LENGTHS['reference_numbers'], blank=True)
    payment_frequency = models.ForeignKey(PaymentFrequency, on_delete=models.SET_NULL, null=True, related_name="qp_payment_fequency")
    area_of_cover = models.ForeignKey(Area_Of_Cover, on_delete=models.SET_NULL, null=True, related_name="qp_area_of_cover")
    consultation_copay = models.ForeignKey(ConsultationCopay, on_delete=models.SET_NULL, null=True, related_name="qp_consultation_copay")
    pharmacy_copay = models.ForeignKey(PharmacyCopay, on_delete=models.SET_NULL, null=True, related_name="qp_pharmacy_copay")
    diagnostics_copay = models.ForeignKey(DiagnosticsCopay, on_delete=models.SET_NULL, null=True, related_name="qp_diagnostics_copay")
    inpatient_deductible = models.ForeignKey(InpatientDeductible, on_delete=models.SET_NULL, null=True, related_name="qp_deductible")
    network = models.ForeignKey(Network, on_delete=models.SET_NULL, null=True, related_name="qp_network")
    #tpa_network = models.ForeignKey(Network, on_delete=models.SET_NULL, null=True, related_name="qp_tpa_network")
    annual_limit = models.ForeignKey(AnnualLimit, on_delete=models.SET_NULL, null=True, related_name="qp_annual_limit")
    physiotherapy = models.ForeignKey(Physiotherapy, on_delete=models.SET_NULL, null=True, related_name="qp_physiotherapy")
    alternative_medicine = models.ForeignKey(AlternativeMedicine, on_delete=models.SET_NULL, null=True, related_name="qp_alternative_medicine")
    maternity_benefits = models.ForeignKey(MaternityBenefits, on_delete=models.SET_NULL, null=True, related_name="qp_maternity_benefits")
    maternity_waiting_period = models.ForeignKey(MaternityWaitingPeriod, on_delete=models.SET_NULL, null=True, related_name="qp_maternity_waiting_period")
    dental_benefits = models.ForeignKey(DentalBenefit, on_delete=models.SET_NULL, null=True, related_name="qp_dental_benefits")
    wellness_benefits = models.ForeignKey(WellnessBenefit, on_delete=models.SET_NULL, null=True, related_name="qp_wellness_benefits")
    optical_benefits = models.ForeignKey(OpticalBenefit, on_delete=models.SET_NULL, null=True, related_name="qp_optical_benefits")
    pre_existing_cover = models.ForeignKey(PreExistingCover, on_delete=models.SET_NULL, null=True, related_name="qp_pre_existing_cover")
    is_renewal_plan = models.BooleanField(default=False)
    plan_renewal_document = models.FileField(upload_to=get_document_upload_path, blank=True)
    is_repatriation_benefit_enabled = models.BooleanField(default=False)
    status = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=STATUSES, default=STATUS_PUBLISHED)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    premium_info = JSONField("premium_info", default=None, null=True)
    def __str__(self):
        return f'Plan: {self.plan.code} Total Premium: {self.total_premium}'

    def is_published(self):
        return self.status == self.STATUS_PUBLISHED

    @property
    def renewal_filename(self):
        return os.path.basename(self.plan_renewal_document.name)
    

class Order(AuditTrailMixin, models.Model):
    STATUS_PAID = 'paid'
    STATUS_UNPAID = 'unpaid'
    STATUSES = (
        (STATUS_PAID, 'Paid'),
        (STATUS_UNPAID, 'Unpaid'),
    )
    status = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=STATUSES, default=STATUS_UNPAID)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_void = models.BooleanField(default=False)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name="health_order")
    selected_plan = models.ForeignKey(QuotedPlan, on_delete=models.CASCADE)
    policy_start_date = models.DateField(blank=True)
    payment_amount = models.DecimalField(max_digits=9, decimal_places=2, blank = True)
    discount = models.DecimalField(max_digits=9, decimal_places=2, default=0, blank = True)
    created_by_agent = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.selected_plan.plan.code} ({self.payment_amount})'

    def save(self, *args, **kwargs):
        # if self.deal:
        #     previous_active_orders_qs = Order.objects.filter(deal=self.deal, is_void=False)
        #     if self.pk is not None:
        #         previous_active_orders_qs = previous_active_orders_qs.exclude(pk=self.pk)

        #     if previous_active_orders_qs.exists():
        #         raise IntegrityError('There can only be one non-void order per deal')

        super(Order, self).save(*args, **kwargs)

    def get_pdf_url(self):
        return "https://{}{}".format(
            settings.DOMAIN,
            reverse("health-insurance:order-pdf-view", kwargs={"pk": self.pk})
        )
