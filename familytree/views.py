from django.shortcuts import render, get_object_or_404
from .models import Person, FamilyTree
from django.contrib.auth.models import User
# Create your views here.


def get_owner(request):
    owner = Person.objects.filter(owner=request.user).first()
    return render(request, 'familytree/family-list.html',
                  {'owner': owner})
