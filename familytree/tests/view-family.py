from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from familytree.models import Person, FamilyTree


class ViewFamilyTest(TestCase):
    """Test suite for the view_family view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.login(username="user", password="pass")

        # Setup main person (Signal legt FamilyTree automatisch an)
        self.pov = Person.objects.create(
            owner=self.user, first_name="Amina", last_name="Core"
        )

        # FamilyTree wird durch Signal erstellt, also hier nur referenzieren:
        self.tree = FamilyTree.objects.get(owner=self.user)
        self.tree.person.add(self.pov)

    def get_url(self):
        return reverse("family_view", args=[self.pov.id])

    def test_redirect_if_not_logged_in(self):
        """Users who are not logged in should be redirected."""
        self.client.logout()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_404_if_user_does_not_own_person(self):
        """Users cannot view family for someone they don't own."""
        other_user = User.objects.create_user(
            username="other", password="pass")
        stranger = Person.objects.create(
            owner=other_user, first_name="Hassan", last_name="Stranger")
        url = reverse("family_view", args=[stranger.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_family_view_renders_correct_template(self):
        """Should render family_view.html with expected context."""
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "familytree/family_view.html")
        self.assertIn("person", response.context)
        self.assertIn("family_tree", response.context)
        self.assertIn("persons", response.context)

    def test_family_members_are_in_context(self):
        """Parents, children, siblings,
        partners should be in 'persons' list."""
        # Create relations
        parent = Person.objects.create(
            owner=self.user, first_name="Omar", last_name="Senior")
        child = Person.objects.create(
            owner=self.user, first_name="Salim", last_name="Junior")
        sibling = Person.objects.create(
            owner=self.user, first_name="Zahra", last_name="Core")
        partner = Person.objects.create(
            owner=self.user, first_name="Layla", last_name="Partner")

        # Add relations
        self.pov.parents.add(parent)
        child.parents.add(self.pov)
        self.pov.partners.add(partner)
        sibling.parents.add(parent)  # shared parent = sibling

        response = self.client.get(self.get_url())
        persons_list = response.context["persons"]

        self.assertIn(parent, persons_list)
        self.assertIn(child, persons_list)
        self.assertIn(sibling, persons_list)
        self.assertIn(partner, persons_list)
        self.assertNotIn(self.pov, persons_list)
        # POV should not be in own list
