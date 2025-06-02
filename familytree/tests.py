from django.test import TestCase
from familytree.forms import PersonForm
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from familytree.models import Person
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
