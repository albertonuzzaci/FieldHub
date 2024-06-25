from django.shortcuts import redirect

def home_page(request):

    user = request.user
    if user.is_authenticated:
        if user.is_propStruttura:
            return redirect('core:gestisci_campi')
    return redirect('core:cerca_campo')

