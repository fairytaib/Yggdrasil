from django.test import TestCase, Client
from familytree.forms import PersonForm
from familytree.forms import FamilyRelationForm
from familytree.models import FamilyRelation
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from familytree.models import Person, FamilyTree
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
        expected_choices = [('partner', 'Romantic Partner')]
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
