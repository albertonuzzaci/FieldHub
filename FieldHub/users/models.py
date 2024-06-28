from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.core.validators import RegexValidator
from core.models import Struttura

class User(AbstractUser):
    
    # campi che aiutano a capire se un utente è una struttura o un utente
    is_propStruttura = models.BooleanField(default=False)
    is_utente = models.BooleanField(default=False)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    img = models.ImageField(upload_to='static/img/users_img/profile_pic', default='static/img/default_img/no_img_profile.jpg')
 

class Utente(models.Model):
    # quando User viene eliminato, viene eliminato anche Utente
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    email = models.CharField(max_length=100)
    numTelefono = models.CharField(max_length=13)
    '''
        , validators=[
        RegexValidator(
            regex =  r'^(?:\+39)?\d{11}$',            
            message="Il numero di telefono deve essere nel formato corretto."
        )
    ]
    '''
    

class ProprietarioStruttura(models.Model):
    # quando User viene eliminato, viene eliminato anche Utente
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    struttura = models.OneToOneField(Struttura, on_delete=models.CASCADE)
    