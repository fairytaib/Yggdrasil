from django.shortcuts import render, get_object_or_404
from .models import Person, FamilyTree
from django.contrib.auth.models import User
# Create your views here.


def family_list(request):
    families = Person.objects.all()
    return render(request, 'familytree/family-list.html',
                  {'families': families})
