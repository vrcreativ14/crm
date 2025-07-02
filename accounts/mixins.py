from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from accounts.models import Company


class LoginRequiredMixin(object):
    """Makes sure the user is logged in"""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.request.company = Company.objects.get(pk=settings.COMPANY_ID)
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)
