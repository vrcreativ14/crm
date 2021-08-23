from rest_framework.permissions import BasePermission


class HasAdminRolePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        profile = user.userprofile

        return profile.has_admin_role() or user.is_superuser
