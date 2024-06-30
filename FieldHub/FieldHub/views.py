from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import logout
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
    
    if user.is_staff:
        logout(request)
        url = reverse('core:cerca_campo')
        
    return redirect(url)
    

def permission_denied_view(request, exception):
    return render(request, '403.html', status=403)

def resource_not_found_view(request):
    return render(request, '404.html', status=404)