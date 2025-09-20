from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with username, email and password"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password_confirm")

    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login that accepts either email or username"""
    email_or_username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        """Validate and authenticate the user with email OR username"""
        email_or_username = attrs.get("email_or_username")
        password = attrs.get("password")

        if not email_or_username or not password:
            raise serializers.ValidationError(
                {"detail": _('Must include "email_or_username" and "password".')}
            )

        try:
            # Try to find user by email OR username
            user_obj = User.objects.get(Q(email=email_or_username) | Q(username=email_or_username))
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": _("Invalid credentials.")})

        # Always authenticate using the email field (USERNAME_FIELD = "email")
        user = authenticate(
            request=self.context.get("request"),
            username=user_obj.email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError({"detail": _("Invalid credentials.")})

        if not user.is_active:
            raise serializers.ValidationError({"detail": _("User account is disabled.")})

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for returning user data"""
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")
