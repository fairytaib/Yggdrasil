from .models import FamilyTree


def pov_context(request):
    """
    Context processor to add the main person of the family tree to the context.
    """
    if request.user.is_authenticated:
        try:
            family_tree = FamilyTree.objects.get(owner=request.user)
            person = family_tree.main_person
        except FamilyTree.DoesNotExist:
            person = None
        return {'person': person}
    return {}
