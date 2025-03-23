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
        # Check if the user has a FamilyTree
        family_tree, created_tree = FamilyTree.objects.get_or_create(
            owner=user
            )
        family_tree.persons.add(instance)
