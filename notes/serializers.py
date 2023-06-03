from rest_framework import serializers
from .models import Tag, Note
from rest_framework.validators import ValidationError
from rest_framework.request import Request


class TagSerializer(serializers.ModelSerializer):
    # replace related string field with id
    name = serializers.CharField(max_length=20)
    note = serializers.StringRelatedField(many=False)
    

    class Meta:
        model = Tag
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    # since using modelserializer, repeating title is redundant, but places at top
    title = serializers.CharField(max_length=50)
    # replace id in foreignKey-field with related name
    author = serializers.StringRelatedField(many=False)

    # this returns tags as a string field
    tags = serializers.StringRelatedField(many=True, read_only=True)
    tag = TagSerializer(many=True, read_only=True)
    # this returns the entire tag object serialized
    # tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = '__all__'
