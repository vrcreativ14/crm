import datetime

from django.utils.timezone import now as tz_now

from django import forms

from core.utils import add_empty_choice

from healthinsurance.models.quote import Order
from healthinsurance.models.quote import Quote, QuotedPlan, Deal

from core.custom_fields import MoneyField
from healthinsurance_shared.models import Plan


class OrderForm(forms.ModelForm):
    

    class Meta:
        model = Order
        exclude = ('created_on', 'updated_on')
        