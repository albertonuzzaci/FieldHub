from django.shortcuts import render, redirect#, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.views.generic import DetailView

from .models import Campo
from .forms import CampoForm


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
    

class DetailCampoView(DetailView):
    model = Campo
    template_name = "core/visualizza_campo.html"

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

#---------------FBV--------------------
def create_campo(request):
    if request.method == 'POST':
        form = CampoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/core/listacampi') 
    else:
        form = CampoForm()
    
    return render(request, 'core/crea_campo2.html', {'form': form})

@csrf_exempt
def prenota_campo(request, pk):
    if request.method == 'POST':
        #campo = get_object_or_404(Campo, pk=pk)
        return redirect('core:visualizza_campo', pk=pk)
    return redirect('core:listacampi')




