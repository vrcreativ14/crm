from rest_framework.permissions import BasePermission
from rest_framework.authtoken.models import Token
from re import sub

def get_request_user(request):
    #header_token = request.META.get('HTTP_AUTHORIZATION', None)
    #if header_token is not None:
      try:
        token = sub('Token ', '', request.META.get('HTTP_AUTHORIZATION', None))
        token_obj = Token.objects.get(key = token)
        request.user = token_obj.user
        return token_obj.user
      except Token.DoesNotExist:
        pass

class HasAdminRolePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        profile = user.userprofile

        return profile.has_admin_role() or user.is_superuser
