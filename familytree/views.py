from django.shortcuts import render, get_object_or_404
from .models import Person, FamilyTree
from django.contrib.auth.models import User
from .forms import PersonForm
from django.shortcuts import redirect
# Create your views here.


def get_owner(request):
    """Display the users own Data"""
    owner = Person.objects.filter(owner=request.user).first()
    return render(request, 'familytree/family-list.html',
                  {'owner': owner})


def get_family_members(request):
    """Display the users family members"""
    family_tree = get_object_or_404(FamilyTree, owner=request.user)
    family_members = Person.objects.filter(family_tree=family_tree)
    return render(request, 'familytree/family-list.html',
                  {'family_members': family_members})


def add_family_member(request):
    relation = request.GET.get('relation')  # parent, child, partner
    owner_person_id = request.GET.get('owner_id')
    owner_person = get_object_or_404(Person, id=owner_person_id)

    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            if relation == "partner" and owner_person.partner:
                form.add_error(None, "This person already has a partner.")
            elif relation == "parent" and owner_person == 2:
                form.add_error(
                    None,
                    "This person has already two parents reigstered.")
            else:
                person = form.save(commit=False)
                person.owner = request.user
                person.save()

                if relation == "parent":
                    owner_person.parents.add(person)
                elif relation == "child":
                    person.parents.add(owner_person)
                elif relation == "partner":
                    owner_person.partner = person
                    owner_person.save()

                    person.partner = owner_person
                    person.save()

                return redirect('get_owner')

    else:
        form = PersonForm()

    return render(request, 'familytree/add-family-member.html', {
        'form': form,
        'relation': relation,
        'owner_person': owner_person
    })
