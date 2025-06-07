from django.test import TestCase, Client
from django.urls import reverse
from .models import PersonOfHistory
from unittest.mock import patch
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from datetime import date

# ==== Modeltests ====


class PersonOfHistoryModelTest(TestCase):

    def setUp(self):
        self.person = PersonOfHistory.objects.create(
            name="Salah ad-Din Yusuf ibn Ayyub",
            nickname="Saladin",
            story="""Saladin was the first sultan of Egypt and Syria and the
            founder of the Ayyubid dynasty."""
        )

    def test_person_creation(self):
        """Test that a PersonOfHistory instance is correctly created."""
        self.assertEqual(self.person.name, "Salah ad-Din Yusuf ibn Ayyub")
        self.assertEqual(self.person.nickname, "Saladin")
        self.assertIn("Saladin", self.person.story)

    def test_str_representation(self):
        """Test the string representation returns the name."""
        self.assertEqual(str(self.person), "Salah ad-Din Yusuf ibn Ayyub")

    def test_blank_nickname(self):
        """Test that nickname can be blank."""
        person = PersonOfHistory.objects.create(
            name="Fatima al-Fihri",
            nickname="",
            story="""Founder
            of the world's oldest existing university in Fez, Morocco."""
        )
        self.assertEqual(person.nickname, "")

    def test_null_image_field(self):
        """Test that image field uses the default placeholder if unset."""
        person = PersonOfHistory.objects.create(
            name="Ibn Battuta",
            story="A Moroccan explorer known for his extensive travels.",
        )
        self.assertEqual(person.image, 'placeholder')

    def test_max_length_constraints(self):
        """Test that max_length constraints are enforced."""
        long_name = "A" * 101
        with self.assertRaises(ValidationError):
            person = PersonOfHistory(
                name=long_name,
                story="A test person with a too long name."
            )
            person.full_clean()  # triggers validation

        long_nickname = "B" * 101
        with self.assertRaises(ValidationError):
            person = PersonOfHistory(
                name="Valid Name",
                nickname=long_nickname,
                story="A test person with a too long nickname."
            )
            person.full_clean()

    def test_story_is_required(self):
        """Test that story is a required field."""
        person = PersonOfHistory(
            name="Name Only",
        )
        with self.assertRaises(ValidationError):
            person.full_clean()


# ==== Viewtests ====

class PersonOfTheDayViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('person_of_the_day')

    def test_view_with_no_persons(self):
        """If no persons exist, a suitable message is displayed."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No historical figures available today.")
        self.assertTemplateUsed(response,
                                'peopleOfHistory/people_of_history.html')
        self.assertIsNone(response.context['person_of_history'])

    def test_view_with_one_person(self):
        """If a person exists, this is displayed."""
        person = PersonOfHistory.objects.create(
            name="Salah ad-Din",
            nickname="Saladin",
            story="Ayyubid Sultan of Egypt and Syria"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Salah ad-Din")
        self.assertEqual(response.context['person_of_history'], person)

    def test_view_renders_correct_template(self):
        """The view uses the correct template."""
        PersonOfHistory.objects.create(
            name="Ibn Sina", nickname="Avicenna", story="Persian polymath"
        )
        response = self.client.get(self.url)
        self.assertTemplateUsed(response,
                                'peopleOfHistory/people_of_history.html')

    @patch('peopleOfHistory.views.date')
    def test_same_day_returns_same_person(self, mock_date):
        """The same person is always displayed for the same day."""
        # Fix today's date
        mock_date.today.return_value = date(2025, 6, 2)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        persons = [
            PersonOfHistory.objects.create(name=f"Person {i}", story="Story")
            for i in range(5)
        ]
        first_response = self.client.get(self.url)
        second_response = self.client.get(self.url)

        self.assertEqual(
            first_response.context['person_of_history'],
            second_response.context['person_of_history']
        )

    @patch('peopleOfHistory.views.date')
    def test_different_days_return_different_persons(self, mock_date):
        """A different person can be displayed on different days
        (if enough are available)."""
        persons = [
            PersonOfHistory.objects.create(name=f"Person {i}", story="Story")
            for i in range(10)
        ]

        mock_date.today.return_value = date(2025, 6, 2)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
        response_day1 = self.client.get(self.url)
        person_day1 = response_day1.context['person_of_history']

        mock_date.today.return_value = date(2025, 6, 3)
        response_day2 = self.client.get(self.url)
        person_day2 = response_day2.context['person_of_history']

        # Can be the same - but probability decreases with more people
        self.assertNotEqual(person_day1, None)
        self.assertNotEqual(person_day2, None)
        # If there are enough entries, you can even expect them to be different
        self.assertNotEqual(person_day1, person_day2)
