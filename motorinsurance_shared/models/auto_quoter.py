from django.db.models import JSONField
from django.db import models

from auto_quoter.constants import AUTO_QUOTABLE_INSURERS
from felix.constants import FIELD_LENGTHS


class AutoQuoterCarTrimData(models.Model):
    """Stores additional information used by auto quoters about the trims in our MMT tree. This additional data is
    stored in a JSON field and associated with an auto quoter & trim."""
    insurer = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=AUTO_QUOTABLE_INSURERS, editable=False)
    trim = models.ForeignKey('motorinsurance_shared.CarTrim', on_delete=models.CASCADE, editable=False)

    data = JSONField(default=dict)

    def __str__(self):
        return self.insurer + ' - ' + self.trim.get_full_title()
