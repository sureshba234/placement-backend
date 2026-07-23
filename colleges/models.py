from django.db import models


class College(models.Model):
    name = models.CharField(max_length=255, unique=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Create your models here.
