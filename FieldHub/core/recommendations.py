import heapq
from .models import  Campo, Recensione
from collections import defaultdict

def get_recommendations_for_campo(campo, num_recommended=3, considerJustSameType=False, user_id=None):
    # Ottieni tutte le recensioni per il campo specificato
    campo_recensioni = Recensione.objects.filter(campo_id=campo.id)
    # Crea un dizionario con utente_id come chiave e voto come valore
    recensioni_dict = {recensione.utente: recensione.voto for recensione in campo_recensioni}
    recommended_campi = defaultdict(list)
    # scorro tutti gli utenti e i voti che hanno dato al campo
    for utente, voto in recensioni_dict.items():
        # Scorro tutti i campi che ha recensito un utente
        # moltiplico il voto dato al campo in questione * il campo che ha recensito e lo salvo in un dizionario
        # campo: [voto, voto, voto] dove la lista dei voti sarà esclusivamente degli utenti che hanno recensito sia 
        # quel campo che il campo passato come parametro
        # Così facendo sarà più importante l'opinione di un utente a cui è piaciuto il campo che sto visualizzando. 
        recensioni_utente = Recensione.objects.filter(utente=utente).exclude(campo_id=campo.id)
        for recensione in recensioni_utente:
            if considerJustSameType:
              if recensione.campo.tipo_sport == campo.tipo_sport:
                
                recommended_campi[recensione.campo.id].append(recensione.voto*voto)
            else: 
              recommended_campi[recensione.campo.id].append(recensione.voto*voto)   
    
    medie_dict = {campo_id: sum(voti) / len(voti) for campo_id, voti in recommended_campi.items()}
    topCampi = heapq.nlargest(num_recommended, medie_dict.items(), key=lambda x: x[1])
    return [Campo.objects.get(id=id) for id, _ in topCampi]

