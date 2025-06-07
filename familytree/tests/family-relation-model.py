from django.test import TestCase
from django.contrib.auth.models import User
from familytree.models import Person, FamilyRelation


class FamilyRelationModelTest(TestCase):
    """Test suite for the FamilyRelation model."""

    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.person1 = Person.objects.create(
            owner=self.user, first_name="Ali", last_name="A")
        self.person2 = Person.objects.create(
            owner=self.user, first_name="Zaynab", last_name="B")

    def test_str_representation(self):
        """Test the __str__ method of FamilyRelation."""
        relation = FamilyRelation.objects.create(
            from_person=self.person1,
            to_person=self.person2,
            relation_type="partner"
        )
        expected = "Ali A → partner → Zaynab B"
        self.assertEqual(str(relation), expected)
