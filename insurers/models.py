from django.db import models
from django.conf.urls.static import static

from felix.constants import COUNTRIES, PUBLIC_STORAGE, FIELD_LENGTHS


class Insurer(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    country = models.CharField(max_length=2, choices=COUNTRIES)
    name = models.CharField(max_length=FIELD_LENGTHS['name'])
    logo = models.ImageField(upload_to='insurer-logos', storage=PUBLIC_STORAGE)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_insurer_logo(self):
        return self.logo.url if self.logo else static("images/avatar.jpg")
