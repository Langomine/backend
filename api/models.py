import os

import uuid
from django.db import models
from uuid import uuid4

def generate_uuid4_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('voices', filename)

class Voice(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    duration_s = models.IntegerField(default=0)
    file = models.FileField(upload_to=generate_uuid4_filename, null=True)
    language = models.CharField(max_length=50, null=True)
    text = models.TextField(null=True)
    words = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(default=None, null=True)

class Question(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField()