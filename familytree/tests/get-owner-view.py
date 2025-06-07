from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from familytree.models import Person, FamilyTree


class GetOwnerViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="nobody", password="test")
        self.client.login(username="nobody", password="test")

    def test_redirects_to_add_self_if_tree_does_not_exist(self):
        response = self.client.get(reverse("get_owner"))
        self.assertRedirects(response, reverse("add_self"))

    def test_redirects_to_family_view_if_main_person_exists(self):
        main = Person.objects.create(
            owner=self.user, first_name="A", last_name="B"
        )
        # FamilyTree wird durch das Signal automatisch erstellt!
        tree = FamilyTree.objects.get(owner=self.user)
        tree.main_person = main
        tree.save()
        tree.person.add(main)

        response = self.client.get(reverse("get_owner"))
        self.assertRedirects(response, reverse("family_view", args=[main.id]))
