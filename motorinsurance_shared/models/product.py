from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.db import models

from felix.constants import PUBLIC_STORAGE, FIELD_LENGTHS
from insurers.models import Insurer


class ProductManager(models.Manager):
    def get_non_filtered_queryset(self):
        return super(ProductManager, self).get_queryset()

    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(is_active=True)


class Product(models.Model):
    PRODUCT_ATTRIBUTES = ['rent_a_car', 'road_side_assistance', 'pab_driver', 'pab_passenger',
                          'pab_family_and_friends', 'fire_and_theft_cover', 'natural_disaster', 'riot_and_strike',
                          'windscreen_and_glass_damage', 'emergency_medical_expenses', 'personal_belongings',
                          'replacement_keys_and_locks', 'oman_cover', 'off_road_cover', 'ambulance_cover',
                          'third_party_property_damage', 'third_party_bodily_injury']

    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    insurer = models.ForeignKey(Insurer, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='product-logos', storage=PUBLIC_STORAGE)

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=FIELD_LENGTHS['name'])
    display_name = models.CharField(max_length=FIELD_LENGTHS['name'], blank=True)

    is_tpl_product = models.BooleanField(default=False)
    allows_agency_repair = models.BooleanField(default=True)
    repair_type_description_non_agency = models.CharField(max_length=FIELD_LENGTHS['name'], default='', blank=True)

    document_url = models.URLField(max_length=FIELD_LENGTHS['website'], blank=True)

    rent_a_car = JSONField(help_text='Rent a car')
    road_side_assistance = JSONField(help_text='Road side assistance')

    pab_driver = JSONField(help_text='PAB driver')
    pab_passenger = JSONField(help_text='PAB passenger')
    pab_family_and_friends = JSONField(help_text='PAB family and friends')

    fire_and_theft_cover = JSONField(help_text='Fire and theft cover')
    natural_disaster = JSONField(help_text='Natural disaster')
    riot_and_strike = JSONField(help_text='Riot and strike')
    windscreen_and_glass_damage = JSONField(help_text='Windscreen and glass damage')

    emergency_medical_expenses = JSONField(help_text='Emergency medical expenses')
    personal_belongings = JSONField(help_text='Personal belongings')
    replacement_keys_and_locks = JSONField(help_text='Replacement keys and locks')

    oman_cover = JSONField(help_text='Oman cover')
    off_road_cover = JSONField(help_text='Off-road cover')

    ambulance_cover = JSONField(help_text='Ambulance cover')
    third_party_property_damage = JSONField(help_text='Third party property damage')
    third_party_bodily_injury = JSONField(help_text='third party bodily injury')

    can_auto_quote = models.BooleanField(default=False)

    objects = ProductManager()

    class Meta:
        ordering = ['-created_on', 'code']

    @classmethod
    def validate_product_attribute(cls, attribute):
        if len({'available', 'add_on', 'description'} - set(attribute.keys())) != 0:
            return False, 'Attribute value missing one of available, add_on, and description'

        if attribute['add_on'] and 'price' not in attribute:
            return False, 'Attribute value missing a price when add_on is True'

        return True, ''

    def __str__(self):
        return f'{self.code}'

    def clean(self):
        super(Product, self).clean()

        for field_name in self.PRODUCT_ATTRIBUTES:
            if getattr(self, field_name):
                validation_response = self.validate_product_attribute(getattr(self, field_name))
                if not validation_response[0]:
                    raise ValidationError({field_name: validation_response[1]})

    def save(self, *args, **kwargs):
        self.clean()
        super(Product, self).save(*args, **kwargs)

    def get_logo(self):
        return self.logo.url

    def get_add_ons(self):
        addons = []
        for product_attribute in self.PRODUCT_ATTRIBUTES:
            if getattr(self, product_attribute)['available'] and getattr(self, product_attribute)['add_on']:
                field_meta = self._meta.get_field(product_attribute)
                label = field_meta.help_text
                price = getattr(self, product_attribute).get('price', 0)
                addons.append({product_attribute: {'label': label, 'price': price}})

        return addons

    def get_display_name(self):
        return self.display_name or self.name
