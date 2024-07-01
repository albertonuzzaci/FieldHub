from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.db.models import Q

from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse
from django.db.models import Avg


from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import Campo, Prenotazione, Struttura, Recensione
from .form import CreaCampoForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from users.models import ProprietarioStruttura, Utente

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
            return self.handle_no_permission()
        
        if request.user.is_utente:
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)
#---------------CBV--------------------

from django.db.models import Avg, Q

class ListaCampiView(ListView):
    model = Campo
    template_name = 'core/listacampi.html'
    context_object_name = 'object_list'
    paginate_by = 6
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_propStruttura:  # Accessibile ai non loggati e agli utenti normali / NON accessibile solo alle strutture
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def get_model_name(self):
        return self.model._meta.verbose_name_plural
    
    def get_queryset(self):
        tipo_sport = self.request.GET.get('tipo_sport')
        luogo = self.request.GET.get('luogo')
        coperto = self.request.GET.get('coperto') 
        ordinamento = self.request.GET.get('ordinamento', 'voto_medio')  
        ordine = self.request.GET.get('ordine', 'asc')  

        queryset = Campo.objects.all()

        if tipo_sport:
            queryset = queryset.filter(tipo_sport=tipo_sport)
        if luogo:
            queryset = queryset.filter(struttura__citta__icontains=luogo)  # Case insensitive
        if coperto in ['True', 'False']:
            queryset = queryset.filter(coperto=(coperto == 'True'))
        
        queryset = queryset.annotate(voto_medio=Avg('recensioni__voto'))

        if ordinamento:
            if ordine == 'asc':
                queryset = queryset.order_by(ordinamento)
            elif ordine == 'desc':
                queryset = queryset.order_by(f'-{ordinamento}')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lista dei campi trovati" 
        
        campi = self.get_queryset()
        campi_dict = {}
        
        for campo in campi:
            voto_medio = campo.voto_medio
            if voto_medio is None:
                voto_medio = "-"
            else:
                voto_medio = round(voto_medio, 1)
            campi_dict[campo] = voto_medio

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

        context['tipo_sport'] = self.request.GET.get('tipo_sport', '')
        context['luogo'] = self.request.GET.get('luogo', '')
        context['ordinamento'] = self.request.GET.get('ordinamento', 'voto_medio')  
        context['ordine'] = self.request.GET.get('ordine', 'asc')  
        context['coperto'] = self.request.GET.get('coperto', '')  
        
        return context

    
class PrenotazioneConfermataView(UtenteNormale, TemplateView):
    template_name = 'core/prenotazione_confermata.html'

    def post(self, request, *args, **kwargs):
        user = self.request.user
        utente = get_object_or_404(Utente, user=user)

        id_campo = request.POST.get('id')
        campo = get_object_or_404(Campo, pk=id_campo)

        data = request.POST.get('data')
        ora = request.POST.get('ora')

        try:
            data = datetime.strptime(data, '%d/%m/%Y').date().isoformat()
        except ValueError:
            raise ValueError('Formato data non valido. Deve essere nel formato DD/MM/YYYY.')

        if Prenotazione.objects.filter(
            utente=utente,
            campo=campo,
            data=data,
            ora=ora,
            struttura=campo.struttura
        ).exists():
            raise ValueError('Prenotazione già esistente per la data e ora selezionate.')

        Prenotazione.objects.create(
            utente=utente,
            campo=campo,
            data=data,
            ora=ora,
            struttura=campo.struttura
        )

        context = self.get_context_data()
        context['data'] = data
        context['ora'] = ora
        context['campo'] = campo

        return self.render_to_response(context)

class PrenotazioniUtenteView(UtenteNormale, TemplateView):
    template_name = 'core/prenotazioni_utente.html' 
    paginate_by = 5  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        utente = Utente.objects.get(user=user)
       
        now = timezone.localtime(timezone.now())
        prenotazioni_vecchie = Prenotazione.objects.filter(
            Q(data__lt=now.date()) |
            Q(data=now.date(), ora__lt=now.time()),
            utente__user=user
        ).order_by('data', 'ora')

        prenotazioni_future = Prenotazione.objects.filter(
            Q(data__gt=now.date()) |
            Q(data=now.date(), ora__gte=now.time()),
            utente__user=user
        ).order_by('data', 'ora')

        prenotazioni_dict = {}

        for prenotazione in prenotazioni_vecchie:
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
    template_name = 'core/prenotazioni_struttura.html'
    paginate_by = 7

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        struttura = get_object_or_404(ProprietarioStruttura, user=user).struttura
        prenotazioni = Prenotazione.objects.filter(struttura=struttura).order_by('data', 'ora')

        now = timezone.localtime(timezone.now())

        prenotazioni_dict = {
            prenotazione: prenotazione.data > now.date() or (prenotazione.data == now.date() and prenotazione.ora >= now.time())
            for prenotazione in prenotazioni
        }

        paginator = Paginator(list(prenotazioni_dict.items()), self.paginate_by)
        page = self.request.GET.get('page')

        try:
            prenotazioni_paginati = paginator.page(page)
        except PageNotAnInteger:
            prenotazioni_paginati = paginator.page(1)
        except EmptyPage:
            prenotazioni_paginati = paginator.page(paginator.num_pages)


        context['prenotazioni'] = dict(prenotazioni_paginati)
        context['page_obj'] = prenotazioni_paginati

        return context

class DetailCampoView(UtenteNormale, ListView):
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
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_propStruttura: #accesso negato SOLO SE sei loggato come struttura
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
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
    if not request.user.is_authenticated or not request.user.is_propStruttura:
        raise PermissionDenied
    
    if request.method == 'POST':
        
        form = CreaCampoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('core:gestisci_campi') + '?created=ok')
        else:
            return redirect(reverse('core:gestisci_campi') + '?created=no')
    else:
        form = CreaCampoForm(user=request.user)
    return render(request, 'core/crea_campo.html', {'form': form})


def elimina_campo(request, pk):
    if request.method == 'POST':
        campo = get_object_or_404(Campo, pk=pk)
        propStruttura = get_object_or_404(ProprietarioStruttura, struttura=campo.struttura)
        
        #si può eliminare un campo solo di cui si è i proprietari
        if propStruttura.user != request.user:
            raise PermissionDenied
        
        campo.delete()
        
        return redirect(reverse('core:gestisci_campi') + '?deleted=ok')


    return PermissionDenied

def elimina_prenotazione(request, pk):
    prenotazione = get_object_or_404(Prenotazione, pk=pk)
    
    if not request.user.is_authenticated:
        raise PermissionDenied
    
    if request.user.is_propStruttura:
        # il proprietario della struttura della prenotazione che si sta cercando di eliminare
        # deve essere lo stesso che sta facendo la richiesta
        propStruttura = get_object_or_404(ProprietarioStruttura, struttura=prenotazione.struttura)
        if propStruttura.user != request.user:
            raise PermissionDenied
        
        prenotazione.delete()
        return redirect(reverse('core:prenotazioni_struttura') + '?prenotazionedeleted=ok')

    if request.user.is_utente:
        utente = prenotazione.utente
        # l'utente della prenotazione che si sta cercando di eliminare
        # deve essere lo stesso che sta facendo la richiesta
        if utente.user != request.user:
            raise PermissionDenied
        
        prenotazione.delete()
         
        return redirect(reverse('core:prenotazioni_utente') + '?prenotazionedeleted=ok')
    
    return redirect('/')  


def home_page(request):
    user = request.user
    
    if user.is_propStruttura:
        return redirect('core:gestisci_campi')
    else:
        return redirect('core:cerca_campo')

def ore_libere(request, campo_id, data):
    if not request.user.is_authenticated:
        raise PermissionDenied
    
    if request.user.is_propStruttura:
        raise PermissionDenied
    
    data_prenotazione = datetime.strptime(data, "%Y-%m-%d").date()
    prenotazioni = Prenotazione.objects.filter(campo_id=campo_id, data=data_prenotazione)
    ore_prenotate = [prenotazione.ora.strftime("%H:%M") for prenotazione in prenotazioni]
    ore = [f'{hour}:00' for hour in range(10,22)]
    ore_libere = [ora for ora in ore if ora not in ore_prenotate]
    return JsonResponse(ore_libere, safe=False)

def salva_recensione(request, prenotazione_id):
    if not request.user.is_authenticated:
        raise PermissionDenied
    
    if request.user.is_propStruttura:
        raise PermissionDenied
    
    prenotazione = get_object_or_404(Prenotazione, id=prenotazione_id)
    utente = get_object_or_404(Utente, user=request.user)
    
    # se l'utente che fa richiesta di salvataggio recensione
    # è diverso dall'utente che ha prenotato
    # allora lancio permission denied
    if prenotazione.utente != utente:
        raise PermissionDenied
    
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
            return redirect(reverse('core:prenotazioni_utente') + '?review=no')
    return redirect('core:prenotazioni_utente')

def esporta_prenotazioni(request):
    if not request.user.is_authenticated:
        raise PermissionDenied
    
    if not request.user.is_propStruttura:
        raise PermissionDenied
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        user = request.user
        struttura = get_object_or_404(ProprietarioStruttura, user=user).struttura

        prenotazioni = Prenotazione.objects.filter(
            struttura=struttura,
            data__range=[start_date, end_date]
        ).order_by('data', 'ora')

        lines = []
        for prenotazione in prenotazioni:
            line = f"Data: {prenotazione.data.strftime('%d %B %Y')}, Ora: {prenotazione.ora}, Campo: {prenotazione.campo.get_tipo_sport_display()}, Utente: {prenotazione.utente.user.username}\n"
            lines.append(line)
        txt_content = "\n".join(lines)

        response = HttpResponse(txt_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="prenotazioni_{start_date}_to_{end_date}.txt"'
        #attachment serve per scaricare altrimenti si vede solo nel browser

        return response