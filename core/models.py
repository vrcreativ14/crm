import datetime
import uuid

from django.contrib.humanize.templatetags.humanize import naturaltime, naturalday

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils.timezone import now as tz_now

from felix.constants import FIELD_LENGTHS


class NotesManager(models.Manager):
    def get_notes_for_object(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        pk = obj.pk

        return self.filter(content_type=ct, object_id=pk)


class Note(models.Model):
    NOTE_TEXT = 'text'
    NOTE_CALL = 'call'
    NOTE_MEETING = 'meeting'
    NOTE_SMS = 'sms'
    NOTE_EMAIL = 'email'
    NOTE_TYPES = (
        (NOTE_TEXT, 'Note'),
        (NOTE_CALL, 'Call record'),
        (NOTE_MEETING, 'Meeting minutes'),
        (NOTE_SMS, 'SMS record'),
        (NOTE_EMAIL, 'Email record')
    )

    DIRECTION_NONE = 'none'
    DIRECTION_IN = 'incoming'
    DIRECTION_OUT = 'outgoing'
    NOTE_DIRECTIONS = (
        (DIRECTION_NONE, 'Not applicable'),
        (DIRECTION_IN, 'Incoming communication from client'),
        (DIRECTION_OUT, 'Outgoing communication to client')
    )

    objects = NotesManager()

    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    attached_to = GenericForeignKey()

    note_type = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=NOTE_TYPES, default=NOTE_TEXT)
    note_direction = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=NOTE_DIRECTIONS, default=DIRECTION_NONE)
    content = models.TextField()

    system_generated = models.BooleanField(default=False)

    added_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    updated_on = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ['-created_on']


class AuditTrail(models.Model):
    """A simple model to keep track of changes to some of the models in our application.

    We manually mark models to keep audit trails. There are a number of options out there, but we created a custom one
    because we have the ability to use a Postgres JSON field to track history, instead of having to create a new row
    for each model change."""
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    audited_object = GenericForeignKey()

    change_history = models.JSONField(default=list, encoder=DjangoJSONEncoder)

    def _serialize_user(self, user):
        return {
            'pk': user.pk,
            'username': user.username
        } if user else None

    def _serialize_note(self, note):
        return {
            'pk': note.pk,
            'note_type': note.note_type,
            'note_direction': note.note_direction,
            'content': note.content
        }

    def _serialize_task(self, task):
        return {
            'pk': task.pk,
            'due_datetime': task.due_datetime,
            'title': task.title,
            'content': task.content
        }

    def record_edit(self, changed_fields, user=None, created=False):
        self.change_history.append({
            'type': 'create' if created else 'edit',
            'changes': changed_fields,

            'user': self._serialize_user(user),
            'timestamp': tz_now()
        })

    def record_deletion(self, user=None):
        self.change_history.append({
            'type': 'delete',

            'user': self._serialize_user(user),
            'timestamp': tz_now()
        })

    def record_note_history(self, operation_type, note, user=None):
        self.change_history.append({
            'type': operation_type,
            'note': self._serialize_note(note),

            'user': self._serialize_user(user),
            'timestamp': tz_now()
        })

    def record_task_history(self, operation_type, task, user=None):
        self.change_history.append({
            'type': operation_type,
            'task': self._serialize_task(task),

            'user': self._serialize_user(user),
            'timestamp': tz_now()
        })

    def record_generic_history(self, _type, message, user=None):
        self.change_history.append({
            'type': _type,
            'message': message,

            'user': self._serialize_user(user),
            'timestamp': tz_now()
        })


class Attachment(models.Model):
    def get_file_upload_path(self, filename):
        base_path = 'attachments/{}-{}/{}-{}'.format(self.company.pk, slugify(self.company.name),
                                                     slugify(self.content_type.name), self.object_id)

        date_component = datetime.datetime.utcnow().strftime('%Y-%m-%d')

        return f'{base_path}/{date_component}_{uuid.uuid4().hex}_{filename}'

    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    attached_to = GenericForeignKey()
    

    label = models.CharField(max_length=1000, blank=True)
    file = models.FileField(max_length=FIELD_LENGTHS['file'], upload_to=get_file_upload_path)

    added_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True)

    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    updated_on = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ['label']

    def get_file_extension(self):
        return self.file.name.rsplit('.', 1)[-1]

    def get_file_url(self):
        return '{}{}'.format(self.file.url, settings.AZURE_STORAGE_SHARED_TOKEN) if self.file.url else ''

    def can_preview_in_frontend(self):
        """Returns True if the file extension is in a list of extensions that we allow previewing in the browser.

        This was added when an XSS vulnerability was detected. The user could upload files that could contain <script>
        tags like SVG and HTML. When the user clicks on the file, we open it up in a new browser window.

        If there is a script tag inside the document, it is then executed. The solution for this is to only allow
        opening files in the browser that have an extension that we have approved."""
        return self.get_file_extension() in ['jpg', 'png', 'pdf']

    def get_url_for_linking_in_frontend(self):
        """Returns a URL that can be used to link to this file in the frontend.

        Using the `can_preview_in_frontend` method, if preview is not allowed, this method will add a parameter to the
        signed S3 URL that forces the browser to download the file instead of allowing it to be previewed in the
        browser."""
        if self.can_preview_in_frontend():
            return self.get_file_url()
        else:
            return self.file.storage.url(self.file.name)


class TaskManager(models.Manager):
    def get_tasks_for_object(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        pk = obj.pk

        return self.filter(content_type=ct, object_id=pk)


class Task(models.Model):
    objects = TaskManager()

    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    attached_to = GenericForeignKey()

    title = models.CharField(max_length=FIELD_LENGTHS['title'])
    content = models.TextField(blank=True)

    assigned_to = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, related_name='assigned_to')

    due_datetime = models.DateTimeField()

    is_completed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    added_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    updated_on = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ['-created_on']

    def get_status_display(self):
        if self.is_completed:
            return 'done'
        elif self.is_overdue():
            return 'overdue'
        else:
            return 'todo'

    def is_overdue(self):
        return self.due_datetime < tz_now() and not self.is_completed

    def due_in(self):
        diff = self.due_datetime - tz_now()

        if diff.days == 0:
            return '{0:.0f} hours'.format(divmod(diff.total_seconds(), 60)[0] / 60)
        elif diff.days > 0:
            return '{} {}'.format(
                diff.days, 'day' if diff.days == 1 else 'days')
        else:
            return naturaltime(self.due_datetime)

    def formatted_created_on(self):
        diff = (tz_now() - self.created_on).days

        if diff:
            return '{} {} ago'.format(
                diff, 'day' if diff == 1 else 'days')
        else:
            return naturaltime(self.created_on)

    def formatted_updated_on(self):
        diff = (tz_now() - self.updated_on).days

        if diff:
            return '{} {} ago'.format(
                diff, 'day' if diff == 1 else 'days')
        else:
            return naturaltime(self.updated_on)
