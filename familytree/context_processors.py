from .models import Person


def pov_context(request):
    if request.user.is_authenticated:
        person = Person.objects.filter(owner=request.user).first()
        return {'person': person}
    return {}
