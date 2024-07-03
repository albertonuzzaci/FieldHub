from django.views.generic import CreateView
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.crypto import get_random_string
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth import login, logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from .models import User, Utente, ProprietarioStruttura
from users.form import *
from django.urls import reverse
from django.contrib.auth.decorators import login_required

def register(request):
    return render(request, 'users/register.html')

def propStrutturaUpdateView(request):
    
    if not request.user.is_authenticated:
        raise PermissionDenied
    
    if not request.user.is_propStruttura:
        raise PermissionDenied
    
    struttura = get_object_or_404(ProprietarioStruttura, user=request.user).struttura
    
    initial_data = {
        'init_nome': request.user.first_name,
        'init_cognome': request.user.last_name,
        'init_nome_struttura': struttura.nome_struttura,
        'init_citta': struttura.citta,
        'init_indirizzo': struttura.indirizzo,
        'init_num_civico': struttura.num_civico,
        'init_descrizione': struttura.descrizione,
        'init_email': struttura.email,
        'init_numTelefono': struttura.numTelefono,
    }
    
    print(initial_data)
    if request.method == 'POST':
        struttura_form = UpdateStrutturaForm(request.POST, instance=struttura)
        user_form = UpdateUserForm(request.POST, request.FILES, instance=request.user)
        
        if user_form.is_valid() and struttura_form.is_valid():
            struttura_form.save()
            user_form.save()
            return redirect('/users/profile/?modified=ok')
        else:
            error_fields = [
                field  
                for form in [struttura_form, user_form]
                for field, error_list in form.errors.as_data().items()
                if error_list  
            ]
            error_params = '&'.join(f'{field}=no' for field in error_fields)
            return redirect(f'/users/profile/?modified=no&{error_params}')

    else:
        struttura_form = UpdateUtenteForm(instance=struttura)
        user_form = UpdateUserForm(instance=request.user)
        
    return render(request, 'users/edit_profile_struttura.html', 
                    {
                      'user_form': user_form,
                      'utente_form': struttura_form,
                      'initial_data': initial_data
                    }
                  )

def utenteUpdateView(request):
    if not request.user.is_authenticated:
        raise PermissionDenied
    
    if not request.user.is_utente:
        raise PermissionDenied
    
    utente = get_object_or_404(Utente, user=request.user)
    inital_data = {
        'init_nome': request.user.first_name,
        'init_cognome': request.user.last_name,
        'init_email': utente.email,
        'init_numTelefono': utente.numTelefono
    }
    
    if request.method == 'POST':
        utente_form = UpdateUtenteForm(request.POST, instance=utente)
        user_form = UpdateUserForm(request.POST, request.FILES, instance=request.user)

        if utente_form.is_valid() and user_form.is_valid():
            print(user_form)
            utente_form.save()
            user_form.save()
            return redirect('/users/profile/?modified=ok')
        else:
            error_fields = [
                field
                for form in [utente_form, user_form]
                for field, error_list in form.errors.as_data().items()
                if error_list
            ]
            error_params = '&'.join(f'{field}=no' for field in error_fields)
            return redirect(f'/users/profile/?modified=no&{error_params}')
    else:
        utente_form = UpdateUtenteForm(instance=utente)
        user_form = UpdateUserForm(instance=request.user)
        
    return render(request, 'users/edit_profile_utente.html', 
                  {
                      'user_form': user_form,
                      'utente_form': utente_form,
                      'inital_data': inital_data
                  })

class UtenteRegistrationView(CreateView):
    model = User
    form_class = UtenteSignUpForm
    template_name = 'users/utente_register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/core/cercacampo/?registration=ok')

class PropStrutturaRegistrationView(CreateView):
    model = User
    form_class = ProprietarioStrutturaSignUpForm
    template_name = 'users/propstruttura_register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/core/gestiscicampi/?registration=ok')

def login_request(request):
    if request.user.is_authenticated:
        raise PermissionDenied
        
    next_url = request.GET.get('next') or request.POST.get('next') or '/?login=ok'

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if next_url:
                    return redirect(next_url)

                    #return redirect('/?login=ok')
            else:
                messages.error(request, "Username o password sbagliati.")
        else:
            messages.error(request, "Username o password sbagliati.")
    
    return render(request, 'users/login.html', context={'form': AuthenticationForm(), 'next': next_url})
@login_required
def logout_view(request):
    logout(request)
    return redirect('/?logout=ok')

@login_required
def view_profile(request):
    user = get_object_or_404(User, pk=request.user.pk)
    
    if user.is_utente:
        profile_data = {
            'user': user,
            'utente': get_object_or_404(Utente, user=user)
        }
    elif user.is_propStruttura:
        admin_email = User.objects.filter(is_staff=True).values_list('email', flat=True).first()

        profile_data = {
            'user': user,
            'proprietario': get_object_or_404(ProprietarioStruttura, user=user),
            'struttura': get_object_or_404(Struttura, pk=user.proprietariostruttura.struttura.pk),
            'admin_email' : admin_email
        }

    return render(request, 'users/profile_detail.html', profile_data)



@login_required
def update_profile(request):
    user = request.user
    if user.is_utente:
        utente_view = utenteUpdateView
        return utente_view(request)
    elif user.is_propStruttura:
        prop_struttura_view = propStrutturaUpdateView
        return prop_struttura_view(request)
    else:
        raise Exception("Errore")

@login_required
def cambia_password(request):
    
    if request.method == 'POST':
        form = CambiaPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            return redirect(reverse('users:view_profile') + '?changed=ok')
    else:
        form = CambiaPasswordForm(request.user)

    return render(request, 'users/cambia_password.html', {'form': form})
'''
from django.http import JsonResponse
from django.core.files.storage import default_storage

@csrf_exempt  # Necessario solo se stai gestendo la vista con AJAX senza il CSRF token
def upload_image(request):
    if request.method == 'POST' and request.is_ajax():
        image_file = request.FILES.get('img')
        if image_file:
            try:
                # Salva il file nella cartella MEDIA_ROOT
                saved_path = default_storage.save('img/users_img/profile_pic/' + image_file.name, image_file)
                # Costruisci l'URL completo dell'immagine
                image_url = settings.MEDIA_URL + saved_path
                return JsonResponse({'url': image_url})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Nessun file ricevuto'}, status=400)
    else:
        return JsonResponse({'error': 'Richiesta non valida'}, status=400)


def save_image(img, save_path):
    # Genera un nome unico per l'immagine
    img_name = get_random_string(10) + '.jpg'
    path = os.path.join(settings.MEDIA_ROOT, save_path)

    # Assicurati che la directory di salvataggio esista, altrimenti creala
    if not os.path.exists(path):
        os.makedirs(path)

    # Salva l'immagine nel percorso specificato
    file_path = os.path.join(path, img_name)
    with open(file_path, 'wb+') as destination:
        for chunk in img.chunks():
            destination.write(chunk)

    # Ritorna il percorso relativo dell'immagine salvata
    return os.path.join(save_path, img_name)
'''
