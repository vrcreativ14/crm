import yaml
from django.core.exceptions import ValidationError
from django.db import models

from auto_quoter.constants import AUTO_QUOTABLE_INSURERS
from felix.constants import FIELD_LENGTHS


class AutoQuoterConfig(models.Model):
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE)
    insurer = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=AUTO_QUOTABLE_INSURERS)

    options = models.TextField(blank=False)

    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    updated_on = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ('company', 'insurer')

    def __str__(self):
        return f'{self.company.name} - {self.insurer}'

    def clean(self):
        self.validate_options()

    def validate_options(self):
        try:
            yaml.load(self.options)
        except yaml.YAMLError:
            raise ValidationError({'options': 'Unable to parse options as valid YAML'})

    def get_options_dict(self):
        return yaml.safe_load(self.options)


class InsurerApiTransactionLog(models.Model):
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE)
    insurer = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=AUTO_QUOTABLE_INSURERS)

    deal = models.ForeignKey('motorinsurance.Deal', null=True, on_delete=models.SET_NULL)

    request_content = models.TextField()

    response_info = models.TextField(blank=True)
    response_content = models.TextField()

    created_on = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f'{self.get_insurer_display()} <- Deal {self.deal.pk} @ {self.created_on}'
