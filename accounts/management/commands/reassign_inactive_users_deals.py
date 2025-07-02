from django.core.management import BaseCommand

from accounts.models import Company
from motorinsurance.models import Deal as MotorDeal


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', '--company_id', type=int, help='Company ID')
        parser.add_argument('--preview_only', action='store_true', help='set this if only wants to view the results.')

    def handle(self, *args, **options):
        company_id = options['company_id']
        preview_only = options['preview_only'] or False

        companies = Company.objects.all()

        if company_id:
            companies = companies.filter(pk=company_id)

        for company in companies:
            if company.schema_name == 'public':
                continue

            company.activate()

            in_active_users = company.userprofile_set.filter(user__is_active=False)
            active_admin = self._get_active_admin_user(company.userprofile_set.filter(user__is_active=True))

            if not active_admin:
                self.stdout.write('No active admin user found for {}'.format(company))

                return None

            self.stdout.write('\nFound {} inactive users for {}'.format(in_active_users.count(), company))

            self.stdout.write('Assigning all to {} '.format(active_admin))

            counter = 1
            for user in in_active_users:
                motor_deals_assigned_to, motor_deals_producer = self._get_motor_deals(user.user)

                self.stdout.write('\t{}: {}\n\t   Motor Assigned: {}, Motor Producer: {}'.format(
                    counter,
                    user.user,
                    motor_deals_assigned_to.count(),
                    motor_deals_producer.count()))

                counter += 1

                if not preview_only:
                    for deal in motor_deals_assigned_to:
                        deal.assigned_to = active_admin
                        deal.save()

                    for deal in motor_deals_producer:
                        deal.producer = None
                        deal.save()

    def _get_active_admin_user(self, users=[]):
        for user in users:
            if user.has_admin_role():
                return user.user

        return None

    def _get_motor_deals(self, user):
        motor_deals_assigned_to = MotorDeal.objects.filter(assigned_to=user)
        motor_deals_producer = MotorDeal.objects.filter(producer=user)

        return motor_deals_assigned_to, motor_deals_producer
