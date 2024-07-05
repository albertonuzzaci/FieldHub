from django.urls import path
from .views import *



app_name = 'users'

urlpatterns = [
    path('register/', register, name='register'),
    path('utenteregister/', UtenteRegistrationView.as_view(), name='utente_registration'),
    path('propstrutturaregister/',PropStrutturaRegistrationView.as_view(), name='propstruttura_registration'),
    path('login/',login_request, name='login'),
    path('logout/',logout_request, name='logout'),
    path('profile/', view_profile, name='view_profile'),
    path('updateprofile/', update_profile, name='update_profile'),
    path('cambiapassword', cambia_password, name='cambia_password')
]