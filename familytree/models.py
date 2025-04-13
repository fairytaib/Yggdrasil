from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.db.models import SET_NULL
import pycountry
from multiselectfield import MultiSelectField


COUNTRY_CHOICES = [
    (country.alpha_2, country.name) for country in pycountry.countries
    ]


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
    birth_place = models.CharField(max_length=100, blank=True)
    birth_country = models.CharField(
        max_length=2,
        choices=COUNTRY_CHOICES,
        blank=True,
        null=True,
        verbose_name="Country of Birth"
        )
    language = MultiSelectField(
        choices=COUNTRY_CHOICES,
        blank=True,
        null=True,
        max_choices=5,
        max_length=50,
        verbose_name="Languages spoken"
    )

    occupation = models.CharField(max_length=100, blank=True)
    hobbies = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=100, blank=True)

    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    bio = models.TextField(default="I am me!", blank=True)

    parents = models.ManyToManyField(
        'self', related_name='children',
        symmetrical=False, blank=True
        )

    partner = models.ForeignKey(
        'self', on_delete=SET_NULL,
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
