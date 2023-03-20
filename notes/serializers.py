from rest_framework import serializers
from .models import Tag, Note
from rest_framework.validators import ValidationError


class TagSerializer(serializers.ModelSerializer):
    # replace related string field with id
    name = serializers.CharField(max_length=20)
    # note = serializers.StringRelatedField(many=False)

    class Meta:
        model = Tag
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=50)
    # replace id in foreignKey-field with related name
    author = serializers.StringRelatedField(many=False)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    # tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = '__all__'
