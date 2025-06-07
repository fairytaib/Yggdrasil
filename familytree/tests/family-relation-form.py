from django.test import TestCase
from familytree.forms import FamilyRelationForm


class FamilyRelationFormTest(TestCase):
    """Test suite for FamilyRelationForm and its dynamic relation context."""

    def test_parent_context_shows_correct_choices(self):
        """Form initialized with 'parent' context
        should only allow parent relations."""
        form = FamilyRelationForm(relation_context='parent')
        expected_choices = [
            ('parent', 'Parent'),
            ('step-parent', 'Step Parent'),
            ('foster-parent', 'Foster Parent'),
        ]
        self.assertEqual(form.fields[
            'relation_type'].choices, expected_choices)

    def test_child_context_shows_correct_choices(self):
        """Form initialized with 'child' context should
        only allow child relations."""
        form = FamilyRelationForm(relation_context='child')
        expected_choices = [
            ('child', 'Child'),
            ('foster-child', 'Foster Child'),
        ]
        self.assertEqual(form.fields[
            'relation_type'].choices, expected_choices)

    def test_sibling_context_shows_correct_choices(self):
        """Form initialized with 'sibling'
        context should only allow sibling relations."""
        form = FamilyRelationForm(relation_context='sibling')
        expected_choices = [
            ('sibling', 'Sibling'),
            ('half-sibling', 'Half Sibling'),
            ('step-sibling', 'Step Sibling'),
        ]
        self.assertEqual(form.fields['relation_type'].choices,
                         expected_choices)

    def test_partner_context_shows_correct_choices(self):
        """Form initialized with 'partner' context should
        only allow partner relation."""
        form = FamilyRelationForm(relation_context='partner')
        expected_choices = [('partner', 'Romantic Partner'),
                            ('ex-partner', 'Ex Romantic Partner'),
                            ('deceased', 'Deceased Partner')]
        self.assertEqual(form.fields[
            'relation_type'].choices, expected_choices)

    def test_form_invalid_without_required_fields(self):
        """Form should not validate without required data."""
        form = FamilyRelationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('relation_type', form.errors)

    def test_form_valid_with_valid_choice(self):
        """Form should validate with a valid relation_type."""
        form = FamilyRelationForm(
            data={'relation_type': 'partner'},
            relation_context='partner'
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_wrong_choice_for_context(self):
        """Form should reject invalid choices not in the context."""
        form = FamilyRelationForm(
            data={'relation_type': 'child'},
            relation_context='partner'
        )
        self.assertFalse(form.is_valid())
        self.assertIn('relation_type', form.errors)
