
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from safedelete.models import SafeDeleteModel
from safedelete.managers import SafeDeleteManager
from safedelete import DELETED_VISIBLE_BY_PK
from django.utils.timezone import now
import uuid
from django.db import transaction
import datetime
# Create your models here.

#version
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import json
from django.utils.functional import cached_property
from django.core.serializers.json import DjangoJSONEncoder

User = get_user_model()

class GUIDModel(models.Model):
    """
    Mixin for providing a model with a unique GUID
    """
    guid = models.UUIDField(primary_key=True, max_length=40, default=uuid.uuid4)
    created = models.DateTimeField(editable=True, null=True, default=now)
    modified = models.DateTimeField(editable=False, null=True, default=now)

    def save(self, *args, **kwargs):
        """
        On save, update timestamps
        """
        if not self.created:
          self.created = timezone.now()

        self.modified = timezone.now()

        return super(GUIDModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True

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
        

class VersionedModelMixin(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')
    version_number = models.PositiveIntegerField()
    comments = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    fields_json = models.JSONField(encoder=DjangoJSONEncoder)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        abstract = True

    def __str__(self):
        return f"Version {self.version_number} of {self.content_object}"

    def revert(self):
        #revert the original model to this version
        fields_json = self.deserialize_json_fields()
        for field_name, field_value in fields_json.items():
            setattr(self.content_object, field_name, field_value)
        self.content_object.save()

    def register_model(self):
        #save some extra information here
        pass

    @classmethod
    def create_version(cls, instance, creator, version_number=None, comments=None):
        if not instance:
            return #raise Exception
        #TODO make creator request.user
        fields_json = cls.serialize_json_fields(cls, instance)
        if not version_number:
            #if version_number is not provided, calculate the highest version_number + 1
            highest_version = cls.objects.filter(content_type=ContentType.objects.get_for_model(instance), object_id=str(instance.pk)).order_by('-version_number').first()
            version_number = highest_version.version_number + 1 if highest_version else 1

        version = cls(
            content_type=ContentType.objects.get_for_model(instance),
            object_id=str(instance.pk),
            content_object=instance,
            version_number=version_number,
            fields_json=fields_json,
            creator=creator,
            comments=comments
        )
        version.save()
        return version
    
    def deserialize_json_fields(self):
        fields_json = self.fields_json
        result_dict = {}
        for field_name, field_value in fields_json.items():
            field = self._model._meta.get_field(field_name)
            if isinstance(field, models.ManyToManyField):
                related_model = field.related_model
                related_instances = related_model.objects.filter(pk__in=field_value)
                result_dict[field_name] = related_instances
            elif isinstance(field, models.ForeignKey):
                related_model = field.related_model
                try:
                    print("FOREIGN_KEY_VALUE", field_value)
                    related_instance = related_model.objects.get(pk=field_value)
                    result_dict[field_name] = related_instance
                except related_model.DoesNotExist:
                    pass  # Raise some exception
            elif isinstance(field, models.DateTimeField):
                result_dict[field_name] = datetime.datetime.strptime(field_value, '%Y-%m-%dT%H:%M:%S.%f%z') if field_value else field_value #'%Y-%m-%dT%H:%M:%S.%fZ'
            elif isinstance(field, models.BooleanField):
                result_dict[field_name] = True if field_value == 'True' else False
            elif isinstance(field, models.UUIDField):
                result_dict[field_name] = uuid.UUID(field_value)
            else:
                result_dict[field_name] = field_value
        return result_dict
    

    def serialize_json_fields(self, instance):
        fields_json = {}
        for field in instance._meta.fields:
            if isinstance(field, models.ForeignKey):
                #for ForeignKey fields, store the primary key
                print("FIELD ATTNAME", field.attname)
                fields_json[field.name] = str(getattr(instance, field.attname))
                print("FOREIGN_KEY", str(getattr(instance, field.attname)))
            elif isinstance(field, models.ManyToManyField):
                #for ManyToMany fields, store the primary keys of related instances
                fields_json[field.name] = [related_instance.pk for related_instance in getattr(instance, field.name).all()]
            elif isinstance(field, models.DateTimeField):
                # For DateTime fields, store the datetime in ISO 8601 format
                fields_json[field.name] = getattr(instance, field.name).isoformat() if getattr(instance, field.name) else getattr(instance, field.name)
            else:
                fields_json[field.name] = str(getattr(instance, field.name))
        return fields_json
    
    @cached_property
    def object(self):
        #create an instance of the associated model using the fields stored in the version
        model_class = self.content_type.model_class()
        instance = model_class(**self.deserialize_json_fields())

        return instance
    
    @property
    def _model(self):
        return self._content_type.model_class()
    
    @property
    def _content_type(self):
        return ContentType.objects.db_manager(self._state.db).get_for_id(self.content_type_id)
    

    def delete(self, *args, **kwargs):
        #overwrite delete method and bulk_delete method so that versions cannot be accidentally deleted
        pass

class PostVersion(VersionedModelMixin):
    pass

class NoteVersion(VersionedModelMixin):
    pass


class Notes(GUIDModel):
    author = models.ForeignKey(
        'Usr', on_delete=models.CASCADE, blank=True, related_name="user_notes")
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


class Usr(GUIDModel):
    email = models.EmailField()
    username = models.CharField(max_length=45)
    date_of_birth = models.DateField(null=True)

    def __str__(self) -> str:
        return self.email


class NotesVersion(VersionedModelMixin):
    pass