"""Timeline Search"""
import dateutil
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturalday
from mortgage.models import Deal as mortgagedeals

from felix.constants import GENDER_CHOICES, EMIRATES_LIST


class Timeline:
    model_name = None

    @classmethod
    def get_formatted_object_history(cls, obj):
        trail = obj.get_audit_trail()
        cls.model_name = obj._meta.model_name.title()

        history = list()
        for item in trail.change_history:
            if item['type'] == 'create':
                content = '{} created'.format(cls.model_name)

                history.append({
                    'content': content,
                    'user': item['user'],
                    'date': cls.formatted_date(item['timestamp'])
                })
            elif item['type'] == 'attach file':
                message = cls.get_file_message(item['message'])
                history.append({
                    'content': message[0],
                    'user': item['user'],
                    'file': message[-1],
                    'date': cls.formatted_date(item['timestamp'])
                })
            elif item['type'] == 'email':
                message = cls.get_file_message(item['message'])
                msg = message[0]
                email_pk = None
                try:
                    if isinstance(obj, mortgagedeals):
                        sub = message[0].split("emailpk")
                        msg = sub[0].strip()
                        email_pk = sub[1].strip()
                except:
                    pass
                data = {
                    'type': 'email',
                    'content': msg,
                    'user': item['user'],
                    'date': cls.formatted_date(item['timestamp'])
                }
                if email_pk:
                    data['email_pk'] = email_pk
                history.append(data)

            elif item['type'] == 'edit':
                for k, v in item['changes'].items():
                    field_name = k.replace('_', ' ').title()

                    # We have an issue with old field change data saving None as the string representation
                    # This check is here to deal with those older incorrect data items
                    if isinstance(v, dict):
                        for key in ['new', 'old']:
                            if v[key] == 'None':
                                v[key] = None

                    if hasattr(cls, k) and callable(getattr(cls, k)):
                        method = getattr(cls, k)
                    else:
                        method = cls.generic_field_content

                    history.append({
                        'content': method(field_name, v),
                        'user': item['user'],
                        'date': cls.formatted_date(item['timestamp'])
                    })

        return history[::-1]

    @classmethod
    def generic_field_content(cls, field, item):
        old_title = item['old'].title() if item['old'] else 'Empty'
        new_title = item['new'].title() if item['new'] else 'Empty'

        if item['old']:
            return '{} updated: {} ⟶ {}'.format(field, old_title, new_title)

        return '{} updated: {}'.format(field, new_title)

    @classmethod
    def stage(cls, field, item):
        return 'Stage: {} ⟶ {}'.format(item["old"].title(), item['new'].title())

    @classmethod
    def gender(cls, field, item):
        if item['old']:
            return 'Gender: {} ⟶ {}'.format(
                dict(GENDER_CHOICES)[item['old']], dict(GENDER_CHOICES)[item['new']])

        return 'Gender: {}'.format(dict(GENDER_CHOICES)[item['new']])

    @classmethod
    def place_of_registration(cls, field, item):
        if item['old']:
            return 'Place of registration: {} ⟶ {}'.format(
                dict(EMIRATES_LIST)[item['old']], dict(EMIRATES_LIST)[item['new']])

        return 'Place of registration: {}'.format(dict(EMIRATES_LIST)[item['new']])

    @classmethod
    def assigned_to(cls, field, item):
        user = cls.get_user(user_id=item['new'])

        if item['old'] and item['new'] is None:
            return '{} unassigned'.format(cls.model_name)

        if user:
            return '{} assigned to ⟶ {}'.format(
                cls.model_name,
                user.get_full_name()
            )

        return None

    @classmethod
    def get_user(cls, user_id):
        if user_id:
            try:
                return User.objects.get(pk=user_id)
            except User.DoesNotExist:
                pass

        return None

    @classmethod
    def get_file_message(cls, file):
        return file.split('URL: ')

    @classmethod
    def formatted_date(cls, date):
        if date:
            return naturalday(dateutil.parser.isoparse(date)).title()

        return date
