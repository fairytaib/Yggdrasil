from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from familytree.models import Person


class EntireTreeViewTest(TestCase):
    """Test suite for the entire view."""

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
        self.assertTemplateUsed(response, "familytree/entire_view.html")
        self.assertIn("pov", response.context)
        self.assertEqual(response.context["pov"], self.pov)
        self.assertContains(response, "Ismail")
