import logging
from django.utils.dateparse import parse_datetime
from datetime import date
from rolepermissions.mixins import HasPermissionsMixin
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import formset_factory
from django.views.generic import TemplateView, FormView, View, UpdateView, DetailView
from rolepermissions.roles import clear_roles, assign_role
from accounts.serializers import UserProfileSerializer

from felix.constants import ITEMS_PER_PAGE

from core.utils import log_user_activity
from core.email import Emailer

from accounts.forms import ProfileForm, AgentForm, PasswordChange, InvitationForm, InvitationRegisterForm
from accounts.models import UserProfile, Invitation

from core.intercom import Intercom
from django.db.models import Q
from rest_framework.generics import ListAPIView
from accounts.pagination import UserPagination
from collections import OrderedDict

logger = logging.getLogger('api.typeform')


class DashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.djhtml"
    permission_required = 'auth.company_dashboard'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        params = ''

        user_id = self.request.GET.get('user') or None
        if user_id:
            params = 'user={}'.format(self.request.GET['user'])

        ctx['users'] = User.objects.filter(userprofile__company=self.request.company).order_by('first_name')
        ctx['selected_user_id'] = int(user_id) if user_id else None
        ctx['entity'] = self.request.GET.get('entity')
        if self.request.GET.get('entity') == "mortgage":
            self.request.session["selected_product_line"] = "mortgage"
            ctx['params'] = self.request.get_full_path().replace(self.request.path,'').replace('?','')
            ctx['filtertype'] = self.request.GET.get('filtertype')
            if self.request.GET.get('start_date'):
                if parse_datetime(self.request.GET.get('start_date')):
                    ctx['start_date'] = parse_datetime(self.request.GET.get('start_date')).date().strftime("%m/%d/%Y") 
                    ctx['show_date'] = True
            if self.request.GET.get('end_date'): 
                if parse_datetime(self.request.GET.get('end_date')):
                    ctx['end_date'] = parse_datetime(self.request.GET.get('end_date')).date().strftime("%m/%d/%Y")
                    ctx['show_date'] = True
        else:
            self.request.session["selected_product_line"] = "motorinsurance"
            ctx['params'] = params
        ctx['entity_switch'] = True
        return ctx


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/profile.djhtml"
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return UserProfile.objects.get(user=self.request.user)

    def get(self, request, *args, **kwargs):
        profile = self.get_object()

        ctx = {
            'profile_form': ProfileForm(instance=profile),
            'profile': profile
        }
        if request.GET.get('entity') == "mortgage":
            ctx['entity'] = "mortgage"

        log_user_activity(self.request.user, self.request.path)

        return render(request, self.template_name, ctx)

    def form_valid(self, form, **kwargs):
        self.request.user.first_name = form.cleaned_data['first_name']
        self.request.user.last_name = form.cleaned_data['last_name']

        self.request.user.save()

        profile = form.save(commit=False)

        if len(form.data['remove_avatar']):
            profile = self.object
            profile.image = ''

        profile.save(user=self.request.user)

        log_user_activity(self.request.user, self.request.path, 'U')

        return JsonResponse({'success': True})

    def form_invalid(self, form, **kwargs):
        return JsonResponse({'success': False, 'errors': form.errors})


class ProfilePasswordChangeView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile_change_password.djhtml"

    def post(self, request, *args, **kwargs):
        form = PasswordChange(request.user, request.POST)

        if form.is_valid():
            self.request.user.set_password(request.POST['new_password'])
            update_session_auth_hash(request, request.user)
            request.user.save()

            log_user_activity(self.request.user, self.request.path, 'U')

            response = {'success': True}
        else:
            response = {'success': False, 'errors': form.errors}

        return JsonResponse(response)


class LockView(TemplateView):
    template_name = "accounts/lock.djhtml"

class SearchResultAgentView(LoginRequiredMixin, HasPermissionsMixin,ListAPIView):
        #required_permission = 'list_users'
        default_order_by = 'user__first_name'
        page_size = 30
        pagination_class = UserPagination
        serializer_class = UserProfileSerializer
        permission_classes = []
        def get_queryset(self):
            qs = UserProfile.objects.filter(company=self.request.company, user__is_active=True).order_by(self.default_order_by)
            return qs
        
        def get_paginated_response(self, data, page,paginator):
            return JsonResponse(OrderedDict([
            ('count', paginator.page.count),
            ('current', page),
            ('next', paginator.get_next_link()),
            ('previous', paginator.get_previous_link()),        
            ('results', data)
        ]))

        def get_page(self, **kwargs):
            
            if 'agents' in kwargs:
                agents = kwargs.get('agents')
                paginator = Paginator(agents, per_page=ITEMS_PER_PAGE)
            else:
                agents = self.get_queryset()
                paginator = Paginator(agents, per_page=ITEMS_PER_PAGE)

            return paginator.get_page(self.request.GET.get('page', 1))

        def search_user(self,key, filters):            
            qs_name = UserProfile.objects.none()
            qs_email = UserProfile.objects.none()
            qs_role = UserProfile.objects.none()
            filter_array = filters.split(',')
            # if 'name' in filters:
            #     qs_name = UserProfile.objects.filter((Q(user__first_name__icontains = key) | Q(user__last_name__contains = key)),company=self.request.company,user__is_active=True).order_by(self.default_order_by)
            #     filter_array.remove('name')
            # if 'email' in filters:
            #     qs_email = UserProfile.objects.filter(user__email__icontains = key,company=self.request.company,user__is_active=True).order_by(self.default_order_by)
            #     filter_array.remove('email')
            
            if key:
                qs_name = UserProfile.objects.filter((Q(user__first_name__icontains = key) | Q(user__last_name__contains = key)),company=self.request.company,user__is_active=True).order_by(self.default_order_by)
                qs_email = UserProfile.objects.filter(user__email__icontains = key,company=self.request.company,user__is_active=True).order_by(self.default_order_by)
                qs1 = (qs_name | qs_email ).distinct()
                qs1_copy = qs1.order_by(self.default_order_by)
            else:
                qs1_copy = self.get_queryset()
            if len(filter_array) > 1:
                for user_profile in qs1_copy:
                    if 'producer' in filters:
                        if user_profile.get_assigned_role() == 'producer':
                            qs_role |= UserProfile.objects.filter(pk = user_profile.pk)
                    if 'regular' in filters:               
                        if user_profile.get_assigned_role() == 'user':
                            qs_role |= UserProfile.objects.filter(pk = user_profile.pk)
                    if 'admin' in filters:
                        if user_profile.get_assigned_role() == 'admin':
                            qs_role |= UserProfile.objects.filter(pk = user_profile.pk)
                    if 'none' in filters:
                        if user_profile.get_assigned_role() == None:
                            qs_role |= UserProfile.objects.filter(pk = user_profile.pk)

                return qs_role.order_by(self.default_order_by)
            
            return qs1.order_by(self.default_order_by)

        def get(self, request, *args, **kwargs):            
            search_key = self.request.GET.get('search_key')
            filters = self.request.GET.get('filters')
            page = self.request.GET.get('page', 1)            
            if search_key or filters:
                qs = self.search_user(search_key, filters)
            else:
                qs = self.get_queryset()
            paginator = UserPagination()
            search_result = paginator.paginate_queryset(qs, request)
            user_serializer = UserProfileSerializer(search_result, many=True)            
            
            return paginator.get_paginated_response(user_serializer.data)            

class AgentView(LoginRequiredMixin, HasPermissionsMixin, TemplateView):
    template_name = "accounts/agents.djhtml"
    required_permission = 'list_users'
    default_order_by = 'user__first_name'

    def get_queryset(self):
        qs = UserProfile.objects.filter(company=self.request.company, user__is_active=True).order_by(self.default_order_by)

        return qs

    def get_page(self):
        agents = self.get_queryset()
        paginator = Paginator(agents, per_page=ITEMS_PER_PAGE)

        return paginator.get_page(self.request.GET.get('page', 1))

    def get_context_data(self, **kwargs):
        ctx = super(AgentView, self).get_context_data(**kwargs)

        qs = self.get_queryset()
        ctx['agents_count'] = qs.count()
        ctx['agents'] = self.get_page()

        ctx['all_agents'] = qs
        if self.request.GET.get('entity') == "mortgage":
            ctx['entity'] = "mortgage"

        log_user_activity(self.request.user, self.request.path)

        return ctx


class AgentDealsDetailsAndDeleteView(LoginRequiredMixin, HasPermissionsMixin, DetailView):
    model = UserProfile
    required_permission = 'list_users'
    default_order_by = 'user__first_name'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        motor_deals_assigned_to, motor_deals_producer = self._get_motor_deals()

        return JsonResponse({
            'agent_id': obj.pk,
            'agent_name': obj.user.get_full_name(),
            'form_action': reverse('accounts:agent-deals-and-delete', kwargs={'pk': obj.pk}),
            'motor_deals_assigned_to': motor_deals_assigned_to.count(),
            'motor_deals_producer': motor_deals_producer.count()
        })

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        user = None
        agent_id = request.POST['agent_id']
        assigned_to = request.POST.get('assigned_to')
        unassign_deals = request.POST['assign_option'] == '0'
        self._update_user_status_in_intercom()

        if agent_id != str(obj.pk):
            return JsonResponse({'success': False, 'message': 'Invalid request.'})

        if assigned_to == str(obj.pk):
            return JsonResponse({'success': False, 'message': 'Please choose another user.'})

        if not unassign_deals:
            try:
                user = UserProfile.objects.get(pk=assigned_to)
                user = user.user
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Requested user doesn\'t exists.'})

        motor_deals_assigned_to, motor_deals_producer = self._get_motor_deals()

        for deal in motor_deals_assigned_to:
            deal.assigned_to = user
            deal.save(user=self.request.user)

            log_user_activity(self.request.user, self.request.path, 'U', deal)

        for deal in motor_deals_producer:
            deal.producer = None
            deal.save(user=self.request.user)

            log_user_activity(self.request.user, self.request.path, 'U', deal)

        obj.user.is_active = False
        obj.user.save()

        return JsonResponse({'success': True})

    def _update_user_status_in_intercom(self):
        obj = self.get_object()
        intercom = Intercom()

        intercom_user_data = intercom.get_contact_by_email_and_id(obj.user.username, obj.user.pk)

        if intercom_user_data:
            intercom.update_contact(intercom_user_data['id'], {'custom_attributes': {'Deleted': True}})

    def _get_motor_deals(self):
        from motorinsurance.models import Deal

        motor_deals_assigned_to = Deal.objects.filter(assigned_to=self.get_object().user)
        motor_deals_producer = Deal.objects.filter(producer=self.get_object().user)

        return motor_deals_assigned_to, motor_deals_producer


class AgentAddView(LoginRequiredMixin, HasPermissionsMixin, FormView):
    template_name = "accounts/agent_form.djhtml"
    required_permission = 'create_users'
    form_class = AgentForm

    def get_context_data(self, **kwargs):
        ctx = super(AgentAddView, self).get_context_data(**kwargs)

        ctx['post_url'] = reverse('accounts:agent-new')

        return ctx

    def get_form_kwargs(self):
        kwargs = super(AgentAddView, self).get_form_kwargs()
        kwargs.update({'request': self.request})

        return kwargs

    def form_valid(self, form, **kwargs):
        data = form.cleaned_data

        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        agent = form.save(commit=False)
        agent.user = user
        agent.company = self.request.company

        agent.save()

        # setting user permissions
        assign_role(agent.user, data['permissions'])

        log_user_activity(self.request.user, self.request.path, 'C', agent)

        return JsonResponse(
            {'success': True, 'redirect_url': reverse('accounts:agent-edit', args=(agent.pk,))})

    def form_invalid(self, form, **kwargs):
        return JsonResponse({'success': False, 'errors': form.errors})


class AgentEditView(LoginRequiredMixin, HasPermissionsMixin, UpdateView):
    template_name = "accounts/agent_form.djhtml"
    required_permission = 'update_users'
    form_class = AgentForm

    def get_object(self, **kwargs):
        try:
            return UserProfile.objects.get(
                pk=self.kwargs['pk'], company=self.request.company, user__is_active=True)
        except UserProfile.DoesNotExist:
            raise Http404()

    def get_form_kwargs(self):
        kwargs = super(AgentEditView, self).get_form_kwargs()
        kwargs.update({'request': self.request})

        return kwargs

    def get_context_data(self, **kwargs):

        ctx = super(AgentEditView, self).get_context_data(**kwargs)
        agent = self.get_object()

        log_user_activity(self.request.user, self.request.path, 'R', self.get_object())

        ctx['form'] = AgentForm(self.request, initial={
            'first_name': agent.user.first_name,
            'last_name': agent.user.last_name,
            'permissions': agent.get_assigned_role()
        }, instance=agent)

        ctx['agent'] = agent
        ctx['post_url'] = reverse('accounts:agent-edit', args=(agent.pk,))
        if self.request.GET.get('entity') == 'mortgage':
            ctx['entity'] = "mortgage"

        ctx['all_agents'] = UserProfile.objects.filter(company=self.request.company, user__is_active=True).order_by('user__first_name').exclude(user=agent.user)

        return ctx

    def form_valid(self, form, **kwargs):
        data = form.cleaned_data

        agent = self.get_object()

        agent.user.first_name = data['first_name']
        agent.user.last_name = data['last_name']

        if data['password']:
            agent.user.set_password(data['password'])

        agent.user.save()

        form.save()

        if len(form.data['remove_avatar']):
            profile = self.get_object()
            profile.image = ''
            profile.save()

        # Updating user permissions
        clear_roles(agent.user)
        assign_role(agent.user, data['permissions'])

        log_user_activity(self.request.user, self.request.path, 'U', self.get_object())

        return JsonResponse({'success': True})

    def form_invalid(self, form, **kwargs):
        return JsonResponse({'success': False, 'errors': form.errors})


class InvitationsView(LoginRequiredMixin, HasPermissionsMixin, View):
    template_name = "accounts/invitations.djhtml"
    required_permission = 'list_users'
    formset_class = formset_factory(InvitationForm)
    formset_class_prefix = "invitations_formset"

    def get(self, request, *args, **kwargs):
        ctx = {
            'invitation_forms': self.formset_class(prefix=self.formset_class_prefix),
            'invitations_sent': self.get_sent_invitations()
        }

        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        invitations_formset = self.formset_class(request.POST, prefix=self.formset_class_prefix)

        if invitations_formset.is_valid():
            for form in invitations_formset:
                invitation = Invitation.objects.invite(form.cleaned_data)
                invitation.sender = request.user
                invitation.save()

                emailer = Emailer(request.company)
                emailer.send_invitation_email(invitation)

            return redirect(reverse("accounts:agent-invites") + "?success=1")
        else:
            ctx = {
                'invitation_forms': invitations_formset,
                'invitations_sent': self.get_sent_invitations()
            }

            return render(request, self.template_name, ctx)

    def get_sent_invitations(self):
        return Invitation.objects.filter(accepted=False).order_by('-id')


class InvitationRegisterView(View):
    template_name = "accounts/invitation_register.djhtml"
    invitation_obj = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.invitation_obj = Invitation.objects.find(kwargs['key'])
        except Invitation.DoesNotExist:
            self.invitation_obj = None

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        ctx = {
            'invitation': self.invitation_obj,
            'form': InvitationRegisterForm()
        }

        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        form = InvitationRegisterForm(request.POST)

        if form.is_valid() and self.invitation_obj:
            data = form.cleaned_data
            user = User(username=self.invitation_obj.email,
                        email=self.invitation_obj.email,
                        first_name=data['first_name'],
                        last_name=data['last_name'])
            user.set_password(data['password'])
            user.save()

            user_profile = UserProfile(user=user, company=request.company, designation=data['designation'])

            if self.invitation_obj.allowed_workspaces:
                user_profile.allowed_workspaces = self.invitation_obj.allowed_workspaces

            user_profile.save()

            assign_role(user, self.invitation_obj.role)
            self.invitation_obj.accepted = True
            self.invitation_obj.save()

            auth_user = authenticate(username=self.invitation_obj.email, password=data['password'])
            login(request, auth_user)

            return redirect('motorinsurance:deals')
        else:
            ctx = {
                'invitation': self.invitation_obj,
                'form': InvitationRegisterForm(request.POST)
            }

            return render(request, self.template_name, ctx)


class InvitationCancelView(LoginRequiredMixin, HasPermissionsMixin, UpdateView):
    required_permission = 'list_users'
    model = Invitation

    def get(self, request, *args, **kwargs):
        obj = self.get_object()

        obj.delete()

        return JsonResponse({'success': True})
