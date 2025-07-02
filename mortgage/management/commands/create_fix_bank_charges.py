from django.core.management import BaseCommand
from mortgage.models import GovernmentFee, Eibor


class Command(BaseCommand):
    def handle(self):
        GovernmentFee.objects.create(
            trustee_center_fee=400,
            property_fee_rate=4,
            property_fee_addition=580,
            mortgage_fee_rate=0.25,
            mortgage_fee_addition=290,
            real_state_fee=2,
        )

        Eibor.objects.create(eibor_rate=1)
