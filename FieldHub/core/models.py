from django.db import models
from django.core.validators import RegexValidator

class Struttura(models.Model):
    nome_struttura = models.CharField(max_length=255)
    citta = models.CharField(max_length=255)
    indirizzo = models.CharField(max_length=255)
    num_civico =models.IntegerField()
    descrizione = models.TextField()
    email = models.CharField(max_length=150)
    numTelefono = models.CharField(max_length=20, validators=[
        RegexValidator(
            regex =  r'^(?:\+39)?\d{11}$',            
            message="Il numero di telefono deve essere nel formato corretto."
        )
    ])
   
    def __str__(self):
        return self.nome_struttura

    class Meta:
        verbose_name_plural = "strutture"
        
class Servizio(models.Model):
    SERVIZIO_CHOICES = [
        ('docce', 'Docce'),
        ('piscina', 'Piscina'),
        ('spogliatoi', 'Spogliatoi'),
        ('armadietti', 'Armadietti'),
        ('illuminazione','Illuminazione notturna'),
        ('bar','Bar'),
        ('parcheggio','Parcheggio gratuito'),
        ('noleggiorachette','Noleggio racchette'),
        ('casacche','Casacche in prestito')
    ]

    nome = models.CharField(max_length=50, choices=SERVIZIO_CHOICES, unique=True)

    def __str__(self):
        return self.get_nome_display()
    
class Campo(models.Model):
    TIPO_SPORT_CHOICES = [
        ('tennis', 'Tennis'),
        ('calcio5', 'Calcio a 5'),
        ('calcio7', 'Calcio a 7'),
        ('padel', 'Padel'),
        ('beachvolley', 'Beach Volley'),
        ('pallavolo', 'Pallavolo')
    ]
    
    tipo_sport = models.CharField(max_length=50, choices=TIPO_SPORT_CHOICES)
    coperto = models.BooleanField(default=False)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    servizi = models.ManyToManyField(Servizio)
    struttura = models.ForeignKey(Struttura, on_delete=models.CASCADE)
    
    def __str__(self):
        servizi_list = ', '.join([servizio.nome for servizio in self.servizi.all()])
        copertura = "Coperto" if self.coperto else "Scoperto"
        return f'{self.tipo_sport} - {copertura} - {self.costo}€ - Servizi: {servizi_list}'
    
    class Meta:
        verbose_name_plural = "campi"

class Prenotazione(models.Model):
    utente = models.ForeignKey('users.Utente', on_delete=models.CASCADE)
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE)
    data = models.DateField()
    ora = models.TimeField()

    def __str__(self):
        return f'{self.utente.username} - {self.campo} - {self.data} {self.ora}'
    
    class Meta:
        verbose_name_plural = "prenotazioni"
        unique_together = ('campo', 'data', 'ora') 