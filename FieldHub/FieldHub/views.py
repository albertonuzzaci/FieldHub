from django.shortcuts import redirect
from django.urls import reverse

def home_page(request):
    
    is_login = request.GET.get('login') == 'ok'
    is_logout = request.GET.get('logout') == 'ok'
    
    user = request.user
    if user.is_authenticated and user.is_propStruttura:
        url = reverse('core:gestisci_campi')
            
    if user.is_authenticated and user.is_utente:
        url = reverse('core:cerca_campo')
    
    if not user.is_authenticated:
        url = reverse('core:cerca_campo')
    
    if is_login:
        return redirect(f'{url}?login=ok')
    
    if is_logout:
        return redirect(f'{url}?logout=ok')
    
    return redirect(url)
    

