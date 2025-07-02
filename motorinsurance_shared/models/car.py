from django.db.models import JSONField
from django.db import models

from felix.constants import CAR_YEARS_LIST


class CarMake(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class CarModel(models.Model):
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {}".format(self.make.name, self.name)

    class Meta:
        ordering = ['make', 'name']


class CarTrim(models.Model):
    year = models.PositiveSmallIntegerField(choices=CAR_YEARS_LIST)

    model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)

    algo_driven_id = models.CharField(max_length=30, default='', blank=True)
    algo_driven_data = JSONField(default=dict, blank=True)

    def __str__(self):
        return self.get_full_title()

    def get_title_with_model(self):
        return "{} {}".format(self.model.name, self.title)

    def get_full_title(self):
        return "{} {} {} {}".format(self.year, self.model.make.name, self.model.name, self.title)

    class Meta:
        ordering = ['year', 'model__make', 'model', 'title']
