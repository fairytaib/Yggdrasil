from .models import FamilyTree


def pov_context(request):
    if request.user.is_authenticated:
        try:
            family_tree = FamilyTree.objects.get(owner=request.user)
            # Falls es keine main_person gibt, wird person=None gesetzt
            person = family_tree.main_person
        except FamilyTree.DoesNotExist:
            person = None
        return {'person': person}
    return {}
