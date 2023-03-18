from rest_framework import serializers
from .models import *


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
