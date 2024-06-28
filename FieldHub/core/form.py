from django import forms
from .models import Campo, Servizio
from django.db import transaction
from users.models import ProprietarioStruttura

class CreaCampoForm(forms.ModelForm):
    img = forms.ImageField(required=True, label="Immagine")
    tipo_sport = forms.ChoiceField(choices=Campo.TIPO_SPORT_CHOICES, required=True, label="Tipo di sport")
    coperto = forms.NullBooleanField(required=True, initial=False, widget=forms.Select(choices=[
        (True, 'Coperto'),
        (False, 'Scoperto'),
    ]))
    costo = forms.DecimalField(max_digits=10, decimal_places=2)
    servizi = forms.ModelMultipleChoiceField(
        queryset=Servizio.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Servizi"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  
        super(CreaCampoForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = Campo
        fields = ['img', 'tipo_sport', 'coperto', 'costo', 'servizi']
    
    @transaction.atomic
    def save(self):  
        struttura = list(ProprietarioStruttura.objects.filter(user=self.user))[0].struttura
        
        if self.cleaned_data['coperto'] is None:
            coperto = False  # Imposta False se il valore è None
        else:
            coperto = self.cleaned_data['coperto']
        campo = Campo.objects.create(tipo_sport=self.cleaned_data['tipo_sport'],
                                    coperto=coperto,
                                    costo=self.cleaned_data['costo'],
                                    struttura=struttura,
                                    img=self.cleaned_data['img']
                                    )

        
        for servizio in self.cleaned_data['servizi']:
            campo.servizi.add(servizio)
        campo.save()
        return campo

