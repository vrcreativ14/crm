from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.generic import View
from django.shortcuts import render
from django.urls import reverse, resolve
import urllib


class HealthCheckView(View):
    def get(self, request):
        return HttpResponse("I'm still here!")


def Error403View(request, exception, template_name=None):
    data = {}
    return render(request, 'errors/403.html', data, status=403)


def Error404View(request, exception, template_name=None):
    data = {}
    return render(request, 'errors/404.html', data, status=404)


def Error500View(request, template_name=None):
    data = {'request': request}
    return render(request, 'errors/500.html', data, status=500)

class ProductURLResolver(View):
    def get(self, request, *args, **kwargs):
        base_url = request.GET.get("base_url")
        entity = request.GET.get("entity")
        url = False
        routed_url = resolve(urllib.parse.urlparse(base_url).path)

        if routed_url.namespace == "customers":
            if routed_url.url_name == "edit":
                url = base_url
                if entity == "mortgage":
                    url = reverse('customers:edit-entity', kwargs={
                        "pk":routed_url.kwargs.get('pk'),
                        "entity":"mortgage",
                    })

            elif routed_url.url_name == "edit-entity":
                url = reverse('customers:edit', kwargs={
                    "pk":routed_url.kwargs.get('pk'),
                    })
            elif routed_url.url_name == "customers":
                url = reverse('customers:customers')
                if entity == "mortgage":
                    url = reverse('customers:customers') +'?entity=mortgage'
 
        elif routed_url.namespace == "mortgage":

            if routed_url.url_name == "deal-edit":
                url = reverse('motorinsurance:deals')

            elif routed_url.url_name == "deals":
                url = reverse('motorinsurance:deals')

            elif routed_url.url_name == "banks":
                url = reverse('accounts:dashboard')
            elif routed_url.url_name == "tasks":
                url = reverse('motorinsurance:tasks')+request.GET.get("params")

        elif routed_url.namespace == "motorinsurance":
            if routed_url.url_name == "deal-edit":
                url = reverse('motorinsurance:deals')
            elif routed_url.url_name == "deals":
                url = reverse('mortgage:deals')
            elif routed_url.url_name == "renewals":
                url = reverse('accounts:dashboard')+"?entity=mortgage"
            elif routed_url.url_name == "policies":
                url = reverse('accounts:dashboard')+"?entity=mortgage"
            elif routed_url.url_name == "tasks":
                url = reverse('mortgage:tasks') + request.GET.get("params")

        elif routed_url.namespace == "accounts":
            if routed_url.url_name == "dashboard":
                url = reverse('accounts:dashboard')
                if entity == "mortgage":
                    url = reverse('accounts:dashboard')+"?entity=mortgage"
            elif routed_url.url_name == "profile":
                url = reverse('accounts:profile')
                if entity == "mortgage":
                    url = reverse('accounts:profile')+"?entity=mortgage"
            elif routed_url.url_name == "agents":
                url = reverse('accounts:agents')
                if entity == "mortgage":
                    url = reverse('accounts:agents')+"?entity=mortgage"
            elif routed_url.url_name == "settings":
                url = reverse('accounts:settings')
                if entity == "mortgage":
                    url = reverse('accounts:settings')+"?entity=mortgage"
            elif routed_url.url_name == "settings-integrations":
                url = reverse('accounts:settings-integrations')
                if entity == "mortgage":
                    url = reverse('accounts:settings-integrations')+"?entity=mortgage"
            elif routed_url.url_name == "settings-workspace-users":
                url = reverse('accounts:settings-workspace-users', args=("mt",))
                if entity == "mortgage":
                    url = reverse('accounts:settings-workspace-users')+"?entity=mortgage"
            elif routed_url.url_name == "settings-workspace-motor-crm":
                url = reverse('accounts:settings-workspace-motor-crm')
                if entity == "mortgage":
                    url = reverse('accounts:settings-workspace-motor-crm')+"?entity=mortgage"
            elif routed_url.url_name == "settings-motor-workspace-notifications":
                url = reverse('accounts:settings-motor-workspace-notifications')
                if entity == "mortgage":
                    url = reverse('accounts:settings-motor-workspace-notifications')+"?entity=mortgage"
            elif routed_url.url_name == "settings-email-templates":
                url = reverse('accounts:settings-email-templates', args=('mt',))
                if entity == "mortgage":
                    url = reverse('accounts:settings-email-templates', args=('mg',))+"?entity=mortgage"
        if not url:
            url = reverse('accounts:dashboard')
            if entity == "mortgage":
                url = reverse('accounts:dashboard')+"?entity=mortgage"

        return JsonResponse({"url": url})

