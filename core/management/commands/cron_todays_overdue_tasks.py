import logging
import datetime

from django.core.management import BaseCommand
from collections import defaultdict

from core.email import Emailer
from core.models import Task

from accounts.models import Company
from core.utils import clean_and_validate_email_addresses

logger = logging.getLogger('workers')


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Fetch all active companies from DB')

        active_companies = Company.objects.filter(status=Company.STATUS_ACTIVE)

        for company in active_companies:
            if company.schema_name == 'public':
                continue

            company.activate()

            self.stdout.write('********* {} *********'.format(company.name))

            today = datetime.date.today() + datetime.timedelta(days=1)

            tasks = Task.objects.filter(
                due_datetime__lte=today,
                is_completed=False,
                is_deleted=False,
                assigned_to__isnull=False
            ).order_by('due_datetime')

            if not tasks.count():
                self.stdout.write('No tasks found')
                continue

            self.stdout.write('{} tasks found'.format(tasks.count()))

            users = defaultdict(list)

            for task in tasks:
                users[task.assigned_to].append(task)

            today = datetime.date.today()

            for user, tasks in users.items():
                if not clean_and_validate_email_addresses(user.email):
                    logger.error('Error sending cron task email. User: %s, Invalid email address', user)
                    continue

                overdue_tasks = []
                todays_tasks = []
                for task in tasks:
                    if task.due_datetime.day == today.day and task.due_datetime.month == today.month:
                        todays_tasks.append(task)
                    else:
                        overdue_tasks.append(task)

                self.stdout.write('Sending email to {} with Todays: {}, Overdue: {} tasks'.format(
                    user, len(todays_tasks), len(overdue_tasks)))

                emailer = Emailer(company)
                emailer.send_tasks_summary_cron_email(user, todays_tasks, overdue_tasks)
