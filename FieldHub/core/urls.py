from django.urls import path
from .views import *

app_name = 'core'

urlpatterns = [
    path("listacampi/",ListaCampiView.as_view(), name="listacampi"), #Accessibile da: Utenti, Anonymous OK
    path('prenotazioni/utente/', PrenotazioniUtenteView.as_view(), name='prenotazioni_utente'), #Accessibile da: Utenti OK
    path('prenotazioni/struttura/', PrenotazioniStrutturaView.as_view(), name='prenotazioni_struttura'), #Accessibile da: Strutture OK
    path("campo/<int:pk>/", DetailCampoView.as_view(), name="visualizza_campo"), #Accessibile da: Utenti OK
    path("struttura/<int:struttura_id>/", visualizza_struttura, name="visualizza_struttura"),
    path('cercacampo/', CercaCampoListView.as_view(), name="cerca_campo"), #Accessibile da: Utenti, Anonymous  OK
    path('prenotazioneconfermata/', PrenotazioneConfermataView.as_view(), name='prenotazione_confermata'), #Accessibile da: Utenti  OK
    path('gestiscicampi/', ListaCampiPerStrutturaView.as_view(), name="gestisci_campi"), #Accessibile da: Strutture  OK

    path('recensione/<int:prenotazione_id>', salva_recensione, name="salva_recensione"), #Accessibile da: Utenti (ulteriore protezione per logiche a livello di DB)  OK
    
    path("creacampo/", create_campo, name="crea_campo"),  #Accessibile da: Strutture  OK
    path("eliminacampo/<int:pk>/", elimina_campo, name="elimina_campo"),  #Accessibile da: Strutture OK
    path("home/", home_page, name="homepage"),
    path('ore_libere/<int:campo_id>/<str:data>/', ore_libere, name='ore_libere'), #Accessibile da: Utenti ok
    path("eliminaprenotazione/<int:pk>/", elimina_prenotazione, name="elimina_prenotazione"), #Accessibile da: Utenti, Strutture
    path('esporta_prenotazioni/', esporta_prenotazioni, name='esporta_prenotazioni'), 

]
