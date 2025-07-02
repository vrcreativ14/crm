import json

from django.core.management import BaseCommand
from django.conf import settings
import os.path

from insurers.models import Insurer
from motorinsurance_shared.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
                os.path.join(settings.BASE_DIR, 'motorinsurance/management/commands/products.json')
        ) as _if:
            products = json.load(_if)

            for product in products:
                insurer, _ = Insurer.objects.get_or_create(name=product['insurer'])
                product.pop('insurer')

                product_model = Product(**product, insurer=insurer)
                product_model.save()
