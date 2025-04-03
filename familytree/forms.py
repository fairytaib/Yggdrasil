from .models import Person
from django import forms


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = (
            'first_name', 'last_name',
            'birth_date', 'death_date',
            'bio')
