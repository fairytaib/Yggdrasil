from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from familytree.models import Person, FamilyTree


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
