from rest_framework import serializers

from courses.models import Course, Lesson
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
