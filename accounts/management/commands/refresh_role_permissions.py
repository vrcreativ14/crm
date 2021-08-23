from django.contrib.auth.models import User
from django.core.management import BaseCommand
from rolepermissions.roles import get_user_roles, assign_role, clear_roles


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects.all():
            roles = get_user_roles(user)
            self.stdout.write('Clearing existing roles for user {}'.format(user.username))
            clear_roles(user)
            for role in roles:
                self.stdout.write('Assigning role {} to user {}'.format(role.__name__, user.username))
                assign_role(user, role)
