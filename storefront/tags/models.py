from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User

# Create your models here.
class TaggedItemManager(models.Manager):
    def get_tags_for(self, object_type, object_id):
        content_type = ContentType.objects.get_for_model(object_type)
        query_set = TaggedItem.objects.select_related('tag').filter(
            content_type=content_type,
            object_id=object_id
        )

        return query_set

class Tag(models.Model):
    label = models.CharField(max_length=255)
    
    def __str__(self):
        return self.label

# what tag applied to what object

class TaggedItem(models.Model):
    objects = TaggedItemManager()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)  # to connect to the Tag class to find the label
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) # use generic typr not specific type to connect all the models
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

class LikedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()