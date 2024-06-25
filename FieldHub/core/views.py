from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.views import View

from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import Campo, Prenotazione
from .form import CreaCampoForm

from users.models import ProprietarioStruttura, User, Utente

from datetime import datetime
#---------------PERMESSI--------------
class UtenteNormale(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.is_propStruttura:
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)

#---------------CBV--------------------
class ListaCampiView(ListView):
    model = Campo
    template_name = 'core/listacampi.html'
    context_object_name = 'object_list'
    
    def get_model_name(self):
        return self.model._meta.verbose_name_plural
    
    def get_queryset(self):
        tipo_sport = self.request.GET.get('tipo_sport')
        luogo = self.request.GET.get('luogo')
        if tipo_sport:
            return Campo.objects.filter(tipo_sport=tipo_sport)
        
        return Campo.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lista dei campi trovati"        
        return context
    
class PrenotazioneConfermataView(TemplateView):
    template_name = 'core/prenotazione_confermata.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        utente = get_object_or_404(Utente, user=user)
        
        id_campo = self.request.GET.get('id')
        campo = get_object_or_404(Campo, pk=id_campo)
        
        data = self.request.GET.get('data')
        ora = self.request.GET.get('ora')
        
        try:
            data = datetime.strptime(data, '%d/%m/%Y').date().isoformat()
        except ValueError:
            raise ValueError('Formato data non valido. Deve essere nel formato DD/MM/YYYY.')
        
        new_prenotazione, _ = Prenotazione.objects.get_or_create(
            utente=utente,
            campo=campo,
            data=data,
            ora=ora
        )
        
        context['data'] = data
        context['ora'] = ora
        context['campo'] = campo
        
        return context

class PrenotazioniUtenteView(UtenteNormale, TemplateView):
    template_name = 'core/prenotazioni_utente.html'  # Nome del template da creare

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        
        prenotazioni = Prenotazione.objects.filter(utente__user=user).order_by('data', 'ora')
        
        context['prenotazioni'] = prenotazioni
        
        return context

class DetailCampoView(UtenteNormale, View):
    template_name = "core/visualizza_campo.html"
    
    def get(self, request, pk):
        campo = get_object_or_404(Campo, pk=pk)
        
        return render(request, self.template_name, {'object': campo})

    def post(self, request, pk):
        # Logica per gestire il metodo POST, ad esempio prenotare il campo
        # Puoi ottenere il campo e l'utente dal request
        campo = get_object_or_404(Campo, pk=pk)
        # Logica per la prenotazione
        # ...
        return HttpResponseRedirect(request.path)
   
class CercaCampoListView(ListView):
    model = Campo
    template_name = 'core/cerca_campo.html'
    context_object_name = 'campi'
    #paginate_by = 10  
    
    def get_queryset(self):
        tipo_sport_query = self.request.GET.get('tipo_sport', '')
        return Campo.objects.filter(tipo_sport__icontains=tipo_sport_query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_sport_query'] = self.request.GET.get('tipo_sport', '')
        context['tipi_sport'] = Campo.TIPO_SPORT_CHOICES
        return context

class ListaCampiPerStrutturaView(ListView):
    model = Campo
    template_name = 'core/lista_campi_per_struttura.html'
    context_object_name = 'object_list'
    
    def get_model_name(self):
        return self.model._meta.verbose_name_plural
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Campo.objects.none() 

        self.struttura = get_object_or_404(ProprietarioStruttura, user=user).struttura
        return Campo.objects.filter(struttura=self.struttura)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['struttura'] = self.struttura
        return context

#---------------FBV--------------------
def create_campo(request):
    if request.method == 'POST':
        form = CreaCampoForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = CreaCampoForm(user=request.user)
    return render(request, 'core/crea_campo.html', {'form': form})


def elimina_campo(request, pk):
    if request.method == 'POST':
        campo = get_object_or_404(Campo, pk=pk)
        campo.delete()
        return redirect('core:gestisci_campi')  # Redirect alla lista dei campi dopo l'eliminazione

    return HttpResponse(status=405)  # Method Not Allowed

def elimina_prenotazione(request, pk):
    if request.method == 'POST':
        prenotazione = get_object_or_404(Prenotazione, pk=pk)
        prenotazione.delete()
        return redirect('core:prenotazioni_utente')  # Redirect alla lista delle prenotazioni dopo l'eliminazione

    return HttpResponse(status=405)  # Method Not Allowed


def home_page(request):
    user = request.user
    
    if user.is_propStruttura:
        return redirect('core:gestisci_campi')
    else:
        return redirect('core:cerca_campo')



def ore_libere(request, campo_id, data):
    data_prenotazione = datetime.strptime(data, "%Y-%m-%d").date()
    prenotazioni = Prenotazione.objects.filter(campo_id=campo_id, data=data_prenotazione)
    ore_prenotate = [prenotazione.ora.strftime("%H:%M") for prenotazione in prenotazioni]
    ore = [f'{hour}:00' for hour in range(10,22)]
    ore_libere = [ora for ora in ore if ora not in ore_prenotate]
    return JsonResponse(ore_libere, safe=False)

