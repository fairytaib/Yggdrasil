from django.shortcuts import render, get_object_or_404
from .models import Person, FamilyTree
from django.contrib import messages
from .forms import PersonForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def add_self(request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.owner = request.user
            person.save()
            return redirect("family_view", person_id=person.id)
    else:
        form = PersonForm()
    return render(request, "familytree/add-self.html", {"form": form})


def get_owner(request):
    """Display the user's current person in focus with view-switching (POV)"""
    owner = Person.objects.filter(owner=request.user).first()

    context = {
        "owner": owner,
    }
    return render(request, 'familytree/family-list.html', context)


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

    if request.method == 'GET':
        if relation == "sibling" and not owner_person.parents.exists():
            messages.info(
                request,
                """Please add at least one parent first,
                before you can add a sibling"""
            )
            return redirect(
                f"{reverse(
                    'add_family_member'
                    )}?relation=parent&owner_id={owner_person.id}"
            )

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
                elif relation == "sibling":
                    if not owner_person.parents.exists():
                        messages.error(
                            request,
                            "Please tell us about your parents first."
                            )
                        return redirect(
                            f"{reverse(
                                'add_family_member'
                                )}?relation=parent&owner_id={owner_person.id}")
                    else:
                        for parent in owner_person.parents.all():
                            person.parents.add(parent)

                return redirect('get_owner')

    else:
        form = PersonForm()

    return render(request, 'familytree/add-family-member.html', {
        'form': form,
        'relation': relation,
        'owner_person': owner_person
    })


def family_view(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    view_mode = request.GET.get("view")

    context = {
        "owner": person,
        "view_mode": view_mode,
    }

    if view_mode == "partner":
        context["partner"] = person.partner
        return render(request, "familytree/view-partner.html", context)
    elif view_mode == "parents":
        context["parents"] = person.parents.all()
        return render(request, "familytree/view-parents.html", context)
    elif view_mode == "children":
        context["children"] = person.children.all()
        return render(request, "familytree/view-children.html", context)
    elif view_mode == "siblings":
        parents = person.parents.all()
        siblings = Person.objects.filter(
            parents__in=parents
            ).exclude(id=person.id).distinct()
        context["siblings"] = siblings
        context["parents"] = parents
        return render(request, "familytree/view-siblings.html", context)

    # Fallback to descendants view
    return render(request, "familytree/family-list.html", context)
