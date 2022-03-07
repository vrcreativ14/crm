import logging

from django.contrib.humanize.templatetags.humanize import naturalday

from django.http.response import JsonResponse
from django.core.exceptions import PermissionDenied
from dirtyfields.dirtyfields import DirtyFieldsMixin
from django.contrib.contenttypes.models import ContentType
from felix.constants import ITEMS_PER_PAGE
from core.models import AuditTrail

from django.contrib.auth.models import User


class AuditTrailMixin(DirtyFieldsMixin):
    ignored_fields = []

    def get_audit_trail(self):
        audit_trail, created = AuditTrail.objects.get_or_create(content_type=ContentType.objects.get_for_model(self),
                                                                object_id=self.pk)
        return audit_trail

    def format_field_value(self, field_name, value):
        if value is not None:
            return str(value)

        return value

    def save(self, *args, **kwargs):
        saving_user = kwargs.pop('user', None)
        if saving_user is None:
            logger = logging.getLogger('security')
            logger.warning('Trying to save a {} without logging the saving user'.format(
                self._meta.label
            ))

        changed_fields = self.get_dirty_fields(verbose=True, check_relationship=True)
        creating = self.pk is None

        # Do a save here so even if it's a new object the PK has been set by the time we call `get_audit_trail`
        super(AuditTrailMixin, self).save(*args, **kwargs)

        audit_trail = self.get_audit_trail()
        audit_trail.record_edit({
            field_name: {
                'old': self.format_field_value(field_name, changed_fields[field_name]['saved']),
                'new': self.format_field_value(field_name, changed_fields[field_name]['current']),
            } for field_name in changed_fields.keys() if field_name not in self.ignored_fields
        }, saving_user, creating)
        audit_trail.save()

    def delete(self, *args, **kwargs):
        audit_trail = self.get_audit_trail()
        audit_trail.record_deletion(kwargs.pop('user', None))
        audit_trail.save()

        super(AuditTrailMixin, self).delete(*args, **kwargs)


class AjaxListViewMixin():
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            records = self.get_page()

            response = {
                'records': self.serialize_object_list(records.object_list),
                'count': records.paginator.count,
                'pages': records.paginator.num_pages,
                'per_page': ITEMS_PER_PAGE,
                'current_page': int(request.GET.get('page', 1))
            }

            return JsonResponse(response, safe=False)

        return super().get(request, *args, **kwargs)

    def get_natural_date(self, date):
        return naturalday(date)


class AdminAllowedMixin():
    def dispatch(self, *args, **kwargs):
        if not self.request.user.userprofile.has_admin_role():
            raise PermissionDenied

        return super().dispatch(*args, **kwargs)


class CompanyAttributesMixin():

    def get_company_user_admin_list(self):
        from accounts.models import UserProfile
        users = [{'value': -1, 'text': '-----'}]
        for up in UserProfile.objects.filter(company=self.request.company, user__is_active=True) \
                                     .order_by('user__first_name'):
            if up.has_admin_role() or up.has_user_role():
                users.append({
                    'value': up.user.pk,
                    'text': str(up.user)
                })

        return users

    def get_company_agents_list(self):
        logged_in_user = self.request.user

        agents = [{'value': -1, 'text': '-----'}, {
            'value': logged_in_user.id,
            'text': logged_in_user.get_full_name() if logged_in_user.get_full_name() else logged_in_user.username
        }]
        for user in User.objects.filter(userprofile__company=self.request.company, is_active=True) \
                                .exclude(pk=logged_in_user.id) \
                                .order_by('first_name'):
            agents.append({
                'value': user.pk,
                'text': str(user)
            })

        return agents

    def get_company_producers_list(self):
        from accounts.models import UserProfile

        producers = [{'value': -1, 'text': '-----'}]
        for up in UserProfile.objects.filter(company=self.request.company, user__is_active=True) \
                                     .order_by('user__first_name'):
            if up.has_producer_role():
                producers.append({
                    'value': up.user.pk,
                    'text': str(up.user)
                })

        return producers
