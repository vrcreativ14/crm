import re
import logging
import datetime

from django.db import connection
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

activity_logger = logging.getLogger('user_actions')
api_logger = logging.getLogger("api")


def log_user_activity(user, path, action='R', obj=None):
    actions = {
        'C': 'Create',
        'R': 'Read',
        'U': 'Update',
        'D': 'Delete',
    }

    activity_logger.info(
        "[{}], User: [{}:{}], Path: {}, Record: {}".format(
            actions[action.upper()], user.id, user.email, path, obj
        )
    )


def is_valid_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, "AE")
    except NumberParseException:
        return False

    return phonenumbers.is_possible_number(parsed_number) and phonenumbers.is_valid_number(parsed_number)


def normalize_phone_number(phone_number):
    """Given a phone number as a string, `normalize_phone_number` converts it into a standard form that we use
    all across the project.

    This is needed so that when both inserting and searching for phone numbers we work with a standard representation of
    it. Right now that representation is the `phonenumbers.PhoneNumberFormat.E164`."""
    parsed_number = phonenumbers.parse(phone_number, "AE")
    return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)


def add_empty_choice(choices, empty_label=''):
    return [(None, empty_label)] + list(choices)


def get_initials_from_the_name(name):
    initials = ''

    if name:
        name_parts = name.split(' ')[:2]
        if not name_parts:
            return ''

        if len(name_parts) == 1:
            initials = name[:2]
        else:
            for part in name_parts:
                if not part:
                    continue

                initials += part[0]

    return initials.upper()


def serialize_to_json(obj):
    options = [{'value': '', 'text': 'Select an option'}]
    for item in obj:
        options.append({
            'value': item[0],
            'text': item[1]})

    return options


def clean_and_validate_email_addresses(email_addresses):
    delimiters = ',|;'
    final_email_addresses = list()

    for email in re.split(delimiters, email_addresses):
        email = email.strip()
        if not email:
            continue

        try:
            validate_email(email)
            final_email_addresses.append(email)
        except ValidationError:
            return False

    final_email_addresses = set(final_email_addresses)

    return '; '.join(final_email_addresses)


def calculate_age(date):
    if not date:
        return 0

    today = datetime.date.today()

    return today.year - date.year - ((today.month, today.day) < (date.month, date.day))


def add_months(date, months=1):
    newmonth = (((date.month - 1) + months) % 12) + 1
    newyear = int(date.year + (((date.month - 1) + months) / 12))

    return datetime.date(newyear, newmonth, date.day)
