from rest_framework import serializers
from .models import UserProfile, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','email','username']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    role = serializers.SerializerMethodField("get_assigned_role")

    
    class Meta:
        model = UserProfile
        fields = ['user','company','phone','allowed_workspaces','role','id']

    def get_assigned_role(self, obj):
        role = UserProfile.get_assigned_role(obj)
        return role
