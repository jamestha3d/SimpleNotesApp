
from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=20)
    note = models.ForeignKey(
        'Note', on_delete=models.CASCADE, blank=True, related_name="tags")

    def __str__(self) -> str:
        return self.name


class Note(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, related_name="notes")
    title = models.CharField(max_length=40)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title

    def tag_not_exists(self, tag_name) -> bool:
        return tag_name not in [tag.name for tag in self.tags.all()]

    class Meta:
        ordering = ["-created"]
