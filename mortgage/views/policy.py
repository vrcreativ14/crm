from django.views.generic import TemplateView


class MortgagePolicy(TemplateView):
    template_name = "mortgage-policies.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super(MortgagePolicy, self).get_context_data(**kwargs)
        ctx["entity"] = "mortgage"
        return ctx

