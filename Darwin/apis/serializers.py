from rest_framework import serializers
# from apis.models import User
from rest_framework_mongoengine import serializers

# class UserSerializer(serializers.DocumentSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'name', 'email', 'password', 'mobile_no']