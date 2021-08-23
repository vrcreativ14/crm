from django.core.exceptions import ValidationError

from django import forms


class MoneyField(forms.DecimalField):
    description = 'A custom decimal field which cleans the value before save'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_message = {
            "required": "This field is required",
            "value": "Invalid value"
        }

    def clean(self, value):
        try:
            value = float(value.replace(',', ''))
            return super().clean(value)
        except (ValueError, TypeError):
            raise ValidationError('Invalid value')
