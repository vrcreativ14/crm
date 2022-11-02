import json
import datetime

from django.http import Http404
from django.apps import apps
from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http.response import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, View, DetailView, UpdateView
from rolepermissions.mixins import HasPermissionsMixin

from core.forms import TaskForm, TaskSearchAndOrderingForm
from core.mixins import AjaxListViewMixin, CompanyAttributesMixin
from core.models import Task
from core.utils import log_user_activity
from core.views import AddEditTaskView as CoreAddEditTaskView
from core.views import AddEditTaskView, DeleteTaskView
from felix.constants import ITEMS_PER_PAGE, DEFAULT_TIMESLOT
from healthinsurance.models.deal import Deal


class TaskBaseView(LoginRequiredMixin, CompanyAttributesMixin,
                   PermissionRequiredMixin, AjaxListViewMixin, TemplateView):
    template_name = "healthinsurance/tasks_list.html"
    permission_required = 'auth.list_health_tasks'
    default_order_by = 'due_datetime'
    default_filter = 'todo'

    def get_queryset(self):
        ContentType = apps.get_model("contenttypes", "ContentType")
        content_type = ContentType.objects.get(app_label="healthinsurance", model="deal")
        qs = Task.objects.filter(content_type=content_type, is_deleted=False)
        so_form = self.get_search_and_ordering_form()

        if so_form.is_valid():
            if so_form.cleaned_data['filter_type']:

                today = datetime.date.today()
                tomorrow = today + datetime.timedelta(days=1)

                if so_form.cleaned_data['filter_type'] == 'overdue':
                    qs = qs.filter(due_datetime__lt=today, is_completed=False)
                elif so_form.cleaned_data['filter_type'] == 'today':
                    qs = qs.filter(
                        due_datetime__year=today.year,
                        due_datetime__month=today.month,
                        due_datetime__day=today.day,
                        is_completed=False
                    )
                elif so_form.cleaned_data['filter_type'] == 'tomorrow':
                    qs = qs.filter(
                        due_datetime__year=tomorrow.year,
                        due_datetime__month=tomorrow.month,
                        due_datetime__day=tomorrow.day,
                        is_completed=False
                    )
                elif so_form.cleaned_data['filter_type'] == 'done':
                    qs = qs.filter(is_completed=True)
                elif so_form.cleaned_data['filter_type'] == 'todo':
                    qs = qs.filter(is_completed=False)
            else:
                qs = qs.filter(is_completed=False)

            if so_form.cleaned_data['assigned_to']:
                if so_form.cleaned_data['assigned_to'] == 'unassigned':
                    qs = qs.filter(assigned_to__isnull=True)
                else:
                    qs = qs.filter(assigned_to=so_form.cleaned_data['assigned_to'])

            if so_form.cleaned_data['created_on_after']:
                qs = qs.filter(created_on__gte=so_form.cleaned_data['created_on_after'])
            if so_form.cleaned_data['created_on_before']:
                qs = qs.filter(created_on__lte=so_form.cleaned_data['created_on_before'] + relativedelta(days=1))

            if so_form.cleaned_data['order_by']:
                qs = qs.order_by(so_form.cleaned_data['order_by'])
            else:
                qs = qs.order_by(self.default_order_by)

        return qs

    def get_search_and_ordering_form(self):
        data = self.request.GET
        return TaskSearchAndOrderingForm(data=data, company=self.request.company)

    def get_company_agents_list(self):
        agents = super().get_company_agents_list()

        # Removing empty option from the list so user cannot select it to unassign task.
        if agents:
            agents = agents[1:]

        return agents

    def serialize_object_list(self, records):
        company_agents = self.get_company_agents_list()

        return [{
            'pk': record.pk,
            'title': record.title,
            'attached_to': f'{record.attached_to.customer.name}',
            'created_on': record.formatted_created_on(),
            'updated_on': record.formatted_updated_on(),
            'assigned_to': (record.assigned_to and record.assigned_to.get_full_name()) or None,
            'assigned_to_name': record.assigned_to.get_full_name() if record.assigned_to else '',
            'assigned_to_id': record.assigned_to.pk if record.assigned_to else '',
            'due_in': record.due_in(),
            'due_date': record.due_datetime,
            'due_date_display': timezone.localtime(record.due_datetime).strftime('%b. %d %Y, %I:%M %p'),
            'created_on_display': timezone.localtime(record.created_on).strftime('%b. %d %Y, %I:%M %p'),
            'updated_on_display': timezone.localtime(record.updated_on).strftime('%b. %d %Y, %I:%M %p'),
            'is_overdue': record.is_overdue(),
            'is_completed': record.is_completed,
            'added_by': (record.added_by and record.added_by.get_full_name()) or None,
            'status': record.get_status_display().title(),
            'company_agents': json.dumps(company_agents),
            'update_task_field_url': reverse('health-insurance:task-update-field', kwargs={'pk': record.pk}),
        } for record in records]

    def get_deal_premium(self, deal):
        if deal.quote:
            return '{:,}'.format(deal.quote.get_least_quoted_product().get_sale_price())

        return None


class TaskView(TaskBaseView, CompanyAttributesMixin):
    def get_page(self):
        tasks = self.get_queryset()
        paginator = Paginator(tasks, per_page=ITEMS_PER_PAGE)

        return paginator.get_page(self.request.GET.get('page', 1))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if self.request.user.userprofile.has_producer_role():
            raise Http404()

        ctx['search_form'] = self.get_search_and_ordering_form()
        ctx['entity'] = "health"
        ctx['task_form'] = TaskForm(
            company=self.request.company,**{"create_task":True, "model":Deal}
        )

        # ctx['order_by'] = self.request.GET.get('order_by', self.default_order_by)
        # ctx['filter_type'] = self.request.GET.get('filter_type', self.default_filter)
        ctx['page'] = self.request.GET.get('page') or 1
        # ctx['company_agents'] = self.get_company_agents_list()

        log_user_activity(self.request.user, self.request.path)

        return ctx

class DealTaskListView(TaskBaseView):
    permission_required = 'auth.update_health_deals'

    def get(self, *args, **kwargs):
        records = self.get_queryset().filter(object_id=self.kwargs['pk'])
        return JsonResponse(self.serialize_object_list(records), safe=False)


class TaskSingleView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_health_tasks'
    model = Task

    def get(self, request, *args, **kwargs):
        task = self.get_object()

        response = {
            'pk': task.pk,
            'title': task.title,
            'content': task.content,
            'assigned_to': task.assigned_to.pk,
            'deal': task.object_id,
            'created_on': task.formatted_created_on(),
            'updated_on': task.formatted_updated_on(),
            'due_date': timezone.localtime(task.due_datetime).strftime('%d-%m-%Y'),
            'due_time': timezone.localtime(task.due_datetime).strftime('%H:%M'),
            'status': task.get_status_display().title(),
            'is_completed': task.is_completed,
        }

        return JsonResponse(response, safe=False)


class AddEditTaskView(CoreAddEditTaskView):
    permission_required = 'auth.create_health_tasks'
    model = Task
    attached_model = Deal

 
class TaskDeleteView(DeleteTaskView):
    permission_required = 'auth.update_health_tasks'
    model = Task
    attached_model = Deal


class TasksMarkAsDoneView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'auth.update_health_tasks'
    model = Task

    def post(self, request, *args, **kwargs):
        task_ids = self.request.POST.getlist('task_ids[]')

        Task.objects.filter(id__in=task_ids).update(is_completed=True)

        return JsonResponse({'success': True}, safe=False)


class TaskUpdateFieldView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'auth.update_health_tasks'

    def get_object(self, **kwargs):
        try:
            return Task.objects.get(pk=self.kwargs['pk'])
        except Task.DoesNotExist:
            raise Http404()

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        field_name = request.POST['name']
        field_value = request.POST['value']

        if task.pk != int(request.POST['pk']):
            raise Http404()

        try:
            setattr(task, field_name, field_value)
            task.save()

            response = {'success': True, 'message': 'Updated successfully'}

            log_user_activity(self.request.user, self.request.path, 'U', task)

        except Task.DoesNotExist:
            response = {'success': False, 'message': 'You do not have permissions'}

        return JsonResponse(response)


class DealsTaskAdd(AddEditTaskView):    
    permission_required = ('auth.update_health_deals',)
    attached_model = Deal