from django.urls import path
from .views import *

app_name = 'core'

urlpatterns = [
    path("listacampi/",ListaCampiView.as_view(), name="listacampi"),
    path('prenotazioni/utente/', PrenotazioniUtenteView.as_view(), name='prenotazioni_utente'),
    path('prenotazioni/struttura/', PrenotazioniStrutturaView.as_view(), name='prenotazioni_struttura'),    
    path("campo/<int:pk>/", DetailCampoView.as_view(), name="visualizza_campo"),
    path("struttura/<int:pk>/", DetailStrutturaView.as_view(), name="visualizza_struttura"),
    path('cercacampo/', CercaCampoListView.as_view(), name="cerca_campo"),
    path('prenotazioneconfermata/', PrenotazioneConfermataView.as_view(), name='prenotazione_confermata'),
    path('gestiscicampi/', ListaCampiPerStrutturaView.as_view(), name="gestisci_campi"),

    path('recensione/<int:prenotazione_id>', salva_recensione, name="salva_recensione"),
    
    path("creacampo/", create_campo, name="crea_campo"),
    path("eliminacampo/<int:pk>/", elimina_campo, name="elimina_campo"),
    path("home/", home_page, name="homepage"),
    path('ore_libere/<int:campo_id>/<str:data>/', ore_libere, name='ore_libere'),
    path("eliminaprenotazione/<int:pk>/", elimina_prenotazione, name="elimina_prenotazione")
]
