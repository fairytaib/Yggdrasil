from django.shortcuts import render, get_object_or_404
from .models import Person, FamilyTree
from django.contrib import messages
from .forms import PersonForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def get_owner(request):
    """Redirect to the main person of the family tree."""
    try:
        family_tree = FamilyTree.objects.get(owner=request.user)
        if family_tree.main_person:
            return redirect("family_view",
                            person_id=family_tree.main_person.id)
    except FamilyTree.DoesNotExist:
        pass

    return redirect("add_self")


@login_required
def add_self(request):
    """Add the main person to the family tree."""
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.owner = request.user
            person.save()
            form.save_m2m()

            # Erzeuge FamilyTree und setze die Person als main_person
            family_tree, created = FamilyTree.objects.get_or_create(
                owner=request.user)
            family_tree.person.add(person)

            if family_tree.main_person is None:
                family_tree.main_person = person
                family_tree.save()

            return redirect("family_view", person_id=person.id)
    else:
        form = PersonForm()
    return render(request, "familytree/add_self.html", {"form": form})


@login_required
def add_family_member(request):
    """Add a family member to the family tree."""
    relation = request.GET.get('relation')
    person_id = request.GET.get('person_id')
    main_person = get_object_or_404(Person, id=person_id)

    if request.method == 'GET':
        if relation == "sibling" and not main_person.parents.exists():
            messages.info(
                request,
                """Please add at least one parent first,
                before you can add a sibling"""
            )
            return redirect(
                f"{reverse(
                    'add_family_member'
                    )}?relation=parent&person_id={main_person.id}"
            )

    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES)
        if form.is_valid():
            if relation == "partner" and main_person.partner:
                form.add_error(None, "This person already has a partner.")
            elif relation == "parent" and main_person.parents.count() >= 2:
                form.add_error(
                    None,
                    "This person has already two parents reigstered.")
            else:
                new_person = form.save(commit=False)
                new_person.owner = request.user
                new_person.save()
                form.save_m2m()

                family_tree, created = FamilyTree.objects.get_or_create(
                    owner=request.user)
                family_tree.person.add(new_person)

                if family_tree.main_person is None:
                    family_tree.main_person = new_person
                    family_tree.save()

                if relation == "parent":
                    main_person.parents.add(new_person)
                elif relation == "child":
                    new_person.parents.add(main_person)
                elif relation == "partner":
                    main_person.partner = new_person
                    main_person.save()
                    new_person.partner = main_person
                    new_person.save()
                elif relation == "sibling":
                    if not main_person.parents.exists():
                        messages.error(
                            request,
                            "Please tell us about your parents first."
                            )
                        return redirect(
                            f"{reverse(
                                'add_family_member'
                                )}?relation=parent&person_id={main_person.id}")
                    else:
                        for parent in main_person.parents.all():
                            new_person.parents.add(parent)

                return redirect('family_view', person_id=main_person.id)

            return redirect('family_view', person_id=new_person.id)
    else:
        form = PersonForm()

    return render(request, 'familytree/add_family_member.html', {
                            'form': form,
                            'relation': relation,
                            'main_person': main_person,
                        })


@login_required
def get_family_members(request):
    """Display the users family members"""
    family_tree = get_object_or_404(FamilyTree, owner=request.user,
                                    main_person=request.user)
    family_members = Person.objects.filter(family_tree=family_tree)
    return render(request, 'familytree/family_view.html',
                  {'family_members': family_members})


@login_required
def edit_person(request, pov_id, person_id):
    """Edit a person in the family tree."""
    person = get_object_or_404(Person, id=person_id, owner=request.user)

    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, "Person updated successfully!")
            return redirect('family_view', person_id=pov_id)
    else:
        form = PersonForm(instance=person)

    return render(request, 'familytree/edit_person.html', {
        'form': form,
        'person': person,
        'pov_id': pov_id
    })


@login_required
def delete_person(request, pov_id, person_id):
    """Delete a person from the family tree."""
    person = get_object_or_404(Person, id=person_id, owner=request.user)

    is_deleting_pov = (person.id == pov_id)

    if request.method == "POST":
        if is_deleting_pov:
            person.delete()
            messages.success(request, "POV was deleted – returning to main view.")
            return redirect('get_owner')  # nicht mehr zu gelöschtem POV weiterleiten

        person.delete()
        messages.success(request, "Person was successfully deleted.")
        return redirect('family_view', person_id=pov_id)

    return render(request, 'familytree/delete_person.html', {
        'person': person,
        'pov_id': pov_id
    })


@login_required
def view_family(request, person_id):
    """Display the family tree of a person."""
    person = get_object_or_404(Person, id=person_id, owner=request.user)
    family_tree = get_object_or_404(FamilyTree, owner=request.user)

    context = {
        "person": person,
        "family_tree": family_tree,
        "persons": [],
    }

    context["persons"].append(person.partner)
    context["persons"].extend(person.parents.all())
    context["persons"].extend(person.children.all())
    context["persons"].extend(person.siblings())

    return render(request, "familytree/family_view.html", context)


@login_required
def view_details(request, person_id):
    """Display the details of a person."""
    person = get_object_or_404(Person, id=person_id, owner=request.user)

    context = {
        "person": person,
    }

    return render(request, "familytree/view_details.html", context)
