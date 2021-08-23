from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render


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
