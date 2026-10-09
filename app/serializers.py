from django.contrib.auth import get_user_model

from .models import Product
from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'



User = get_user_model()



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "password"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class VerifyEmailSerializer(serializers.Serializer):
    pre_token = serializers.CharField()
    code = serializers.CharField(min_length=6, max_length=6)


class ResendCodeSerializer(serializers.Serializer):
    pre_token = serializers.CharField()

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ConfirmPasswordSerializer(serializers.Serializer):
    pre_token = serializers.CharField()
    code = serializers.CharField(min_length=6, max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    pre_token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Parollar bir xil emas"}
            )
        return data