from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import transaction
from .models import User,ProprietarioStruttura,Utente
from django.core.validators import RegexValidator
from core.models import Struttura
from django.contrib.auth.forms import PasswordChangeForm

class UtenteSignUpForm(UserCreationForm):
    nome = forms.CharField(required=True)
    cognome = forms.CharField(required=True)
    email  = forms.CharField(required=True)
    numTelefono = forms.CharField(label="Numero di Telefono", required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'nome', 'cognome', 'email', 'numTelefono', 'password1', 'password2']
        
    @transaction.atomic
    def save(self):
        #-----
        user = super().save(commit=False) 
        user.is_utente = True
        user.first_name = self.cleaned_data.get('nome')
        user.last_name = self.cleaned_data.get('cognome')
        user.save()
        #-----
        utente = Utente.objects.create(
            user=user,
            email=self.cleaned_data.get('email'),
            numTelefono=self.cleaned_data.get('numTelefono')
        )
        utente.save()
        return user

class ProprietarioStrutturaSignUpForm(UserCreationForm):
    nome = forms.CharField(required=True)
    cognome = forms.CharField(required=True)
    
    #----campi della struttura da registrare-----
    nome_struttura = forms.CharField(label="Nome della struttura", required=True)
    citta = forms.CharField(label="Città", required=True)
    indirizzo = forms.CharField(required=True)
    num_civico = forms.IntegerField(label="Numero Civico")
    descrizione = forms.CharField(required=True, 
                                  widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    email =forms.CharField(required=True)
    numTelefono = forms.CharField(label="Numero di Telefono", required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'nome', 'cognome', 'nome_struttura', 'citta', 'indirizzo', 'num_civico', 'descrizione', 'email', 'numTelefono', 'password1', 'password2']
    
    @transaction.atomic
    def save(self):
        #-----
        user = super().save(commit=False) 
        # prima di salvare user nel DB voglio prima salvare le informazioni sotto (nome, cognome, isprop) 
        user.is_propStruttura = True
        user.first_name = self.cleaned_data.get('nome')
        user.last_name = self.cleaned_data.get('cognome')
        user.save()
        #-----
        struttura = Struttura.objects.create(
            nome_struttura=self.cleaned_data.get('nome_struttura'),
            citta=self.cleaned_data.get('citta'),
            indirizzo=self.cleaned_data.get('indirizzo'),
            num_civico=self.cleaned_data.get('num_civico'),
            descrizione=self.cleaned_data.get('descrizione'),
            email=self.cleaned_data.get('email'),
            numTelefono=self.cleaned_data.get('numTelefono')
        )
        
        struttura.save()
        
        proprietarioStruttura = ProprietarioStruttura.objects.create(
            user=user,
            struttura=struttura
        )
        proprietarioStruttura.save()
        
        return user
    
class UpdateUserForm(forms.ModelForm):
    first_name = forms.CharField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    img = forms.ImageField(required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name','last_name','img']
    
class UpdateUtenteForm(forms.ModelForm):
    email = forms.CharField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    numTelefono = forms.CharField(
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Utente
        fields = ['email','numTelefono']

class UpdateStrutturaForm(forms.ModelForm):
    nome_struttura = forms.CharField(required=True,
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
    citta = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    indirizzo = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    num_civico = forms.IntegerField(required=True,
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}))
    descrizione = forms.CharField(required=True,
                                  widget=forms.Textarea(attrs={'class': 'form-control'}))
    email = forms.CharField(required=True,
                            widget=forms.EmailInput(attrs={'class': 'form-control'}))
    numTelefono = forms.CharField(required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Struttura
        fields = ['nome_struttura', 'citta', 'indirizzo', 'num_civico', 'descrizione', 'email', 'numTelefono']

class CambiaPasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Password attuale",
        widget=forms.PasswordInput(),
        required=True,
    )
    new_password1 = forms.CharField(
        label="Nuova password",
        widget=forms.PasswordInput(),
    )
    new_password2 = forms.CharField(
        label="Conferma password",
        widget=forms.PasswordInput(),
    )

    #I metodi clean nei form di Django vengono chiamati automaticamente durante la validazione del form. 
    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError("La password attuale non è corretta.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("Le nuove password non coincidono.")
        return cleaned_data