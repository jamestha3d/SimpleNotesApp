from rest_framework import serializers
from .models import *
from rest_framework.validators import ValidationError


class NoteSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=50)
    # replace id in foreignKey-field with related name
    author = serializers.StringRelatedField(many=False)

    # replace id in many-to-many-field with related name 'name'
    tags = serializers.SlugRelatedField(many=True, read_only=True,
                                        slug_field='name')

    class Meta:
        model = Note
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    # replace related string field with id

    class Meta:
        model = Tag
        fields = '__all__'

    def validate(self, attrs):
        invalid_tag = Tag.objects.filter(name=attrs['name']).exists()
        if invalid_tag:
            raise ValidationError("Invalid Tag")
        return super().validate(attrs)

    # overwrite the create method with custom method to hide password chars in admin view
    def create(self, validated_data):
        tag = super().create(validated_data)
        return tag
