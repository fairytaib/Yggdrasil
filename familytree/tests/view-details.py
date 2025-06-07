from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from familytree.models import Person


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
