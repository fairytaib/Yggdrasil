from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Person, FamilyTree


@receiver(post_save, sender=Person)
def checkFamilyTree(sender, instance, created, **kwargs):
    """
    Signal to create a FamilyTree when a user registers their first Person.
    """
    if created:
        user = instance.owner
        if user and not FamilyTree.objects.filter(owner=user).exists():
            FamilyTree.objects.create(owner=user)
