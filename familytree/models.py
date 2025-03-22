from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class FamilyTree(models.Model):
    """ A family tree model """

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='familytrees'
        )
    person = models.ManyToManyField(
        'Person',
        related_name='persons'
        )

    def __str__(self):
        return f"{self.owner.username} Family Tree"


class Person(models.Model):
    """ A person model """
    name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    bio = models.TextField(default="I am me!", blank=True)

    parents = models.ManyToManyField(
        'self', related_name='children',
        symmetrical=False, blank=True
        )

    partner = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        related_name='partners', blank=True, null=True
        )
