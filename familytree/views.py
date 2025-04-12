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
            elif relation == "parent" and main_person == 2:
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
def edit_person(request, person_id):
    person = get_object_or_404(Person, id=person_id, owner=request.user)

    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, "Person updated successfully!")

            # Redirect zur POV des Users, nicht zur bearbeiteten Person
            pov = Person.objects.filter(owner=request.user).first()
            if pov:
                return redirect('family_view', person_id=pov.id)
            else:
                return redirect('add_self')
    else:
        form = PersonForm(instance=person)

    return render(request,
                  'familytree/edit_person.html',
                  {'form': form, 'person': person})


@login_required
def delete_person(request, person_id):
    person = get_object_or_404(Person, id=person_id, owner=request.user)
    owner_person = Person.objects.filter(owner=request.user).first()

    if person.id == owner_person.id:
        messages.error(request, "Du kannst dich selbst nicht löschen.")
        return redirect('get_owner')

    if request.method == "POST":
        person.delete()
        messages.success(request, "Person was successfully deleted.")
        return redirect('get_owner')

    return render(request, 'familytree/delete_person.html', {'person': person})


@login_required
def view_family(request, person_id):
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
