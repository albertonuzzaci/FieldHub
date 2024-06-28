from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse
from django.db.models import Avg

from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import Campo, Prenotazione, Struttura, Recensione
from .form import CreaCampoForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from users.models import ProprietarioStruttura, User, Utente
from django.contrib import messages

from datetime import datetime
#---------------PERMESSI--------------
class UtenteNormale(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.is_propStruttura:
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)

class UtenteStruttura(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            print("quaaa")
            return self.handle_no_permission()
        
        if request.user.is_utente:
            print("qua")
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)
#---------------CBV--------------------
class ListaCampiView(ListView):
    model = Campo
    template_name = 'core/listacampi.html'
    context_object_name = 'object_list'
    paginate_by = 6
    
    def get_model_name(self):
        return self.model._meta.verbose_name_plural
    
    def get_queryset(self):
        tipo_sport = self.request.GET.get('tipo_sport')
        luogo = self.request.GET.get('luogo')
        
        queryset = Campo.objects.all()
        if tipo_sport:
            queryset = queryset.filter(tipo_sport=tipo_sport)
        if luogo:
            queryset = queryset.filter(luogo=luogo)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lista dei campi trovati" 
        
        campi = self.get_queryset()
        campi_dict = {}
        
        for campo in campi:
            voto_medio = Recensione.objects.filter(campo=campo).aggregate(media=Avg('voto'))['media']
            if voto_medio is None:
                voto_medio = "-"
            else:
                voto_medio = round(voto_medio, 1)
            campi_dict[campo] = voto_medio

        # Gestione della paginazione
        paginator = Paginator(list(campi_dict.items()), self.paginate_by)
        page = self.request.GET.get('page')
        
        try:
            campi_paginati = paginator.page(page)
        except PageNotAnInteger:
            campi_paginati = paginator.page(1)
        except EmptyPage:
            campi_paginati = paginator.page(paginator.num_pages)
        
        context['object_list'] = campi_paginati
        context['campi_dict'] = dict(campi_paginati)
        context['page_obj'] = campi_paginati
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
            ora=ora,
            struttura=campo.struttura
        )
        
        context['data'] = data
        context['ora'] = ora
        context['campo'] = campo
        
        return context
'''
class PrenotazioniUtenteView(UtenteNormale, TemplateView):
    template_name = 'core/prenotazioni_utente.html'  # Nome del template da creare

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        utente =  Utente.objects.get(user=user)
       
        now = timezone.now()
        prenotazioni_vecchie = Prenotazione.objects.filter(
            utente__user=user,
            data__lte=now.date(),
        ).order_by('data', 'ora')

        # Creazione del dizionario per memorizzare l'esistenza della recensione
        prenotazioni_dict = {}

        for prenotazione in prenotazioni_vecchie:
            # Verifichiamo se esiste una recensione per quella prenotazione da parte dell'utente per il campo della prenotazione
            has_recensione = Recensione.objects.filter(utente=utente, campo=prenotazione.campo).exists()
            prenotazioni_dict[prenotazione] = has_recensione
            
        context['prenotazioni_vecchie'] = prenotazioni_dict
        
        context['prenotazioni_future'] = Prenotazione.objects.filter(
            utente__user=user,
            data__gt=now.date()
        ).order_by('data', 'ora')
        
        return context
'''
class PrenotazioniUtenteView(UtenteNormale, TemplateView):
    template_name = 'core/prenotazioni_utente.html'  # Nome del template da creare
    paginate_by = 4  # Numero di prenotazioni per pagina

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        utente = Utente.objects.get(user=user)
       
        now = timezone.now()
        prenotazioni_vecchie = Prenotazione.objects.filter(
            utente__user=user,
            data__lte=now.date(),
        ).order_by('data', 'ora')

        prenotazioni_future = Prenotazione.objects.filter(
            utente__user=user,
            data__gt=now.date()
        ).order_by('data', 'ora')

        # Creazione del dizionario per memorizzare l'esistenza della recensione
        prenotazioni_dict = {}

        for prenotazione in prenotazioni_vecchie:
            # Verifichiamo se esiste una recensione per quella prenotazione da parte dell'utente per il campo della prenotazione
            has_recensione = Recensione.objects.filter(utente=utente, campo=prenotazione.campo).exists()
            prenotazioni_dict[prenotazione] = has_recensione

        # Paginazione delle prenotazioni vecchie
        paginator_vecchie = Paginator(list(prenotazioni_dict.items()), self.paginate_by)
        page_vecchie = self.request.GET.get('page_vecchie')
        
        try:
            prenotazioni_vecchie_paginati = paginator_vecchie.page(page_vecchie)
        except PageNotAnInteger:
            prenotazioni_vecchie_paginati = paginator_vecchie.page(1)
        except EmptyPage:
            prenotazioni_vecchie_paginati = paginator_vecchie.page(paginator_vecchie.num_pages)
        
        # Paginazione delle prenotazioni future
        paginator_future = Paginator(prenotazioni_future, self.paginate_by)
        page_future = self.request.GET.get('page_future')
        
        try:
            prenotazioni_future_paginati = paginator_future.page(page_future)
        except PageNotAnInteger:
            prenotazioni_future_paginati = paginator_future.page(1)
        except EmptyPage:
            prenotazioni_future_paginati = paginator_future.page(paginator_future.num_pages)
        
        context['prenotazioni_vecchie'] = dict(prenotazioni_vecchie_paginati)
        context['prenotazioni_vecchie_page_obj'] = prenotazioni_vecchie_paginati
        context['prenotazioni_future'] = prenotazioni_future_paginati
        context['prenotazioni_future_page_obj'] = prenotazioni_future_paginati
        
        return context
    
class PrenotazioniStrutturaView(UtenteStruttura, TemplateView):
    template_name = 'core/prenotazioni_struttura.html'  # Nome del template da creare
    paginate_by = 5  # Numero di prenotazioni per pagina

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        struttura = get_object_or_404(ProprietarioStruttura, user=user).struttura
        
        prenotazioni = Prenotazione.objects.filter(struttura=struttura).order_by('data', 'ora')
        
        # Paginazione delle prenotazioni
        paginator = Paginator(prenotazioni, self.paginate_by)
        page = self.request.GET.get('page')
        
        try:
            prenotazioni_paginati = paginator.page(page)
        except PageNotAnInteger:
            prenotazioni_paginati = paginator.page(1)
        except EmptyPage:
            prenotazioni_paginati = paginator.page(paginator.num_pages)
        
        context['prenotazioni'] = prenotazioni_paginati
        context['page_obj'] = prenotazioni_paginati
        
        return context


class DetailCampoView(ListView):
    model = Recensione
    template_name = "core/visualizza_campo.html"
    context_object_name = 'recensioni'
    paginate_by = 3

    def get_queryset(self):
        self.campo = get_object_or_404(Campo, pk=self.kwargs['pk'])
        return Recensione.objects.filter(campo=self.campo)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.campo
        voto_medio = self.get_queryset().aggregate(media=Avg('voto'))['media']
        if voto_medio is None:
            voto_medio = "-"
        else:
            voto_medio = round(voto_medio, 1)
        context['voto_medio'] = voto_medio
        return context

class DetailStrutturaView(UtenteNormale, View):
    template_name = "core/visualizza_struttura.html"
    
    def get(self, request, pk):
        struttura = get_object_or_404(Struttura, pk=pk)
        
        return render(request, self.template_name, {'object': struttura})
   
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
        form = CreaCampoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('/')
        else:
            print("non valido")
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
    prenotazione = get_object_or_404(Prenotazione, pk=pk)
    prenotazione.delete()
    return redirect('core:prenotazioni_utente')  # Redirect alla lista delle prenotazioni dopo l'eliminazione


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


def salva_recensione(request, prenotazione_id):
    prenotazione = get_object_or_404(Prenotazione, id=prenotazione_id)
    
    if request.method == 'POST':
        voto = request.POST.get('voto')
        testo = request.POST.get('testo')
        oggi = timezone.localdate()
        recensione = Recensione(
            prenotazione=prenotazione,
            data_recensione=oggi,
            utente=request.user.utente,
            campo=prenotazione.campo,
            struttura=prenotazione.campo.struttura,
            testo=testo,
            voto=voto,
            data_prenotazione=prenotazione.data
        )
        try:
                recensione.save()
                
                return redirect(reverse('core:prenotazioni_utente') + '?review=ok')
        except Exception as e:
            print(e)
            return redirect(reverse('core:prenotazioni_utente') + '?review=no')
    return redirect('core:prenotazioni_utente')

