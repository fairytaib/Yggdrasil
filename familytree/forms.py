from .models import Person
from django import forms


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = (
            'featured_image', 'first_name',
            'last_name', 'birth_date',
            'death_date', 'bio')

        widgets = {
            'featured_image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['featured_image'].widget.attrs['class'] = 'form-control-file'
