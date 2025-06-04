from django.test import TestCase, Client
from familytree.forms import PersonForm
from familytree.forms import FamilyRelationForm
from familytree.models import FamilyRelation
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from familytree.models import Person, FamilyTree, FamilyRelation
from django.urls import reverse
from datetime import date, timedelta
import io


class PersonModelTest(TestCase):
    """Test suite for the Person model."""

    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username="testuser",
                                             password="testpass")

        # Create a basic person
        self.person = Person.objects.create(
            owner=self.user,
            first_name="Fatima",
            last_name="al-Fihri"
        )

    def test_person_creation(self):
        """Test that a Person object is created successfully."""
        self.assertEqual(self.person.first_name, "Fatima")
        self.assertEqual(self.person.last_name, "al-Fihri")
        self.assertEqual(self.person.owner.username, "testuser")

    def test_str_representation(self):
        """Test that __str__ returns the full name."""
        self.assertEqual(str(self.person), "Fatima al-Fihri")

    def test_optional_fields_can_be_blank(self):
        """Test that optional fields can be blank or null."""
        self.assertEqual(self.person.occupation, "")
        self.assertEqual(self.person.hobbies, "")
        self.assertEqual(self.person.nickname, "")
        self.assertIsNone(self.person.birth_date)
        self.assertIsNone(self.person.death_date)
        self.assertEqual(self.person.bio, "I am me!")

    def test_siblings_method(self):
        """Test the siblings() method returns correct people."""
        # Create two parents
        parent1 = Person.objects.create(owner=self.user,
                                        first_name="Ali", last_name="bin Zayd")
        parent2 = Person.objects.create(owner=self.user,
                                        first_name="Amina",
                                        last_name="bint Omar")

        # Link them as parents of self.person
        self.person.parents.add(parent1, parent2)

        # Create a sibling with the same parents
        sibling = Person.objects.create(owner=self.user,
                                        first_name="Zahra",
                                        last_name="al-Fihri")
        sibling.parents.add(parent1, parent2)

        # This one should not be counted as sibling
        stranger = Person.objects.create(owner=self.user,
                                         first_name="Random",
                                         last_name="Guy")

        # Test that only Zahra is returned as sibling
        siblings = self.person.siblings()
        self.assertIn(sibling, siblings)
        self.assertNotIn(stranger, siblings)
        self.assertNotIn(self.person, siblings)  # should not include self


class PersonFormTest(TestCase):
    """Test suite for the PersonForm."""

    def setUp(self):
        self.valid_data = {
            'first_name': 'Fatima',
            'last_name': 'al-Fihri',
            'birth_place': 'Fez',
            'birth_country': 'MA',
            'occupation': 'Educator',
            'hobbies': 'Reading',
            'nickname': 'The Founder',
            'bio': 'A visionary woman.',
            'birth_date': date(800, 1, 1),
            'death_date': date(880, 1, 1),
            'language': ['ar', 'fr'],
        }

    def test_form_valid_with_minimum_data(self):
        """Form should be valid with all required fields and valid data."""
        form = PersonForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_first_name_characters(self):
        """First name must only contain allowed characters."""
        data = self.valid_data.copy()
        data['first_name'] = 'Fatima123!'
        form = PersonForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_invalid_last_name_characters(self):
        """Last name must only contain allowed characters."""
        data = self.valid_data.copy()
        data['last_name'] = 'al-Fihri$%'
        form = PersonForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_trailing_whitespace_is_stripped(self):
        """Leading/trailing whitespace should be stripped from fields."""
        data = self.valid_data.copy()
        data['first_name'] = '   Fatima   '
        data['last_name'] = '  al-Fihri  '
        form = PersonForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['first_name'], 'Fatima')
        self.assertEqual(form.cleaned_data['last_name'], 'al-Fihri')

    def test_birth_date_in_future_is_invalid(self):
        """Birth date cannot be in the future."""
        data = self.valid_data.copy()
        data['birth_date'] = date.today() + timedelta(days=1)
        form = PersonForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)

    def test_death_date_before_birth_date(self):
        """Death date cannot be before birth date."""
        data = self.valid_data.copy()
        data['birth_date'] = date(900, 1, 1)
        data['death_date'] = date(800, 1, 1)
        form = PersonForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('death_date', form.errors)

    def test_death_date_in_future(self):
        """Death date cannot be in the future."""
        data = self.valid_data.copy()
        data['death_date'] = date.today() + timedelta(days=1)
        form = PersonForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('death_date', form.errors)

    def test_invalid_image_rejected(self):
        """Uploaded non-image files should be rejected."""
        fake_file = SimpleUploadedFile(
            name='test.txt',
            content=b'not an image',
            content_type='text/plain'
        )
        data = self.valid_data.copy()
        files = {'featured_image': fake_file}
        form = PersonForm(data=data, files=files)
        self.assertFalse(form.is_valid())
        self.assertIn('featured_image', form.errors)


class FamilyRelationFormTest(TestCase):
    """Test suite for FamilyRelationForm and its dynamic relation context."""

    def test_parent_context_shows_correct_choices(self):
        """Form initialized with 'parent' context
        should only allow parent relations."""
        form = FamilyRelationForm(relation_context='parent')
        expected_choices = [
            ('parent', 'Parent'),
            ('step-parent', 'Step Parent'),
            ('foster-parent', 'Foster Parent'),
        ]
        self.assertEqual(form.fields[
            'relation_type'].choices, expected_choices)

    def test_child_context_shows_correct_choices(self):
        """Form initialized with 'child' context should
        only allow child relations."""
        form = FamilyRelationForm(relation_context='child')
        expected_choices = [
            ('child', 'Child'),
            ('foster-child', 'Foster Child'),
        ]
        self.assertEqual(form.fields[
            'relation_type'].choices, expected_choices)

    def test_sibling_context_shows_correct_choices(self):
        """Form initialized with 'sibling'
        context should only allow sibling relations."""
        form = FamilyRelationForm(relation_context='sibling')
        expected_choices = [
            ('sibling', 'Sibling'),
            ('half-sibling', 'Half Sibling'),
            ('step-sibling', 'Step Sibling'),
        ]
        self.assertEqual(form.fields['relation_type'].choices,
                         expected_choices)

    def test_partner_context_shows_correct_choices(self):
        """Form initialized with 'partner' context should
        only allow partner relation."""
        form = FamilyRelationForm(relation_context='partner')
        expected_choices = [('partner', 'Romantic Partner'),
                            ('ex-partner', 'Ex Romantic Partner'),
                            ('deceased', 'Deceased Partner')]
        self.assertEqual(form.fields[
            'relation_type'].choices, expected_choices)

    def test_form_invalid_without_required_fields(self):
        """Form should not validate without required data."""
        form = FamilyRelationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('relation_type', form.errors)

    def test_form_valid_with_valid_choice(self):
        """Form should validate with a valid relation_type."""
        form = FamilyRelationForm(
            data={'relation_type': 'partner'},
            relation_context='partner'
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_wrong_choice_for_context(self):
        """Form should reject invalid choices not in the context."""
        form = FamilyRelationForm(
            data={'relation_type': 'child'},
            relation_context='partner'
        )
        self.assertFalse(form.is_valid())
        self.assertIn('relation_type', form.errors)


class AddSelfViewTest(TestCase):
    """Tests for the add_self view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester",
                                             password="testpass")
        self.url = reverse("add_self")

    def test_redirect_if_not_logged_in(self):
        """Unauthenticated users should be redirected to login."""
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_get_returns_form(self):
        """GET request should return a form."""
        self.client.login(username="tester", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")
        self.assertTemplateUsed(response, "familytree/add_self.html")

    def test_post_creates_person_and_family_tree(self):
        """Valid POST should create Person and FamilyTree and redirect."""
        self.client.login(username="tester", password="testpass")
        data = {
            "first_name": "Fatima",
            "last_name": "al-Fihri",
            "birth_place": "Fez",
            "birth_country": "MA",
        }
        response = self.client.post(self.url, data, follow=True)

        self.assertEqual(Person.objects.count(), 1)
        person = Person.objects.first()
        self.assertEqual(person.first_name, "Fatima")
        self.assertEqual(person.owner, self.user)

        self.assertEqual(FamilyTree.objects.count(), 1)
        tree = FamilyTree.objects.get(owner=self.user)
        self.assertIn(person, tree.person.all())
        self.assertEqual(tree.main_person, person)

        self.assertRedirects(response, reverse("family_view",
                                               args=[person.id]))

    def test_post_with_invalid_data_renders_form_again(self):
        """If form is invalid, the template
        should be re-rendered with errors."""
        self.client.login(username="tester", password="testpass")
        data = {
            "first_name": "",  # Required field missing
            "last_name": "al-Fihri"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "first_name",
                             "This field is required.")


class AddFamilyMemberViewTest(TestCase):
    """Test suite for the add_family_member view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester",
                                             password="testpass")
        self.client.login(username="tester", password="testpass")

        self.main_person = Person.objects.create(
            owner=self.user, first_name="Ali", last_name="Main"
        )

    def get_url(self, relation="parent"):
        return reverse(
            "add_family_member") + f"?relation={
                relation}&person_id={self.main_person.id}"

    def test_redirect_if_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)

    def test_get_redirects_to_add_parent_if_sibling_and_no_parents(self):
        """Should redirect to parent form if
        trying to add sibling with no parents."""
        response = self.client.get(self.get_url(relation="sibling"))
        self.assertRedirects(
            response,
            reverse("add_family_member") + f"?relation=parent&person_id={
                self.main_person.id}"
        )

    def test_get_renders_form_for_valid_relation(self):
        """Renders both forms for valid GET request."""
        # Add a parent to allow sibling creation
        parent = Person.objects.create(owner=self.user,
                                       first_name="Parent", last_name="One")
        self.main_person.parents.add(parent)

        response = self.client.get(self.get_url("sibling"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")
        self.assertTemplateUsed(response, "familytree/add_family_member.html")

    def test_post_creates_child_correctly(self):
        """POST with relation=child should link new person as child."""
        data = {
            "first_name": "Hassan",
            "last_name": "Junior",
            "relation_type": "child",
        }
        url = self.get_url("child")
        response = self.client.post(url, data, follow=True)

        self.assertEqual(Person.objects.count(), 2)
        new_person = Person.objects.get(first_name="Hassan")
        self.assertIn(self.main_person, new_person.parents.all())
        self.assertRedirects(response, reverse("family_view",
                                               args=[self.main_person.id]))

    def test_post_creates_partner_correctly(self):
        """POST with relation=partner should link both as partners."""
        data = {
            "first_name": "Layla",
            "last_name": "Partner",
            "relation_type": "partner",
        }
        url = self.get_url("partner")
        response = self.client.post(url, data, follow=True)

        self.assertEqual(Person.objects.count(), 2)
        new_person = Person.objects.get(first_name="Layla")
        self.assertIn(new_person, self.main_person.partners.all())
        self.assertRedirects(response, reverse("family_view",
                                               args=[self.main_person.id]))

    def test_post_with_save_and_add_redirects_back_to_form(self):
        """POST with 'save_and_add' should reload the add form."""
        data = {
            "first_name": "Zayd",
            "last_name": "Repeat",
            "relation_type": "child",
            "save_and_add": "1"
        }
        url = self.get_url("child")
        response = self.client.post(url, data)
        expected_redirect = reverse(
            "add_family_member") + f"?relation=child&person_id={
                self.main_person.id}"
        self.assertRedirects(response, expected_redirect)


class EditPersonViewTest(TestCase):
    """Test suite for the edit_person view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="editor",
                                             password="pass123")
        self.other_user = User.objects.create_user(username="stranger",
                                                   password="pass123")

        self.client.login(username="editor", password="pass123")

        self.person = Person.objects.create(
            owner=self.user, first_name="Fatima", last_name="al-Fihri"
        )
        self.url = reverse("edit_person",
                           args=[self.person.id, self.person.id])

    def test_redirect_if_not_logged_in(self):
        """Should redirect to login if user is not authenticated."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_get_renders_form_for_owner(self):
        """GET request should render edit form with initial data."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fatima")
        self.assertTemplateUsed(response, "familytree/edit_person.html")

    def test_post_updates_person_data(self):
        """POST with valid data should update the person and redirect."""
        updated_data = {
            "first_name": "Fatima",
            "last_name": "Bint Muhammad",
            "birth_place": "Fez",
            "birth_country": "MA",
        }
        response = self.client.post(self.url, updated_data, follow=True)

        self.person.refresh_from_db()
        self.assertEqual(self.person.last_name, "Bint Muhammad")
        self.assertRedirects(response, reverse("family_view",
                                               args=[self.person.id]))
        self.assertContains(response, "Person updated successfully!")

    def test_post_with_invalid_data_shows_errors(self):
        """POST with invalid data should not update and show errors."""
        invalid_data = {
            "first_name": "",  # required
            "last_name": "NoFirstName"
        }
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "first_name",
                             "This field is required.")

    def test_user_cannot_edit_another_users_person(self):
        """User should not be able to edit another user's person."""
        other_person = Person.objects.create(
            owner=self.other_user, first_name="Private", last_name="Person"
        )
        url = reverse("edit_person", args=[other_person.id, other_person.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class DeletePersonViewTest(TestCase):
    """Test suite for the delete_person view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="deleter", password="pass123")
        self.other_user = User.objects.create_user(
            username="hacker", password="pass123")

        self.client.login(username="deleter", password="pass123")

        self.main_person = Person.objects.create(
            owner=self.user, first_name="Main", last_name="Person"
        )
        self.related_person = Person.objects.create(
            owner=self.user, first_name="Related", last_name="Person"
        )

    def get_url(self, pov_id, person_id):
        return reverse("delete_person", args=[pov_id, person_id])

    def test_redirect_if_not_logged_in(self):
        """Non-authenticated users should be redirected to login."""
        self.client.logout()
        url = self.get_url(self.main_person.id, self.related_person.id)
        response = self.client.get(url)
        self.assertRedirects(response, f"/accounts/login/?next={url}")

    def test_get_renders_confirmation_page(self):
        """GET should show the delete confirmation page."""
        url = self.get_url(self.main_person.id, self.related_person.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure")

    def test_post_deletes_non_pov_person_and_redirects_to_family_view(self):
        """Should delete person and redirect back to family view."""
        url = self.get_url(self.main_person.id, self.related_person.id)
        response = self.client.post(url, follow=True)

        self.assertFalse(Person.objects.filter(
            id=self.related_person.id).exists())
        self.assertRedirects(response, reverse(
            "family_view", args=[self.main_person.id]))
        self.assertContains(response, "Person was successfully deleted.")

    def test_post_deletes_pov_and_redirects_to_get_owner(self):
        """If POV is deleted, redirect to get_owner view
        which redirects to add_self."""
        url = self.get_url(self.main_person.id, self.main_person.id)
        response = self.client.post(url, follow=True)

        self.assertFalse(Person.objects.filter(
            id=self.main_person.id).exists())
        self.assertTemplateUsed(response, "familytree/add_self.html")

    def test_user_cannot_delete_other_users_person(self):
        """A user must not be able to delete someone else's person."""
        other_person = Person.objects.create(
            owner=self.other_user, first_name="Private", last_name="Data"
        )
        url = self.get_url(self.main_person.id, other_person.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ViewFamilyTest(TestCase):
    """Test suite for the view_family view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.login(username="user", password="pass")

        # Setup main person
        self.pov = Person.objects.create(
            owner=self.user, first_name="Amina", last_name="Core")

        # Setup family tree
        self.tree = FamilyTree.objects.create(
            owner=self.user, main_person=self.pov)
        self.tree.person.add(self.pov)

    def get_url(self):
        return reverse("family_view", args=[self.pov.id])

    def test_redirect_if_not_logged_in(self):
        """Users who are not logged in should be redirected."""
        self.client.logout()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_404_if_user_does_not_own_person(self):
        """Users cannot view family for someone they don't own."""
        other_user = User.objects.create_user(
            username="other", password="pass")
        stranger = Person.objects.create(
            owner=other_user, first_name="Hassan", last_name="Stranger")
        url = reverse("family_view", args=[stranger.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_family_view_renders_correct_template(self):
        """Should render family_view.html with expected context."""
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "familytree/family_view.html")
        self.assertIn("person", response.context)
        self.assertIn("family_tree", response.context)
        self.assertIn("persons", response.context)

    def test_family_members_are_in_context(self):
        """Parents, children, siblings,
        partners should be in 'persons' list."""
        # Create relations
        parent = Person.objects.create(
            owner=self.user, first_name="Omar", last_name="Senior")
        child = Person.objects.create(
            owner=self.user, first_name="Salim", last_name="Junior")
        sibling = Person.objects.create(
            owner=self.user, first_name="Zahra", last_name="Core")
        partner = Person.objects.create(
            owner=self.user, first_name="Layla", last_name="Partner")

        # Add relations
        self.pov.parents.add(parent)
        child.parents.add(self.pov)
        self.pov.partners.add(partner)
        sibling.parents.add(parent)  # shared parent = sibling

        response = self.client.get(self.get_url())
        persons_list = response.context["persons"]

        self.assertIn(parent, persons_list)
        self.assertIn(child, persons_list)
        self.assertIn(sibling, persons_list)
        self.assertIn(partner, persons_list)
        self.assertNotIn(self.pov, persons_list)
        # POV should not be in own list


class ViewDetailsTest(TestCase):
    """Test suite for the view_details view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="viewer", password="pass")
        self.client.login(
            username="viewer", password="pass")

        self.pov = Person.objects.create(
            owner=self.user, first_name="Layla", last_name="POV")
        self.detail_person = Person.objects.create(
            owner=self.user, first_name="Fatima", last_name="Detail")

        self.url = reverse(
            "view_details", args=[self.pov.id, self.detail_person.id])

    def test_redirect_if_not_logged_in(self):
        """Should redirect anonymous users to login page."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_404_if_user_does_not_own_person(self):
        """Should raise 404 if trying to access another user's person."""
        other_user = User.objects.create_user(
            username="other", password="pass")
        stranger = Person.objects.create(
            owner=other_user, first_name="Unknown", last_name="Stranger")
        url = reverse("view_details", args=[self.pov.id, stranger.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_view_details_renders_correct_template_and_context(self):
        """Should render the detail view template with person and pov_id."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "familytree/view_details.html")
        self.assertEqual(response.context["person"], self.detail_person)
        self.assertEqual(response.context["pov_id"], self.pov.id)
        self.assertContains(response, "Fatima")


class ClassicTreeViewTest(TestCase):
    """Test suite for the classic_tree_view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="treeuser", password="pass")
        self.client.login(username="treeuser", password="pass")

        self.pov = Person.objects.create(
            owner=self.user, first_name="Ismail", last_name="Tree")
        self.url = reverse("classic_tree_view", args=[self.pov.id])

    def test_redirect_if_not_logged_in(self):
        """Unauthenticated users should be redirected to login page."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_404_if_user_does_not_own_person(self):
        """Should raise 404 if accessing someone else's person."""
        other_user = User.objects.create_user(
            username="intruder", password="pass")
        outsider = Person.objects.create(
            owner=other_user, first_name="Ali", last_name="Foreign")
        url = reverse("classic_tree_view", args=[outsider.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_classic_tree_template_rendered(self):
        """Should render the classic_tree template and pass correct context."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "familytree/classic_tree.html")
        self.assertIn("person", response.context)
        self.assertEqual(response.context["person"], self.pov)
        self.assertContains(response, "Ismail")
