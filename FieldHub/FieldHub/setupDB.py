from core.models import Campo, Servizio, Struttura, Prenotazione, Recensione
import json, os
from django.db import transaction, IntegrityError
import random
from users.models import ProprietarioStruttura, User, Utente
from datetime import datetime, timedelta
from django.utils import timezone
from FieldHub.settings import STATIC_URL

def erase_db():
    print("Cancello il DB")
    Campo.objects.all().delete()
    Servizio.objects.all().delete()
    Struttura.objects.all().delete()
    User.objects.all().delete()
    Prenotazione.objects.all().delete()
    Recensione.objects.all().delete()
        

def init_db():
    
    #------POPOLAZIONE TABELLA STRUTTURE------
    json_strutture_path = os.path.join(os.path.dirname(__file__), 'initDBJson', 'strutture.json')
    
    with open(json_strutture_path, 'r') as file:
        strutture_utenti_data = json.load(file)
    
    with transaction.atomic():
        for item in strutture_utenti_data:
            tmpStruttura = item['struttura']
            tmpUtente = item['utente']
            
            #----creazione della struttura----
            struttura, _ = Struttura.objects.get_or_create(
                nome_struttura=tmpStruttura['nome_struttura'],
                indirizzo=tmpStruttura['indirizzo'],
                num_civico=tmpStruttura['num_civico'],
                descrizione=tmpStruttura['descrizione'],
                email=tmpStruttura['email'],
                numTelefono=tmpStruttura['numTelefono'],
                citta=tmpStruttura['citta']
            )
            struttura.save()
            
            #----creazione dell'utente a cui associare la struttura-----
            user, _ = User.objects.get_or_create(
                username=tmpUtente['username'],
                defaults={
                    'nome': tmpUtente['nome'],
                    'cognome': tmpUtente['cognome'],
                    'is_propStruttura': True,
                    'is_utente': False
                }
            )

            user.set_password(tmpUtente['password'])
            user.save()
            
            #----creazione dell'proprietario struttura vero e proprio-----
            proprietario_struttura, _ = ProprietarioStruttura.objects.get_or_create(
                user=user,
                defaults={'struttura': struttura}
            )

            proprietario_struttura.save()
    
        
    #------POPOLAZIONE TABELLA CAMPI------
    json_campi_path = os.path.join(os.path.dirname(__file__), 'initDBJson', 'campi.json')
    
    with open(json_campi_path, 'r') as file:
        data = json.load(file)    
    
    dict_img = {}

    for tipo_sport, _ in Campo.TIPO_SPORT_CHOICES:
        dict_img[tipo_sport] = {
            'coperto':[],
            'scoperto':[]
        }
    
    for nome_file in os.listdir('static/img/default_img'):
        if 'scoperto' in nome_file:
            tipo_copertura = 'scoperto'
        elif 'coperto' in nome_file:
            tipo_copertura = 'coperto'
        else:
            continue

        # Determina il tipo di sport
        print(Campo.TIPO_SPORT_CHOICES)
        for tipo_sport, _ in Campo.TIPO_SPORT_CHOICES:
            if tipo_sport in nome_file:
                dict_img[tipo_sport][tipo_copertura].append(nome_file)
                break
    
    print(dict_img)
    
    with transaction.atomic(): # assicura che tutte le operazioni del db siano eseguite singolarmente
        for item in data:
            servizi = item.pop('servizi')
            servizi = [nome.strip() for nome in servizi.split(',')]
            
            img = None
            try:
                if item['coperto']:
                    img = random.choice(dict_img[item['tipo_sport']]['coperto'])
                else:
                    img = random.choice(dict_img[item['tipo_sport']]['scoperto'])
                img = f'static/img/default_img/{img}'
            except:
                pass
            
            if img is None:
                img = 'static/img/default_img/no_image.jpg'

            campo, _ = Campo.objects.update_or_create(
                tipo_sport=item['tipo_sport'],
                coperto=item['coperto'],
                costo=item['costo'],
                struttura=random.choice(list(Struttura.objects.all())),
                img=img
            )
            

                
        

            for nome_servizio in servizi:
                servizio, _ = Servizio.objects.get_or_create(
                    nome=nome_servizio.lower()
                )
                campo.servizi.add(servizio)


    #----POPOLAZIONE UTENTI NORMALI ----
    json_utenti_path = os.path.join(os.path.dirname(__file__), 'initDBJson', 'utenti.json')
    with open(json_utenti_path, 'r') as file:
        data = json.load(file)
    
    with transaction.atomic():
        for item in data:
            # Creazione dell'utente
            user, created = User.objects.get_or_create(
                username=item['username'],
                defaults={
                    'nome': item['nome'],
                    'cognome': item['cognome'],
                    'is_propStruttura': False,
                    'is_utente': True
                }
            )

            # Impostazione della password
            user.set_password(item['password'])
            user.save()

            # Creazione dell'oggetto Utente associato
            utente, created = Utente.objects.get_or_create(
                user=user,
                defaults={
                    'email': item['email'],
                    'numTelefono': item['telefono']
                }
            )
    #-----POPOLAZIONE TABELLA PRENOTAZIONI-----
    oggi = timezone.localdate()
    giorni_successivi = 3
    giorni_precedenti = 3
    ore = [f'{hour}:00' for hour in range(10, 22)]

    utenti = Utente.objects.all()
    campi = Campo.objects.all()
    data_minima = oggi - timedelta(days=giorni_precedenti)
    data_massima = oggi + timedelta(days=giorni_successivi)
    
    for campo in campi:
        for _ in range(10):  # 10 prenotazioni future per ogni campo
            utente = random.choice(utenti)
            data = oggi + timedelta(days=random.randint(1, giorni_successivi))
            ora = random.choice(ore)
            
            created = False
            while not created:
                try:
                    Prenotazione.objects.create(
                        utente=utente,
                        campo=campo,
                        data=data,
                        ora=ora,
                        struttura=campo.struttura
                    )
                    created = True
                except IntegrityError:
                    data = oggi + timedelta(days=random.randint(1, giorni_successivi))
                    ora = random.choice(ore)

        for _ in range(20):  # 10 prenotazioni vecchie per ogni campo
            utente = random.choice(utenti)
            data = oggi - timedelta(days=random.randint(1, giorni_precedenti))
            ora = random.choice(ore)
            
            created = False
            while not created:
                try:
                    Prenotazione.objects.create(
                        utente=utente,
                        campo=campo,
                        data=data,
                        ora=ora,
                        struttura=campo.struttura
                    )
                    created = True
                except IntegrityError:
                    data = oggi - timedelta(days=random.randint(1, giorni_precedenti))
                    ora = random.choice(ore)
    
    
    json_recensioni_path = os.path.join(os.path.dirname(__file__), 'initDBJson', 'recensioni.json')
    with open(json_recensioni_path, 'r', encoding='UTF-8') as file:
        data = json.load(file)

    prenotazioni_vecche = Prenotazione.objects.filter(data__lt=oggi)

    for prenotazione in prenotazioni_vecche:
        recensione_random = random.choice(data)
        recensione = Recensione(
            data_recensione=oggi,
            utente=prenotazione.utente,
            campo=prenotazione.campo,
            struttura=prenotazione.struttura,
            testo=recensione_random['Testo'],
            voto=recensione_random['Voto'],
            data_prenotazione=prenotazione.data,
            prenotazione=prenotazione
        )
        try:
            recensione.save()
        except Exception as e:
            print(f'Errore creando recensione per la prenotazione {prenotazione}: {e}')
    

    print("DUMP DB")
    for campo in Campo.objects.all():
        print(campo, campo.servizi.all())
    

    for user in ProprietarioStruttura.objects.all():
        print(f'{user} associato a {user.struttura}')
    
    for user in Utente.objects.all():
        print(user)
        
    for prenotazione in Prenotazione.objects.all():
        print(prenotazione)

            
        
