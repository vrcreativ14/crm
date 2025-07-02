"""Override templates for Django error pages"""
from django.conf.urls import handler403, handler404, handler500
from felix.views import Error403View, Error404View, Error500View

handler403 = Error403View
handler404 = Error404View
handler500 = Error500View
