from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


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
    main_person = models.OneToOneField(
        'Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='main_of_tree'
    )

    def __str__(self):
        return f"{self.owner.username} Family Tree"


class Person(models.Model):
    """ A person model """
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='persons'
    )
    featured_image = CloudinaryField('image', default='placeholder',
                                     blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def siblings(self):
        """Get all siblings of the person.
        Exclude the person itself from the list.
        """
        return Person.objects.filter(
            parents__in=self.parents.all()
            ).exclude(id=self.id).distinct()
