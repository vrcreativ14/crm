from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from core.intercom import Intercom


class Command(BaseCommand):
    help = 'Set intercom custom field "Deleted" to True for users who are deleted from the CRM.'

    def handle(self, *args, **options):
        intercom = Intercom()
        users = User.objects.filter(is_active=False)
        self.stdout.write('{} users found\n=============='.format(users.count()))

        for user in users:
            intercom_user_data = intercom.get_contact_by_email_and_id(user.username, user.pk)

            if intercom_user_data:
                intercom.update_contact(intercom_user_data['id'], {'custom_attributes': {'Deleted': True}})
                self.stdout.write('{} updated'.format(user.username))
