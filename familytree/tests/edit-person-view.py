from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from familytree.models import Person


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
