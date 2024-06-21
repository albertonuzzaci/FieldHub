from django.urls import path
from .views import *


app_name = 'core'

urlpatterns = [
    path("listacampi/",ListaCampiView.as_view(), name="listacampi"),
    path("creacampo/", create_campo, name="creacampo"),
    path("campo/<int:pk>/", DetailCampoView.as_view(), name="visualizza_campo"),
    path("prenota/<int:pk>/", prenota_campo, name="prenota_campo"),
    path('cercacampo/', CercaCampoListView.as_view(), name="cerca_campo")
]
