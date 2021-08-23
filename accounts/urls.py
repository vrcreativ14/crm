from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.urls import path, re_path
from ratelimit.decorators import ratelimit

from accounts.forms import LoginForm
from accounts.views import AgentAddView
from accounts.views import AgentDealsDetailsAndDeleteView
from accounts.views import AgentEditView
from accounts.views import AgentView
from accounts.views import DashboardView
from accounts.views import InvitationCancelView
from accounts.views import InvitationRegisterView
from accounts.views import InvitationsView
from accounts.views import LockView
from accounts.views import ProfilePasswordChangeView
from accounts.views import ProfileView
from accounts.views.settings import *

app_name = 'accounts'

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),

    path(
        'login/',
        ratelimit('login', 'ip', '5/m', block=True)(
            LoginView.as_view(template_name='accounts/login.djhtml', redirect_authenticated_user=True,
                              form_class=LoginForm)
        ),
        name='login'
    ),
    path('logout/', LogoutView.as_view(template_name='accounts/login.djhtml'), name='logout'),
    path('lock/', LockView.as_view(), name='lock'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('users/', AgentView.as_view(), name='agents'),
    path('users/add/', AgentAddView.as_view(), name='agent-new'),
    path('users/invite/', InvitationsView.as_view(), name='agent-invites'),
    re_path('users/invite/cancel/(?P<pk>.+)/', InvitationCancelView.as_view(), name='agent-invite-cancel'),

    re_path('invitation/register/(?P<key>[0-9A-Za-z]+)/', InvitationRegisterView.as_view(), name='invitation-register'),

    re_path('users/edit/(?P<pk>.+)/', AgentEditView.as_view(), name='agent-edit'),
    re_path('users/deals/(?P<pk>.+)/', AgentDealsDetailsAndDeleteView.as_view(), name='agent-deals-and-delete'),

    path('settings/', SettingsAccountView.as_view(), name='settings'),
    # path('settings/crm/', SettingsCRMView.as_view(), name='settings-crm'),
    # path('settings/notifications/', SettingsNotificationsView.as_view(), name='settings-notifications'),
    path('settings/integrations/', SettingsIntegrationsView.as_view(), name='settings-integrations'),

    re_path(
        'settings/(?P<workspace>(mt))/email-templates/(?P<type>.+)/',
        SettingsEmailTemplatesDetailView.as_view(), name='settings-email-templates-detail'),

    re_path(
        'settings/(?P<workspace>(mt))/email-templates/',
        SettingsEmailTemplatesListView.as_view(), name='settings-email-templates'),

    path('settings/mt/notifications/',
         SettingsNotificationsMotorView.as_view(), name='settings-motor-workspace-notifications'),

    re_path(
        'settings/(?P<workspace>(mt))/users/(?P<pk>.+)/',
        SettingsWorkspaceUsersAddEditView.as_view(), name='settings-workspace-users-add-edit'),

    re_path(
        'settings/(?P<workspace>(mt))/users/',
        SettingsWorkspaceUsersView.as_view(), name='settings-workspace-users'),

    re_path('settings/mt/crm/', SettingsMotorCRMView.as_view(), name='settings-workspace-motor-crm'),

    path('profile/password/', ProfilePasswordChangeView.as_view(), name='profile-password'),

    # Password reset/confirm
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.djhtml',
        email_template_name='accounts/password_reset_email.djhtml',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/accounts/password_reset/sent/',
    ), name='password_reset'),

    path(
        'password_reset/sent/',
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_sent.djhtml'),
        name='password_reset_sent'
    ),

    re_path(
        'password_reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_new_form.djhtml',
            success_url='/accounts/password_reset/success/'
        ),
        name='password_reset_confirm'
    ),

    path(
        'password_reset/success/',
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_success.djhtml'),
        name='password_reset_success'
    )
]
