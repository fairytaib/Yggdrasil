from django.test import TestCase
from django.contrib.auth.models import User
from familytree.models import FamilyTree


class FamilyTreeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="treeowner", password="pass")

    def test_str_representation(self):
        tree = FamilyTree.objects.create(owner=self.user)
        self.assertEqual(str(tree), "treeowner Family Tree")
