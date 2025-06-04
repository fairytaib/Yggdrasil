from .models import FamilyTree


def pov_context(request):
    """
    Context processor to add the main person of the family tree to the context.
    """
    if request.user.is_authenticated:
        user = request.user
        family_tree = FamilyTree.objects.filter(owner=user).first()
        person = family_tree.main_person if family_tree else None
        return {'person': person}
    return {}
