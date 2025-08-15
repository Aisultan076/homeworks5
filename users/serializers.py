from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import ConfirmationCode
from django.contrib.auth import authenticate
from users.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Неверный email или пароль")
        data['user'] = user
        return data

class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'phone', 'birth_date']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            phone=validated_data.get('phone'),
            birth_date=validated_data.get('birth_date')
        )
        return user

    def validate_username(self, email):
        try:
            CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return email
        raise ValidationError('User already exists!')


class ConfirmUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")

        try:
            confirmation = ConfirmationCode.objects.get(user=user)
        except ConfirmationCode.DoesNotExist:
            raise serializers.ValidationError("Код подтверждения не найден")

        if confirmation.code != code:
            raise serializers.ValidationError("Неверный код подтверждения")

        attrs['user'] = user  # сохраним пользователя для save()
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.is_active = True
        user.save()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        if user.birthday:
            token['birthday'] = str(user.birthday)
        else:
            token['birthday'] = None
        return token

    def validate(self, attrs):
        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password')
        }
        user = authenticate(**credentials)

        if user is None or not user.is_active:
            raise serializers.ValidationError(
                "Не найдено активной учетной записи с указанными данными"
            )

        data = super().validate(attrs)
        data['birthday'] = str(user.birthday) if user.birthday else None
        return data
