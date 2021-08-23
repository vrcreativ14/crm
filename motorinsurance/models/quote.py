import datetime

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
from felix.constants import FIELD_LENGTHS
from motorinsurance_shared.models import Product


def default_expiry_date():
    """Function needed because lambda can't be used in the `default` argument to a Field"""
    return tz_now().date() + datetime.timedelta(days=30)


class Quote(AuditTrailMixin, models.Model):
    STATUS_PUBLISHED = 'published'
    STATUS_UNPUBLISHED = 'unpublished'

    STATUSES = (
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_UNPUBLISHED, 'Unpublished'),
    )

    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE)
    deal = models.ForeignKey('motorinsurance.Deal', on_delete=models.CASCADE)

    status = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=STATUSES)

    insured_car_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_suv = models.BooleanField(default=False)
    is_coupe = models.BooleanField(default=False)

    outdated = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)

    reference_number = models.CharField(max_length=FIELD_LENGTHS['reference_numbers'], editable=False)
    selected_product_details = JSONField(default=None, null=True)

    note = models.TextField(blank=True)

    number_of_views = models.PositiveIntegerField(default=0)

    expiry_date = models.DateField(default=default_expiry_date)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Quote: " + self.reference_number

    def validate_ownership(self):
        if self.company != self.deal.company:
            raise ValidationError(
                'You can not assign a quote belonging to company {} to a deal of another company'.format(
                    self.company
                )
            )

    def save(self, *args, **kwargs):
        self.validate_ownership()

        if self.pk is None:  # If this is a new quote, generate a reference number to use
            self.reference_number = int(tz_now().timestamp())

        super(Quote, self).save(*args, **kwargs)

        Algolia().upsert_motor_deal_record(self.deal)

    def is_active(self):
        if self.status == self.STATUS_UNPUBLISHED:
            return False

        return self.expiry_date >= tz_now().date()

    def is_expired(self):
        return self.expiry_date < tz_now().date()

    def get_quoted_product_by_id(self, pk):
        try:
            quoted_product = self.get_active_quoted_products().get(pk=pk)
        except QuotedProduct.DoesNotExist:
            quoted_product = None

        return quoted_product

    def get_all_quoted_products(self):
        return self.products.all()

    def get_editable_quoted_products(self):
        return self.products.exclude(status=QuotedProduct.STATUS_DELETED)

    def get_active_quoted_products(self):
        return self.products.filter(status=QuotedProduct.STATUS_PUBLISHED)

    def get_unpublished_quoted_products(self):
        return self.products.filter(status=QuotedProduct.STATUS_UNPUBLISHED)

    def get_quote_url(self):
        return reverse(
            "motorinsurance:quote-comparison", kwargs={
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
            "motorinsurance:quote-upload-documents", kwargs={
                "reference_number": self.reference_number,
                "pk": self.pk
            })

    def get_pdf_url(self):
        return "https://{}{}".format(
            settings.DOMAIN,
            reverse("motorinsurance:quote-pdf-view", kwargs={
                "reference_number": self.reference_number, "pk": self.pk
            })
        )

    def get_download_pdf_url(self, source='agent'):
        return "https://{}{}?source={}".format(
            settings.DOMAIN,
            reverse("motorinsurance:quote-pdf-download", kwargs={
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

    def get_least_quoted_product(self):
        product = None
        products = self.get_active_quoted_products().all()

        if products.count():
            sorted_products = sorted(products, key=lambda v: v.get_sale_price())
            product = sorted_products[0]

        return product


class QuotedProduct(AuditTrailMixin, models.Model):
    STATUS_UNPUBLISHED = 'unpublished'
    STATUS_PUBLISHED = 'published'
    STATUS_DELETED = 'deleted'
    STATUSES = (
        (STATUS_UNPUBLISHED, 'Unpublished'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_DELETED, 'Deleted')
    )

    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='products')

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    agency_repair = models.BooleanField()
    premium = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductible = models.DecimalField(max_digits=10, decimal_places=2)
    deductible_extras = models.TextField(blank=True)
    insured_car_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ncd_required = models.BooleanField(default=False)

    insurer_quote_reference = models.CharField(max_length=FIELD_LENGTHS['reference_numbers'], blank=True)

    default_add_ons = ArrayField(
        models.CharField(max_length=FIELD_LENGTHS['char_choices'],
                         choices=[(attribute, attribute) for attribute in Product.PRODUCT_ATTRIBUTES]),
        default=list, blank=True
    )

    status = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=STATUSES, default=STATUS_PUBLISHED)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Product: {self.product.code} Price: {self.get_sale_price()}'

    def is_published(self):
        return self.status == self.STATUS_PUBLISHED

    def get_sale_price(self):
        return self.sale_price or self.premium


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

    deal = models.ForeignKey('motorinsurance.Deal', on_delete=models.CASCADE)
    selected_product = models.ForeignKey(QuotedProduct, on_delete=models.CASCADE)
    selected_add_ons = ArrayField(
        models.CharField(max_length=FIELD_LENGTHS['char_choices'],
                         choices=[(attribute, attribute) for attribute in Product.PRODUCT_ATTRIBUTES]),
        default=list, blank=True
    )

    policy_start_date = models.DateField(blank=True)
    mortgage_by = models.CharField(max_length=FIELD_LENGTHS['address'], blank=True)

    payment_amount = models.DecimalField(max_digits=9, decimal_places=2)
    discount = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    created_by_agent = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.selected_product.product.code} ({self.payment_amount})'

    def save(self, *args, **kwargs):
        previous_active_orders_qs = Order.objects.filter(deal=self.deal, is_void=False)
        if self.pk is not None:
            previous_active_orders_qs = previous_active_orders_qs.exclude(pk=self.pk)

        if previous_active_orders_qs.exists():
            raise IntegrityError('There can only be one non-void order per deal')

        super(Order, self).save(*args, **kwargs)

    def get_pdf_url(self):
        return "https://{}{}".format(
            settings.DOMAIN,
            reverse("motorinsurance:order-pdf-view", kwargs={"pk": self.pk})
        )
