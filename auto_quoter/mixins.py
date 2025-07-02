from django.http import HttpResponseForbidden


class CompanyAutoQuotationAllowedMixin:
    def dispatch(self, request, *args, **kwargs):
        if hasattr(request, 'company'):
            if not request.company.companysettings.auto_quote_allowed:
                return HttpResponseForbidden('You do not have access to the auto quote apis')

        return super(CompanyAutoQuotationAllowedMixin, self).dispatch(request, *args, **kwargs)
