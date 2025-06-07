from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from familytree.models import Person


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
