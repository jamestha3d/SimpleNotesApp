
from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

"""
 class Note:
    id int
    title str(50)
    body text
    created datetime
"""

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self) -> str:
        return self.name


class Note(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, related_name="notes")
    title = models.CharField(max_length=40)
    body = models.TextField()
    tags = models.ManyToManyField(
        Tag, blank=True, related_name="note")
    created = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-created"]
