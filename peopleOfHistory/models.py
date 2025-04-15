from django.db import models
from cloudinary.models import CloudinaryField


class PersonOfHistory(models.Model):
    """A person of history model"""
    name = models.CharField(max_length=100)
    image = CloudinaryField(
        'image', default='placeholder',
        blank=True, null=True)
    nickname = models.CharField(max_length=100, blank=True)
    story = models.TextField()

    def __str__(self):
        return self.name
