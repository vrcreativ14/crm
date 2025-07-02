import time
import json
import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.http import HttpResponse
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView
from django.shortcuts import render, redirect
from django.utils.html import strip_tags, escape
from django.views.generic import FormView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from core.forms import NoteForm, AttachmentForm, TaskForm
from core.models import Note, Attachment, Task
from core.utils import log_user_activity
from core.email import Emailer
from felix.constants import COUNTRIES, WORKSPACE_MOTOR


class AddNoteView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = None
    form_class = NoteForm
    model = None

    def add_history(self, note):
        audit_history = note.attached_to.get_audit_trail()
        audit_history.record_note_history('add note', note, self.request.user)
        audit_history.save()

    def get_object(self):
        return self.model.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        obj = self.get_object()

        note = form.save(commit=False)
        note.attached_to = obj
        note.added_by = self.request.user
        note.save()

        if hasattr(obj, 'get_audit_trail'):
            self.add_history(note)

        return JsonResponse({
            'success': True,
            'note': {
                'note_pk': note.pk,
                'content': note.content,
                'pk': note.pk,
                'created_on': datetime.datetime.now().strftime("%B %d, %Y %I:%M %p"),
                'added_by': note.added_by.get_full_name(),
                'user_url': reverse('accounts:agent-edit', kwargs={'pk': note.added_by.pk})
            }
        })

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors})


class DeleteNoteView(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, View):
    permission_required = None
    attached_model = None
    model = Note

    def get_success_url(self, attached_obj):
        raise NotImplemented

    def post(self, request, *args, **kwargs):
        note = self.get_object()

        if note.content_type != ContentType.objects.get_for_model(self.attached_model):
            return HttpResponseBadRequest()

        if note.system_generated:
            return HttpResponseForbidden('You do not have permission to delete system generated notes')

        attached_obj = note.attached_to
        if hasattr(attached_obj, 'get_audit_trail'):
            self.add_history(note)

        note.delete()
        return HttpResponseRedirect(self.get_success_url(attached_obj))

    def add_history(self, note):
        audit_history = note.attached_to.get_audit_trail()
        audit_history.record_note_history('delete note', note, self.request.user)
        audit_history.save()


class AddAttachmentView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = AttachmentForm
    permission_required = None
    model = None

    def get_object(self):
        return self.model.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        obj = self.get_object()

        if not len(self.request.FILES):
            return JsonResponse({'success': False})
        else:
            file = list(self.request.FILES.values())[0]

        attachment = Attachment(company=self.request.company, attached_to=obj)
        attachment.label = file.name
        attachment.added_by = self.request.user
        attachment.file = file
        attachment.save()

        if hasattr(obj, 'get_audit_trail'):
            audit_trail = obj.get_audit_trail()
            audit_trail.record_generic_history(
                'attach file',
                f'Attached new file. Label: {attachment.label}. URL: {attachment.get_file_url()}',
                self.request.user
            )
            audit_trail.save()

        return JsonResponse({
            'success': True,
            'file': {
                'pk': attachment.pk,
                'url': attachment.get_url_for_linking_in_frontend(),
                'extension': attachment.get_file_extension(),
                'label': attachment.label,
                'added_by': attachment.added_by.get_full_name() if attachment.added_by else None,
                'user_url': reverse('accounts:agent-edit', kwargs={'pk': attachment.added_by.pk}),
                'created_on': datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")
            }
        })

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors})


class UpdateAttachmentView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'auth.update_customers'
    model = Attachment

    def post(self, request, *args, **kwargs):
        attachment = self.get_object()
        label = escape(strip_tags(request.POST['value']))

        success = True
        message = ''
        data = {}

        try:
            if not label:
                success = False
                message = 'Label required.'
            else:
                attachment.label = label
                attachment.save()

                success = True
                message = 'Updated successfully'

                data = {'name': 'label', 'value': label}

                log_user_activity(self.request.user, self.request.path, 'U', attachment)

        except Attachment.DoesNotExist:
            success = False
            message = 'You do not have permissions'

        return JsonResponse({'success': success, 'message': message, 'data': data, 'id': attachment.id})


class DeleteAttachmentView(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, View):
    permission_required = None
    attached_model = None
    model = Attachment

    def get_success_url(self, attached_obj):
        raise NotImplemented

    def post(self, request, *args, **kwargs):
        attachment = self.get_object()

        if attachment.content_type != ContentType.objects.get_for_model(self.attached_model):
            return HttpResponseBadRequest()

        attached_obj = attachment.attached_to
        if hasattr(attached_obj, 'get_audit_trail'):
            audit_trail = attached_obj.get_audit_trail()
            audit_trail.record_generic_history(
                'remove attachment',
                f'Removed attachment. Label: {attachment.label}. URL: {attachment.get_file_url()}',
                self.request.user
            )
            audit_trail.save()

        attachment.delete()

        return HttpResponseRedirect(self.get_success_url(attached_obj))


class AddEditTaskView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = None
    form_class = TaskForm
    model = Task
    attached_model = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'company': self.request.company})

        return kwargs

    def add_history(self, task, updating=False):
        audit_history = task.attached_to.get_audit_trail()
        audit_history.record_task_history('update task' if updating else 'add task', task, self.request.user)
        audit_history.save()

    def get_object(self):
        if self.request.POST.get('task_id'):
            return self.model.objects.get(pk=self.request.POST.get('task_id'))
        else:
            return None

    def get_attached_to_object(self):
        return self.attached_model.objects.get(pk=self.request.POST.get('deal'))

    def post(self, request, *args, **kwargs):
        instance = None
        attached_to = self.get_attached_to_object()
        instance = self.get_object()
        updating = bool(instance)

        params = {'data': request.POST, 'company': request.company}

        if instance:
            params['instance'] = instance

        form = TaskForm(**params)

        if form.is_valid():
            task = form.save(commit=False)
            task.attached_to = attached_to
            task.added_by = self.request.user

            due_date = datetime.datetime.strptime(
                '{} {}'.format(form.cleaned_data['date'], form.cleaned_data['time']), '%d-%m-%Y %H:%M'
            )

            task.due_datetime = due_date
            task.save()

            if hasattr(attached_to, 'get_audit_trail'):
                if instance:
                    self.add_history(task, updating)

            return JsonResponse({
                'success': True,
                'updated': updating,
                'task': {
                    'pk': task.pk,
                    'object_id': task.object_id,
                    'title': task.title,
                    'content': task.content,
                    'due_date': task.due_datetime,
                    'created_on': task.created_on.strftime("%B %d, %Y %I:%M %p"),
                    'added_by': task.added_by.get_full_name(),
                    'is_completed': task.is_completed,
                    'user_url': reverse('accounts:agent-edit', kwargs={'pk': task.added_by.pk})
                }
            })

        else:
            return JsonResponse({'success': False, 'errors': form.errors})


class DeleteTaskView(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, View):
    permission_required = None
    attached_model = None
    model = Task

    def get(self, request, *args, **kwargs):
        if request.user.userprofile.has_admin_role():
            task = self.get_object()

            if task.content_type != ContentType.objects.get_for_model(self.attached_model):
                return HttpResponseBadRequest()

            attached_obj = task.attached_to
            if hasattr(attached_obj, 'get_audit_trail'):
                self.add_history(task)

            task.is_deleted = True
            task.save()
        else:
            return JsonResponse({'success': False, 'error': 'You don\'t have permissions to delete this record.'})

        return JsonResponse({'success': True})

    def add_history(self, task):
        audit_history = task.attached_to.get_audit_trail()
        audit_history.record_task_history('delete task', task, self.request.user)
        audit_history.save()


class GetCountriesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        countries = [{'value': '', 'text': 'Select an option'}]

        for country in COUNTRIES:
            countries.append({
                'value': country[0],
                'text': country[1]})

        return JsonResponse(countries, safe=False)
