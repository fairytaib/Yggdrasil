from django.test import TestCase
from django.contrib.auth.models import User
from familytree.models import Person
from familytree.templatetags.tree_tags import show_family_tree


class ShowFamilyTreeTagTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester", password="pass")

    def test_none_person_returns_empty_ul(self):
        """Passing None should return empty <ul></ul>"""
        html = show_family_tree(None)
        self.assertIn("<ul></ul>", html)

    def test_single_person_no_children(self):
        """A person without children should render their name only"""
        person = Person.objects.create(
            owner=self.user, first_name="Fatima", last_name="al-Fihri")
        html = show_family_tree(person)
        self.assertIn("Fatima al-Fihri", html)
        self.assertIn("<ul>", html)
        self.assertIn("</ul>", html)

    def test_person_with_children(self):
        """Recursive rendering should include children as nested <li>"""
        parent = Person.objects.create(
            owner=self.user, first_name="Ali", last_name="Parent")
        child1 = Person.objects.create(
            owner=self.user, first_name="Zayd", last_name="Child")
        child2 = Person.objects.create(
            owner=self.user, first_name="Layla", last_name="Child")
        child1.parents.add(parent)
        child2.parents.add(parent)

        html = show_family_tree(parent)

        # Root person
        self.assertIn("Ali Parent", html)
        # Children
        self.assertIn("Zayd Child", html)
        self.assertIn("Layla Child", html)
        # Nested structure
        self.assertIn("<ul>", html)
        self.assertIn("</ul>", html)
