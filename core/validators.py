from django.core.exceptions import ValidationError


class MaximumLengthValidator(object):
    PASSWORD_MAX_LENGTH = 100

    def validate(self, password, user=None):
        if len(password) > self.PASSWORD_MAX_LENGTH:
            raise ValidationError(
                "This password is too big. It should not exceed {} characters.".format(self.PASSWORD_MAX_LENGTH),
                code='password_max_length_exceeded',
            )

    def get_help_text(self):
        return "Your password should not exceed the length of {}".format(self.PASSWORD_MAX_LENGTH)
