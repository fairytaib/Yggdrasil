from django.test import TestCase, Client
from familytree.models import Person
from django.contrib.auth.models import User
from django.urls import reverse


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

    def test_post_creates_sibling_with_common_parents(self):
        parent = Person.objects.create(
            owner=self.user, first_name="Parent", last_name="One")
        self.main_person.parents.add(parent)

        data = {
            "first_name": "Zaynab",
            "last_name": "Sibling",
            "relation_type": "sibling",
        }
        url = self.get_url("sibling")
        response = self.client.post(url, data, follow=True)

        sibling = Person.objects.get(first_name="Zaynab")
        self.assertIn(parent, sibling.parents.all())
        self.assertRedirects(response, reverse(
            "family_view", args=[self.main_person.id]))

    def test_post_creates_parent_correctly(self):
        data = {
            "first_name": "Fatima",
            "last_name": "Elder",
            "relation_type": "parent",
        }
        url = self.get_url("parent")
        response = self.client.post(url, data, follow=True)

        self.assertEqual(Person.objects.count(), 2)
        new_parent = Person.objects.get(first_name="Fatima")
        self.assertIn(new_parent, self.main_person.parents.all())
        self.assertRedirects(
            response, reverse("family_view", args=[self.main_person.id]))
