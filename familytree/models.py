from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.db.models import SET_NULL
import pycountry
from multiselectfield import MultiSelectField


COUNTRY_CHOICES = [
    (country.alpha_2, country.name) for country in pycountry.countries
    ]

LANGUAGE_CHOICES = [
    ('ar', 'Arabic'),
    ('bn', 'Bengali'),
    ('de', 'German'),
    ('el', 'Greek'),
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fa', 'Persian'),
    ('fr', 'French'),
    ('hi', 'Hindi'),
    ('id', 'Indonesian'),
    ('it', 'Italian'),
    ('ja', 'Japanese'),
    ('jv', 'Javanese'),
    ('ko', 'Korean'),
    ('ms', 'Malay'),
    ('nl', 'Dutch'),
    ('pl', 'Polish'),
    ('pt', 'Portuguese'),
    ('ro', 'Romanian'),
    ('ru', 'Russian'),
    ('sv', 'Swedish'),
    ('sw', 'Swahili'),
    ('ta', 'Tamil'),
    ('th', 'Thai'),
    ('tr', 'Turkish'),
    ('uk', 'Ukrainian'),
    ('ur', 'Urdu'),
    ('vi', 'Vietnamese'),
    ('zh', 'Chinese'),
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
    featured_image = CloudinaryField(
        'image', default='placeholder',
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
        choices=LANGUAGE_CHOICES,
        blank=True,
        null=True,
        max_choices=15,
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

    partners = models.ManyToManyField(
        'self',
        symmetrical=True,
        blank=True,
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


class FamilyRelation(models.Model):
    """ A family relation model.
    This model is used to create a relation between two persons """
    RELATIONSHIP_CHOICES = [
        ('parent', 'Parent'),
        ('step-parent', 'Step Parent'),
        ('foster-parent', 'Foster Parent'),
        ('child', 'Child'),
        ('step-child', 'Step Child'),
        ('foster-child', 'Foster Child'),
        ('sibling', 'Sibling'),
        ('half-sibling', 'Half Sibling'),
        ('step-sibling', 'Step Sibling'),
        ('partner', 'Romantic Partner'),
        ('ex-partner', 'Ex Romantic Partner'),
        ('deceased', 'Deceased Partner'),
    ]
    from_person = models.ForeignKey(
        'Person', related_name='relations_from',
        on_delete=models.CASCADE
    )
    to_person = models.ForeignKey(
        'Person', related_name='relations_to',
        on_delete=models.CASCADE
    )
    relation_type = models.CharField(
        max_length=50, choices=RELATIONSHIP_CHOICES
    )

    def __str__(self):
        return f"{
                self.from_person
                } → {self.relation_type} → {self.to_person}"

    class Meta:
        unique_together = ('from_person', 'to_person', 'relation_type')
