from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from core.utils import clean_and_validate_email_addresses

from accounts.models import UserProfile, Invitation, CompanySettings, WorkspaceMotorSettings

from felix.constants import USER_ROLES, WORKSPACES


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control sm', 'placeholder': 'First Name'}))
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control sm', 'placeholder': 'Last Name'}))

    class Meta:
        model = UserProfile
        exclude = ('user', 'company', 'allowed_workspaces',)
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(
                attrs={'class': 'filestyle', 'data-input': 'false', 'data-buttonname': 'btn-secondary'}
            ),
        }


class AgentForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))

    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    email = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))

    password = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    permissions = forms.ChoiceField(choices=USER_ROLES, initial='user')

    allowed_workspaces = forms.MultipleChoiceField(
        choices=WORKSPACES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'multiselect-ui allowed-workspaces-field'}))

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(AgentForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['password'].required = False
            self.fields['email'].required = False

    def clean_email(self):
        email = clean_and_validate_email_addresses(self.cleaned_data['email'])

        if self.cleaned_data['email'] and not email:
            raise forms.ValidationError("Enter a valid email address")

        if self.instance.pk is None and self.check_user(email):
            raise forms.ValidationError("User with the same email address already exists")

        return email.lower()

    def check_user(self, email):
        return User.objects.filter(username=email).exists()

    def clean_password(self):
        user = None
        password = self.cleaned_data.get('password')

        if password:
            if self.instance.pk is not None:
                user = self.instance.user

            try:
                validate_password(password, user=user)
            except ValidationError as e:
                raise forms.ValidationError(e)

        return password

    class Meta:
        model = UserProfile
        exclude = ('user', 'company',)
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(
                attrs={'class': 'filestyle', 'data-input': 'false', 'data-buttonname': 'btn-secondary'}
            ),
        }


class InvitationForm(forms.ModelForm):
    email = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com', 'type': 'email'}))

    first_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}))

    role = forms.ChoiceField(
        choices=USER_ROLES,
        initial=('user', 'Regular User'),
        widget=forms.Select(attrs={'class': 'role-field'}))

    allowed_workspaces = forms.MultipleChoiceField(
        choices=WORKSPACES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'multiselect-ui allowed-workspaces-field'}))

    def clean_email(self):
        email = clean_and_validate_email_addresses(self.cleaned_data['email'])

        if self.cleaned_data['email'] and not email:
            raise forms.ValidationError("Enter a valid email address")

        if self.instance.pk is None and self.check_user(email):
            raise forms.ValidationError("User with the same email address already exists")

        if self.instance.pk is None and self.check_invitation(email):
            raise forms.ValidationError("Invitation already sent.")

        return email.lower()

    def check_user(self, email):
        return User.objects.filter(username=email).exists()

    def check_invitation(self, email):
        return Invitation.objects.filter(email=email, accepted=False).exists()

    class Meta:
        model = Invitation
        fields = ('email', 'first_name', 'role', 'allowed_workspaces')


class InvitationRegisterForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}))
    last_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}))
    designation = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your designation'}))

    password = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control show-toggle', 'placeholder': 'Enter your password (min. 8 characters)',
                   'type': 'password'}))
    confirm_password = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control show-toggle', 'placeholder': 'Confirm password', 'type': 'password'}))

    def clean(self):
        if self.cleaned_data["password"] != self.cleaned_data["confirm_password"]:
            self._errors['password'] = 'Passwords don\'t match'

        try:
            validate_password(self.cleaned_data["password"], user=None)
        except ValidationError as errors:
            self._errors['password'] = errors.messages[0]


class CompanySettingsAccountForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = ('displayed_name', 'phone', 'address', 'website', 'currency',)

        widgets = {
            'displayed_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.TextInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
        }


class CompanySettingsMotorCRMForm(forms.ModelForm):
    class Meta:
        model = WorkspaceMotorSettings
        fields = ('quote_expiry_days', 'auto_close_quoted_deals_in_days',)

        widgets = {
            'quote_expiry_days': forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}),
            'auto_close_quoted_deals_in_days': forms.TextInput(
                attrs={'class': 'form-control', 'type': 'number', 'min': 1}),
        }


class CompanySettingsNotificationsMotorForm(forms.ModelForm):
    class Meta:
        model = WorkspaceMotorSettings
        fields = ('email', 'bcc_all_emails', 'lead_notification_email_list', 'order_notification_email_list',
                  'send_company_email_on_lead_form_submission',
                  'send_company_email_on_order_created_online',
                  'reply_to_company_email')

        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'bcc_all_emails': forms.CheckboxInput(),
            'lead_notification_email_list': forms.Textarea(attrs={'class': 'form-control ignore-length', 'rows': '2'}),
            'order_notification_email_list': forms.Textarea(attrs={'class': 'form-control ignore-length', 'rows': '2'}),
            'send_company_email_on_lead_form_submission': forms.CheckboxInput(),
            'send_company_email_on_order_created_online': forms.CheckboxInput(),
        }

    def clean_lead_notification_email_list(self):
        return self.clean_email_addresses(self.cleaned_data['lead_notification_email_list'])

    def clean_order_notification_email_list(self):
        return self.clean_email_addresses(self.cleaned_data['order_notification_email_list'])

    def clean_email_addresses(self, emails=''):
        if len(emails):
            emails = clean_and_validate_email_addresses(emails)

            if not emails:
                raise forms.ValidationError("Invalid email format.")

        return emails


class CompanySettingsIntegrationsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = ('helpscout_client_id', 'helpscout_client_secret', 'helpscout_mailbox_id',)

        widgets = {
            'helpscout_client_id': forms.TextInput(attrs={'class': 'form-control'}),
            'helpscout_client_secret': forms.TextInput(attrs={'class': 'form-control'}),
            'helpscout_mailbox_id': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PasswordChange(forms.Form):
    old_password = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput)
    new_password = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordChange, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.user.check_password(self.cleaned_data['old_password']):
            self._errors['old_password'] = 'Current password is incorrect'

        if self.cleaned_data["new_password"] != self.cleaned_data["confirm_password"]:
            self._errors['new_password'] = 'New password doesn\'t matched'

        try:
            validate_password(self.cleaned_data["new_password"], user=self.user)
        except ValidationError as errors:
            self._errors['new_password'] = errors.messages


class LoginForm(AuthenticationForm):
    """Overrides the Django login form to allow case insensitive username handling during login."""
    def clean_username(self):
        username = self.cleaned_data['username']
        if username:
            username = username.lower()

        return username
