from rest_framework import serializers
from rest_framework.validators import ValidationError
from rest_framework import serializers
from .models import User
from rest_framework.authtoken.models import Token


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=80)
    username = serializers.CharField(max_length=45)
    # hide
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def validate(self, attrs):
        email_exists = User.objects.filter(email=attrs['email']).exists()
        if email_exists:
            raise ValidationError("Email has already been used")
        return super().validate(attrs)

    # overwrite the create method with custom method to hide password chars in admin view
    def create(self, validated_data):
        password = validated_data.pop("password")

        user = super().create(validated_data)
        # actually update and hash password
        user.set_password(password)
        user.save()
        Token.objects.create(user=user)
        return user


class CurrentUserNotesSerializer(serializers.ModelSerializer):
    # notes = serializers.StringRelatedField(many=True)
    notes = serializers.HyperlinkedRelatedField(
        many=True, view_name="note_detail", queryset=User.objects.all()
    )
    # url = serializers.HyperlinkedIdentityField(view_name="current_user")

    class Meta:
        model = User
        fields = ["id", "username", "email", "notes"]
