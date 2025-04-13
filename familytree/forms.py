from django import forms
from .models import Person


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = (
            'featured_image', 'first_name', 'last_name',
            'birth_place', 'birth_country', 'nationality',
            'language', 'occupation', 'hobbies', 'nickname',
            'birth_date', 'death_date', 'bio'
        )

        widgets = {
            'featured_image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'death_date': forms.DateInput(attrs={'type': 'date'}),
            'language': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'language':
                field.widget.attrs['class'] = 'form-control'
        self.fields['featured_image'].widget.attrs['class'] = 'form-control-file'
