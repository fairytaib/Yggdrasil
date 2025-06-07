from datetime import timedelta
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from familytree.forms import PersonForm
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from familytree.models import Person


class PersonFormEdgeCaseTests(TestCase):
    """Edge-case tests for validation logic in PersonForm."""

    def setUp(self):
        self.valid_data = {
            'first_name': 'Zaynab',
            'last_name': 'Rahman',
            'birth_place': 'Cairo',
            'birth_country': 'Egypt',
            'birth_date': '2000-01-01',
        }

    def test_clean_death_date_future_fails(self):
        """
        Should raise a validation error if death_date is in the future.
        """
        data = self.valid_data.copy()
        future = timezone.now().date() + timedelta(days=10)
        data['death_date'] = future
        data['birth_date'] = '1990-01-01'
        form = PersonForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Death date cannot be in the future.", form.errors['death_date'])

    def test_clean_death_date_before_birth_fails(self):
        """
        Should raise a validation error if death_date is before birth_date.
        """
        data = self.valid_data.copy()
        data['birth_date'] = '2000-01-01'
        data['death_date'] = '1990-01-01'
        form = PersonForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Death date cannot be before birth date.", form.errors[
                'death_date'])

    def test_clean_featured_image_invalid_format(self):
        """
        Should raise a validation error if uploaded file is not a valid image.
        """
        bad_image = SimpleUploadedFile(
            "test.txt", b"invalid image content", content_type="text/plain")
        data = self.valid_data.copy()
        form = PersonForm(data=data, files={'featured_image': bad_image})
        form.is_valid()
        self.assertIn(
            "Uploaded file is not a valid image.", form.errors.get(
                'featured_image', []))

    def test_clean_featured_image_none_returns_none(self):
        """If no image is uploaded, should return None without error."""
        data = {
            "first_name": "Fatima",
            "last_name": "al-Fihri",
            "gender": "female"
        }
        form = PersonForm(data=data)  # no image provided
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data.get('featured_image'))

    def test_clean_featured_image_valid_jpg(self):
        """A valid JPG image should be accepted."""
        from PIL import Image
        import tempfile

        image = Image.new('RGB', (100, 100))
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)

        uploaded = SimpleUploadedFile(
            name='test.jpg',
            content=temp_file.read(),
            content_type='image/jpeg'
        )

        data = {
            "first_name": "Fatima",
            "last_name": "al-Fihri",
            "gender": "female"
        }

        form = PersonForm(data=data, files={'featured_image': uploaded})
        self.assertTrue(form.is_valid())
        self.assertIn('featured_image', form.cleaned_data)

    def test_clean_featured_image_unsupported_format(self):
        """Unsupported image formats (e.g. BMP)
        should raise ValidationError."""
        from PIL import Image
        import tempfile

        image = Image.new('RGB', (100, 100))
        temp_file = tempfile.NamedTemporaryFile(suffix='.bmp')
        image.save(temp_file, format='BMP')
        temp_file.seek(0)

        uploaded = SimpleUploadedFile(
            name='test.bmp',
            content=temp_file.read(),
            content_type='image/bmp'
        )

        data = self.valid_data.copy()
        form = PersonForm(data=data, files={'featured_image': uploaded})
        self.assertFalse(form.is_valid())
        self.assertIn("Only jpeg, png, gif, jpg, webp images are allowed.",
                      form.errors.get('featured_image', []))

        def test_clean_birth_place_invalid_characters(self):
            """
            Should raise a validation error
            if birth_place contains invalid characters.
            """
            data = self.valid_data.copy()
            data['birth_place'] = "123!@#"
            form = PersonForm(data=data)
            form.is_valid()
            error_msg = form.errors['birth_place'][0]
            self.assertIn("Birth place may only contain", error_msg)
            self.assertIn("letters", error_msg)
            self.assertIn("apostrophes", error_msg)


class ClassicTreeViewEdgeTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user", password="test")
        self.client.login(username="user", password="test")

    def test_grandparents_and_partner_parents_are_included(self):
        # Grandparents
        grandfather = Person.objects.create(
            owner=self.user, first_name="Grand", last_name="Father")
        father = Person.objects.create(
            owner=self.user, first_name="Father", last_name="Dad")
        father.parents.add(grandfather)

        # POV
        pov = Person.objects.create(
            owner=self.user, first_name="POV", last_name="Main")
        pov.parents.add(father)

        # Partner with Parents
        partner_parent = Person.objects.create(
            owner=self.user, first_name="PartnerDad", last_name="X")
        partner = Person.objects.create(
            owner=self.user, first_name="Partner", last_name="Y")
        partner.parents.add(partner_parent)
        pov.partners.add(partner)

        url = reverse("classic_tree_view", args=[pov.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("grandparents", response.context)
        self.assertIn(grandfather, response.context["grandparents"])
        self.assertIn(partner_parent, response.context["partner_parents"])
