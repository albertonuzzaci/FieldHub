from core.models import Campo, Servizio, Struttura
import json, os
from django.db import transaction
import random


def erase_db():
    print("Cancello il DB")
    Campo.objects.all().delete()
    Servizio.objects.all().delete()
    Struttura.objects.all().delete()

def init_db():
    
    #------POPOLAZIONE TABELLA STRUTTURE------
    json_strutture_path = os.path.join(os.path.dirname(__file__), 'initDBJson', 'strutture.json')
    
    with open(json_strutture_path, 'r') as file:
        strutture_data = json.load(file)
    
    with transaction.atomic():
        for item in strutture_data:
            struttura, _ = Struttura.objects.get_or_create(
                nome_struttura=item['nome_struttura'],
                indirizzo=item['indirizzo'],
                num_civico=item['num_civico'],
                descrizione=item['descrizione'],
                email=item['email'],
                numTelefono=item['numTelefono'],
                citta=item['citta']
            )
        
    #------POPOLAZIONE TABELLA CAMPI------
    json_campi_path = os.path.join(os.path.dirname(__file__), 'initDBJson', 'campi.json')
    
    with open(json_campi_path, 'r') as file:
        data = json.load(file)
    
    with transaction.atomic(): # assicura che tutte le operazioni del db siano eseguite singolarmente
        for item in data:
            servizi = item.pop('servizi')
            servizi = [nome.strip() for nome in servizi.split(',')]
            campo, _ = Campo.objects.update_or_create(
                tipo_sport=item['tipo_sport'],
                coperto=item['coperto'],
                costo=item['costo'],
                struttura=random.choice(list(Struttura.objects.all()))
            )

            for nome_servizio in servizi:
                servizio, _ = Servizio.objects.get_or_create(
                    nome=nome_servizio.lower()
                )
                campo.servizi.add(servizio)
    

    print("DUMP DB")
    for campo in Campo.objects.all():
        print(campo, campo.servizi.all())
    
    for struttura in Struttura.objects.all():
        print(struttura)
        
        
    