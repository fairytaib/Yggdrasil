from django.test import TestCase
from django.contrib.auth.models import User
from familytree.models import Person


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

    def test_language_field_accepts_multiple_choices(self):
        """Test that the language field accepts multiple selections."""
        self.person.language = ["en", "fr", "ar"]
        self.person.save()
        self.person.refresh_from_db()
        self.assertListEqual(self.person.language, ["en", "fr", "ar"])

    def test_featured_image_default(self):
        """Test that featured_image has the default value if none is given."""
        self.assertEqual(self.person.featured_image, "placeholder")

    def test_valid_birth_country(self):
        """Test that a valid birth_country code can be saved and retrieved."""
        self.person.birth_country = "TN"  # Tunisia
        self.person.save()
        self.person.refresh_from_db()
        self.assertEqual(self.person.birth_country, "TN")

    def test_default_bio(self):
        """Test that the bio field defaults correctly."""
        self.assertEqual(self.person.bio, "I am me!")
