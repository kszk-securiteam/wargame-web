from django.db import models

# Create your models here.


class Challenge(models.Model):
    title = models.CharField(max_length=256)
    creation_dt = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=4096)
