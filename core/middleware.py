from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse

from accounts.models import Company


class AjaxRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if isinstance(response, HttpResponseRedirect) and request.is_ajax():
            return JsonResponse({
                'redirect': True,
                'url': response.url
            })

        return response


class CompanyMiddleware:
    """AccountSecurityMiddle Does security checks on the logged in user."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.company = Company.objects.get(pk=settings.COMPANY_ID)

        return self.get_response(request)


class RemoteAddressMiddleware:
    """Sets the remote address correctly if there is an X-Forwarded-For header in the request.

    If the application is behind a reverse proxy (like Nginx or AWS ALB or Azure LB) the client IP is set in the
    X-Forwarded-For header. This middleware extracts that if available and sets the remote address to that value.

    This helps in using the correct IP address for rate limiting and stuff."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            client_ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[-1]
            client_ip = client_ip.strip()

            if ':' in client_ip:
                client_ip = client_ip.split(':')[0]

            request.META['REMOTE_ADDR'] = client_ip.strip()

        return self.get_response(request)
