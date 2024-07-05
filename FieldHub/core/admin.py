from django.contrib import admin
from .models import *

admin.site.register(Campo)
admin.site.register(Servizio)
admin.site.register(Recensione)
admin.site.register(Prenotazione)


class StrutturaAdmin(admin.ModelAdmin):
    list_display = ['nome_struttura', 'citta', 'indirizzo', 'num_civico', 'email', 'numTelefono', 'verified']
    actions = ['verify_struttura']

    def verify_struttura(self, request, queryset):
        for struttura in queryset:
            struttura.verified = True
            struttura.save()
        self.message_user(request, "Le strutture selezionate sono state verificate.")

    verify_struttura.short_description = "Verifica le strutture selezionate"


admin.site.register(Struttura, StrutturaAdmin)
