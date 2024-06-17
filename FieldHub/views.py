from django.http import HttpResponse

def home_page(request):
    response = "ciao"
    
    return HttpResponse(response)