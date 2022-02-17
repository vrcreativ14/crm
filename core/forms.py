from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from django.contrib.auth.models import User
from core.utils import add_empty_choice
from django.utils.html import strip_tags, escape

from core.models import Note, Attachment, Task

from felix.constants import TIMESLOTS_CHOICES
from motorinsurance.models import Deal


class NoteForm(forms.ModelForm):
    def __init__(self, **kwargs):
        super(NoteForm, self).__init__(**kwargs)

    class Meta:
        model = Note
        fields = ('content', )

    def clean_content(self):
        content = self.cleaned_data['content']

        return escape(strip_tags(content))


class TaskForm(forms.ModelForm):
    task_id = forms.CharField(required=False, widget=forms.HiddenInput())

    assigned_to = forms.ModelChoiceField(queryset=User.objects.none())
    time = forms.ChoiceField(choices=TIMESLOTS_CHOICES)
    date = forms.CharField()
    deal = forms.CharField(widget=forms.Select(choices=[]))
    is_completed = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={'switch': 'success'}))

    def __init__(self, **kwargs):
        self.company = kwargs.pop('company')
        create_task = kwargs.pop('create_task', None)
        model = kwargs.pop('model', None)
        super(TaskForm, self).__init__(**kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(userprofile__company=self.company, is_active=True)
        if create_task:
            self.fields['deal'] = forms.ModelChoiceField(queryset=model.objects.all())

    class Meta:
        model = Task
        fields = ('title', 'content', 'assigned_to', 'is_completed')
        exclude = ('due_datetime', )

    def clean_title(self):
        title = self.cleaned_data['title']

        return escape(strip_tags(title))

    def clean_content(self):
        content = self.cleaned_data['content']

        return escape(strip_tags(content))


class TaskSearchAndOrderingForm(forms.Form):
    search_term = forms.CharField(
        label='Search for', required=False, widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Search by deal, customer or vehicle'}))

    assigned_to = forms.ChoiceField(choices=add_empty_choice([], '-' * 5), required=False)

    created_on_after = forms.DateField(
        input_formats=['%d-%m-%Y'], label='Created after', required=False, widget=forms.TextInput(
            attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}))
    created_on_before = forms.DateField(
        input_formats=['%d-%m-%Y'], label='Created before', required=False, widget=forms.TextInput(
            attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}))

    order_by = forms.CharField(required=False)
    filter_type = forms.CharField(required=False)

    deal = forms.ModelChoiceField(
        queryset=Deal.objects.none(), required=False, empty_label='All Users')

    def __init__(self, **kwargs):
        company = kwargs.pop('company')

        super().__init__(**kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(userprofile__company=company)
        self.fields['deal'].queryset = Deal.objects.filter(company=company)
        self.fields['assigned_to'].choices = [('', 'Select user to filter'), ('unassigned', 'All Unassigned')] + list(
            (user.pk, user.get_full_name()) for user in User.objects.filter(userprofile__company=company, is_active=True).order_by('first_name'))


class AttachmentForm(forms.ModelForm):
    label = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    file = forms.FileField(widget=forms.FileInput(
        attrs={'class': 'filestyle', 'data-input': 'false', 'data-buttonname': 'btn-secondary'}
    ), required=False)

    def __init__(self, **kwargs):
        super(AttachmentForm, self).__init__(**kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('attach', 'Attach'))

    def clean_label(self):
        label = self.cleaned_data['label']

        return escape(strip_tags(label))

    class Meta:
        model = Attachment
        fields = ('label', 'file')
