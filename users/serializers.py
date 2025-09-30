from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import User, Payment


User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Публичный профиль для просмотра чужих аккаунтов.
    Скрываем пароль (write_only), фамилию и любую платёжную историю.
    """
    class Meta:
        model = User
        # только «общая информация» — без last_name и, разумеется, без пароля
        fields = ['id', 'username', 'email', 'first_name', 'city', 'avatar', 'date_joined', 'last_login']
        read_only_fields = fields  # на всякий случай


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'password', 'phone', 'city', 'avatar',
            'is_active', 'is_staff', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'is_staff', 'is_active', 'date_joined', 'last_login']

    def create(self, validated_data):
        pwd = validated_data.pop('password', None)
        if not pwd:
            raise serializers.ValidationError({'password': 'Обязательное поле.'})
        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user

    def update(self, instance, validated_data):
        pwd = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if pwd:
            user.set_password(pwd)
            user.save(update_fields=['password'])
        return user


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','email','username','password','first_name','last_name','phone','city']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
