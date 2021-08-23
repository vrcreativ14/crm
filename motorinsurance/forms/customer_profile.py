from django import forms

from motorinsurance.models import CustomerProfile


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        exclude = ('created_on', 'updated_on', 'company',)