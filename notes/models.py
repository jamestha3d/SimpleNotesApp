
from django.db import models
from django.contrib.auth import get_user_model
from safedelete.models import SafeDeleteModel
from safedelete.managers import SafeDeleteManager
from safedelete import DELETED_VISIBLE_BY_PK
from django.utils.timezone import now
import uuid
from django.db import transaction
# Create your models here.

User = get_user_model()
class SafeDeleteModel(SafeDeleteModel):
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.CharField(max_length=255, null=True, default='')
    deleted_at = models.DateTimeField(null=True, default=None)

    def delete(self):
        self.is_deleted = True
        self.deleted_at = now()
        return super().delete()

class MyModelManager(SafeDeleteManager):
    #modify manager for soft delete model
    _safedelete_visibility = DELETED_VISIBLE_BY_PK

class Tag(models.Model):
    name = models.CharField(max_length=20)
    note = models.ForeignKey(
        'Note', on_delete=models.CASCADE, blank=True, related_name="tags")

    def __str__(self) -> str:
        return self.name


class NoteModel(models.Model):
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

class Post(SafeDeleteModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="posts")
    title = models.CharField(max_length=40)
    body = models.TextField(blank=True, null=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(default=now)
    objects = MyModelManager()

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-created"]


class BlogModel(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="blogs")
    title = models.CharField(max_length=40)
    body = models.TextField(blank=True, null=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(default=now)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-created"]

class Blog(BlogModel):
    """Add Model Logic Here"""
    pass

class Note(NoteModel):
    """Add Note Logic Here"""
    pass

class PaymentMethod(models.Model):
    guid = models.UUIDField(db_column='GUID', primary_key=True, max_length=36, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="payment_method")
    default = models.BooleanField(default=True)
    payment_id = models.CharField(max_length=100, blank=False, null=True, default=None)
    payment_json = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.default:
            return super().save(*args, **kwargs)
        with transaction.atomic():
            PaymentMethod.objects.filter(user=self.user, default=True).update(default=False)
            return super().save(*args, **kwargs)