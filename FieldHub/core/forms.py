from django import forms
from .models import Campo


class SelectWithClass(forms.Select):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        attrs['class'] = 'form-control'
        super().__init__(*args, **kwargs)

class CheckboxInputWithClass(forms.CheckboxInput):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        attrs['class'] = 'form-check-input'
        super().__init__(*args, **kwargs)

class CampoForm(forms.ModelForm):
    class Meta:
        model = Campo
        fields = ['tipo_sport', 'coperto', 'costo', 'servizi']
        widgets = {
            'tipo_sport': SelectWithClass,
            'coperto': CheckboxInputWithClass,
            'costo': forms.NumberInput(attrs={'class': 'form-control'}),
            'servizi': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }


