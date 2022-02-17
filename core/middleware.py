from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.http.response import HttpResponseBadRequest
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from accounts.models import Company
from django.shortcuts import redirect


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

class WorkSpaceMiddleware:
    """WorkSpaceMiddleware will manage access control for workspaces"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if isinstance(request.user, User):
            user = request.user._wrapped
            if not user.is_superuser:
                if hasattr(user, 'userprofile'):
                        spaces = user.userprofile.allowed_workspaces
                        requested_app = resolve(request.path).app_names
                        if requested_app:
                            requested_app = requested_app[0] 
                        if requested_app == 'accounts':
                            if resolve(request.path).url_name == "dashboard":
                                deal = False
                                if user.userprofile.has_producer_role():
                                    deal = True
                                if request.GET.get('entity') == "mortgage":
                                    if "MG" in spaces:
                                        ...
                                    if deal:
                                        return redirect(reverse('mortgage:deals'))
                                    # else:
                                    #     return HttpResponseBadRequest(f'''
                                    #     You are not allowed to view this page.
                                    #     <a href={reverse('accounts:dashboard')}> Click to go back </a>''', status=403)
                                else:
                                    if not "MT" in spaces:
                                        return redirect(reverse('accounts:dashboard')+"?entity=mortgage")
                                    if deal:
                                        return redirect(reverse('motorinsurance:deals'))
                            elif resolve(request.path).url_name == "profile":
                                if request.GET.get('entity') == "mortgage":
                                    if "MG" in spaces:
                                        ...
                                    else:
                                        return HttpResponseBadRequest(f'''
                                        You are not allowed to view this page.
                                        <a href={reverse('accounts:dashboard')}> Click to go back </a>''', status=403)
                                else:
                                    if not "MT" in spaces:
                                        return HttpResponseBadRequest(f'''You are not allowed to view this page
                                        <a href={reverse('accounts:dashboard')}?entity=mortgage> Click to go back </a>''', status=403)

                        if requested_app == 'motorinsurance':
                            if not "MT" in spaces:
                                return redirect(reverse('mortgage:deals'))

                        elif requested_app == 'mortgage':
                            if not "MG" in spaces:
                                return redirect(reverse('motorinsurance:deals'))
                else:
                    "You are not allowed to view this page. Contact administrator"
            else:
                if not hasattr(user, 'userprofile'):
                    "You are not allowed to view this page. Contact administrator"
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
