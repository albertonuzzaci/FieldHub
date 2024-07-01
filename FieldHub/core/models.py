from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, time
class Struttura(models.Model):
    nome_struttura = models.CharField(max_length=255)
    citta = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=255)
    num_civico =models.IntegerField()
    descrizione = models.TextField()
    email = models.CharField(max_length=150)
    verified = models.BooleanField(default=False)

    numTelefono = models.CharField(max_length=20)
   
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
    
    img = models.ImageField(upload_to='static/img/users_img/field_pic', default='img/default_img/no_image.jpg')
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
    struttura = models.ForeignKey(Struttura, on_delete=models.CASCADE)

    
    def __str__(self):
        return f'{self.utente} - {self.campo} - {self.data} {self.ora}'
    
    class Meta:
        verbose_name_plural = "prenotazioni"
        unique_together = ('campo', 'data', 'ora') 
        
    def save(self, *args, **kwargs):

        if len(str(self.ora)) > 5:
            raise ValueError("L'ora deve essere nel formato %H:%M ")

        ora, minuti = self.ora.split(':')
        
        if not self.utente.user.is_utente:
            raise ValueError("L'utente deve essere verificato come utente per scrivere una recensione.")
        if int(minuti) != 0:
            raise ValueError("L'ora deve essere un'ora intera con minuti pari a 0.")
        if int(ora) < 10 or int(ora) > 21:
            raise ValueError("L'ora deve essere tra le 10 e le 21 comprese.")
        super().save(*args, **kwargs)
        
        
class Recensione(models.Model):
    data_recensione = models.DateField()
    utente = models.ForeignKey('users.Utente', on_delete=models.CASCADE, related_name='recensioni')
    campo = models.ForeignKey('Campo', on_delete=models.CASCADE, related_name='recensioni')
    struttura = models.ForeignKey('Struttura', on_delete=models.CASCADE, related_name='recensioni')
    testo = models.TextField()
    voto = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    data_prenotazione = models.DateField()
    prenotazione = models.ForeignKey('Prenotazione', on_delete=models.CASCADE, related_name='recensioni')


    class Meta:
        unique_together = ('utente', 'campo')

    def save(self, *args, **kwargs):
        if not self.utente.user.is_utente:
            raise ValueError("L'utente deve essere verificato come utente per scrivere una recensione.")
        if self.data_recensione < self.data_prenotazione:
            raise ValueError("La data della recensione deve essere maggiore o uguale alla data della prenotazione.")
        if self.prenotazione.utente != self.utente:
            raise ValueError("Non puoi recensire per altre prenotazioni")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Recensione di {self.campo} - Voto: {self.voto}"
