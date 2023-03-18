from rest_framework import serializers
from .models import *


class NoteSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=50)

    class Meta:
        model = Note
        fields = ["id", "title", "body", "created"]
