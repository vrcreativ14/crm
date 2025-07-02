from rest_framework.permissions import BasePermission
from rest_framework.authtoken.models import Token
from re import sub
from accounts.models import UserProfile

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
        profile_id = request.query_params.get('up')  #getting user profile id from request query parameters
        profile = UserProfile.objects.filter(id = profile_id)
        if profile.exists():
            if profile[0].has_admin_role or profile[0].user.is_superuser:
                return super().has_permission(request, view)
            else:
                return False
        else:
            return False
