"""felix URL Configuration"""
from django.urls import path
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from urlshortening.views import get_redirect
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView

from felix.error_url_handlers import *
from felix.views import HealthCheckView
from felix.admin import global_admin


urlpatterns = [
    path('', RedirectView.as_view(url="/accounts"), name='index'),
    path('health-check/', HealthCheckView.as_view()),

    path('superadmin/', global_admin.urls),

    path('accounts/', include('accounts.urls')),
    path('people/', include('customers.urls')),
    path('motor-insurance/', include('motorinsurance.urls')),

    path('core/', include('core.urls', namespace='core')),

    path('linkshortening/', include('urlshortening.urls')),
    path('r/<str:short_id>/', get_redirect, name="short-url"),

    path('tinymce/', include('tinymce.urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
