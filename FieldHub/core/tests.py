from django.test import TestCase
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Struttura, Servizio, Campo, Prenotazione, Recensione
from users.models import Utente, ProprietarioStruttura, User
from django.utils import timezone
from datetime import timedelta
from django.db.utils import IntegrityError
from django.urls import reverse
from django.core.exceptions import PermissionDenied

# Create your tests here.
class PrenotazioneModelTest(TestCase):

    def setUp(self):
        '''
        SetUp Phase
        '''
        #---CREAZIONE DUE USER---
        self.user_utente = User.objects.create(
            username='testutente',
            nome='Federico',
            cognome='Utente',
            password='testpass',
            is_utente=True
        )
        self.user_propStruttura = User.objects.create(
            username='testpropStruttura',
            nome='Massimo',
            cognome='Proprietario',
            password='testpass',
            is_propStruttura=True
        )
        #---CREAZIONI UTENTI---
        self.utente = Utente.objects.create(
            user=self.user_utente,
            email='info@utente.com',
            numTelefono = '123456789'
        )
        self.struttura = Struttura.objects.create(
            nome_struttura='Centro Sportivo',
            citta='Roma',
            indirizzo='Via Roma',
            num_civico=10,
            descrizione='Descrizione della struttura',
            email='info@centrosportivo.it',
            numTelefono='123456789'
        )
        self.propStruttura = ProprietarioStruttura.objects.create(
            user=self.user_propStruttura,
            struttura=self.struttura
        )
        #----CREAZIONE CAMPO ASSOCIATO ALLA STRUTTURA----
        self.campo = Campo.objects.create(
            tipo_sport='tennis',
            coperto=False,
            costo=20.00,
            struttura=self.struttura
        )
        
        #-----CREAZIONE PRENOTAZIONE----
        self.data_futura = timezone.now().date() + timedelta(days=1)
        self.ora_data_futura = '15:00'
        self.prenotazione = Prenotazione.objects.create(
            utente=self.utente,
            campo=self.campo,
            data=self.data_futura,
            ora=self.ora_data_futura,
            struttura=self.struttura
        )
        
    def test_unique_together(self):
        '''
        Ogni prenotazione deve essere univoca in termini di campo-data-ora. Ogni campo può essere prenotato per una certa data, per una certa ora solo una volta. 
        '''
        with self.assertRaises(IntegrityError):
            Prenotazione.objects.create(
                utente=self.utente,
                campo=self.campo,
                data=self.data_futura,
                ora=self.ora_data_futura,
                struttura=self.struttura
            )
    
    def test_only_utente(self):
        '''
        Ogni prenotazione può essere fatta solo da utenti comuni e non propritari di strutture
        '''
        self.data= timezone.now().date() + timedelta(days=3)
        self.ora = '16:00'
        with self.assertRaises(ValueError):
            Prenotazione.objects.create(
                utente=self.propStruttura,
                campo=self.campo,
                data=self.data,
                ora=self.ora,
                struttura=self.struttura
            )

class RecensioneModelTest(TestCase):

    def setUp(self):
        '''
        SetUp Phase
        '''
        #---CREAZIONE DUE USER---
        self.user_utente = User.objects.create(
            username='testutente',
            nome='Federico',
            cognome='Utente',
            password='testpass',
            is_utente=True
        )
        self.user_propStruttura = User.objects.create(
            username='testpropStruttura',
            nome='Massimo',
            cognome='Proprietario',
            password='testpass',
            is_propStruttura=True
        )
        #---CREAZIONI UTENTI---
        self.utente = Utente.objects.create(
            user=self.user_utente,
            email='info@utente.com',
            numTelefono = '123456789'
        )
        self.struttura = Struttura.objects.create(
            nome_struttura='Centro Sportivo',
            citta='Roma',
            indirizzo='Via Roma',
            num_civico=10,
            descrizione='Descrizione della struttura',
            email='info@centrosportivo.it',
            numTelefono='123456789'
        )
        self.propStruttura = ProprietarioStruttura.objects.create(
            user=self.user_propStruttura,
            struttura=self.struttura
        )
        #----CREAZIONE CAMPO ASSOCIATO ALLA STRUTTURA----
        self.campo = Campo.objects.create(
            tipo_sport='tennis',
            coperto=False,
            costo=20.00,
            struttura=self.struttura
        )
        
        #-----CREAZIONE PRENOTAZIONE CON DATA PASSATA E DATA FUTURA----
        self.data_futura = timezone.now().date() + timedelta(days=2)
        self.ora = '15:00'
        self.prenotazione_futura = Prenotazione.objects.create(
            utente=self.utente,
            campo=self.campo,
            data=self.data_futura,
            ora=self.ora,
            struttura=self.struttura
        )
        
        self.data_passata = timezone.now().date() + timedelta(days=-1)
        self.prenotazione_passata = Prenotazione.objects.create(
            utente=self.utente,
            campo=self.campo,
            data=self.data_passata,
            ora=self.ora,
            struttura=self.struttura
        )
        
    def test_invalid_recensione_data(self):
        '''
        Si possono recensire solo prenotazioni con date passate
        '''
        with self.assertRaises(ValueError):
            Recensione.objects.create(
                data_recensione=timezone.now().date(),
                utente=self.utente,
                campo=self.campo,
                struttura=self.struttura,
                testo='Buono',
                voto=4,
                data_prenotazione=self.prenotazione_futura.data,
                prenotazione=self.prenotazione_futura
            )
    
    def test_unique_recensione_campo(self):
        '''
        Un utente può possono recensire un certo campo solo una volta
        '''
        
        Recensione.objects.create(
            data_recensione=timezone.now().date(),
            utente=self.utente,
            campo=self.campo,
            struttura=self.struttura,
            testo='Buono',
            voto=4,
            data_prenotazione=self.prenotazione_passata.data,
            prenotazione=self.prenotazione_passata
        )
        
        self.data_passata_2 = timezone.now().date() + timedelta(days=-5)
        self.prenotazione_passata_2 = Prenotazione.objects.create(
            utente=self.utente,
            campo=self.campo,
            data=self.data_passata_2,
            ora=self.ora,
            struttura=self.struttura
        )
        
        with self.assertRaises(IntegrityError):
            Recensione.objects.create(
                data_recensione=timezone.now().date(),
                utente=self.utente,
                campo=self.campo,
                struttura=self.struttura,
                testo='Buono',
                voto=4,
                data_prenotazione=self.prenotazione_passata_2.data,
                prenotazione=self.prenotazione_passata_2
            )
    
    def test_recensione_for_other_user(self):
        self.user_utente2 = User.objects.create(
            username='testutente2',
            nome='Federico',
            cognome='Utente',
            password='testpass',
            is_utente=True
        )
        self.utente2 = Utente.objects.create(
            user=self.user_utente2,
            email='info@utente.com',
            numTelefono = '123456789'
        )
        with self.assertRaises(ValueError):
            Recensione.objects.create(
                data_recensione=timezone.now().date(),
                utente=self.utente2,
                campo=self.campo,
                struttura=self.struttura,
                testo='Buono',
                voto=4,
                data_prenotazione=self.prenotazione_passata.data,
                prenotazione=self.prenotazione_passata
            )

class EliminaPrenotazioneViewTest(TestCase):

    def setUp(self):
        # CREAZIONE DUE UTENTI
        self.user_utente = User.objects.create(username='testutente',
                                                    nome='nome',
                                                    cognome='cognome',
                                                    password='testpass', 
                                                    is_utente=True
                                                    )
        
        self.utente = Utente.objects.create(user=self.user_utente, 
                                            email='utente@test.com', 
                                            numTelefono='123456789'
                                            )

        self.user_propStruttura = User.objects.create(username='testproprietario', 
                                                        password='testpass', 
                                                        nome='nome',
                                                        cognome='cognome',
                                                        is_propStruttura=True
                                                        )
        self.struttura = Struttura.objects.create(
            nome_struttura='Centro Sportivo',
            citta='Roma',
            indirizzo='Via Roma',
            num_civico=10,
            descrizione='Descrizione della struttura',
            email='info@centrosportivo.it',
            numTelefono='123456789'
        )
        self.propStruttura = ProprietarioStruttura.objects.create(
            user=self.user_propStruttura, 
            struttura=self.struttura
            )

        # CREAZIONE CAMPO ASSOCIATO ALLA STRUTTURA E PRENOTAZIONE

        self.campo = Campo.objects.create(
            tipo_sport='tennis',
            coperto=False,
            costo=20.00,
            struttura=self.struttura
        )

        self.prenotazione = Prenotazione.objects.create(
            utente=self.utente,
            campo=self.campo,
            data=timezone.now().date(),
            ora='10:00',
            struttura=self.struttura
        )
        
    def test_delete_just_own_prenotazioni(self):
        """
        Un utente può eliminare solo le proprie prenotazioni.
        """
        self.user_utente2 = User.objects.create_user(
            username='testutente2',
            password='testpass',
            first_name='nome',
            last_name='cognome',
            is_utente=True
        )
        
        self.utente2 = Utente.objects.create(
            user=self.user_utente2,
            email='utente2@test.com',
            numTelefono='123456789'
        )
        
        
        self.client.login(username='testutente2', password='testpass')
    

        response = self.client.post(reverse('core:elimina_prenotazione', args=[self.prenotazione.pk]))
        self.assertEqual(response.status_code, 403)

class PrenotazioniUtenteViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', is_utente=True)
        self.utente = Utente.objects.create(user=self.user, email='utente@test.com', numTelefono='123456789')

        self.struttura = Struttura.objects.create(
            nome_struttura='Centro Sportivo',
            citta='Roma',
            indirizzo='Via Roma',
            num_civico=10,
            descrizione='Descrizione',
            email='info@centrosportivo.it',
            numTelefono='123456789'
        )

        self.campo = Campo.objects.create(
            tipo_sport='tennis',
            coperto=False,
            costo=20.00,
            struttura=self.struttura
        )

        now = timezone.now().date()
        ora_passata = timezone.now().time().replace(hour=9, minute=0, second=0)

        # Crea prenotazioni vecchie
        for i in range(20):
            Prenotazione.objects.create(
                utente=self.utente,
                campo=self.campo,
                data=now - timezone.timedelta(days=i + 1),
                ora=ora_passata,
                struttura=self.struttura
            )

    def test_last_old_prenotazione_before_today(self):
        '''
        Verifico che l'ultima recensione dell'ultima pagina delle prenotazioni vecchie sia minore di quella attuale
        '''
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('core:prenotazioni_utente') + '?page_vecchie=1')
        
        prenotazioni_vecchie_page = response.context.get('prenotazioni_vecchie_page_obj')
        
        self.assertIsNotNone(prenotazioni_vecchie_page)
        
        last_old_booking = list(prenotazioni_vecchie_page)[-1][0]
        
        self.assertTrue(last_old_booking.data < timezone.now().date())
    
    def test_no_prenotazione_nuovo_utente(self):
        new_user = User.objects.create_user(username='newuser', password='newpass', is_utente=True)
        Utente.objects.create(user=new_user, email='newuser@test.com', numTelefono='987654321')

        self.client.login(username='newuser', password='newpass')
        response = self.client.get(reverse('core:prenotazioni_utente'))

        self.assertContains(response, 'Nessuna prenotazione da recensire')
        self.assertContains(response, 'Nessuna prenotazione futura')

class OreLibereTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='testpass', is_utente=True)
        self.utente = Utente.objects.create(user=self.user, email='utente@test.com', numTelefono='123456789')

        self.struttura = Struttura.objects.create(
            nome_struttura='Centro Sportivo',
            citta='Roma',
            indirizzo='Via Roma',
            num_civico=10,
            descrizione='Descrizione della struttura',
            email='info@centrosportivo.it',
            numTelefono='123456789'
        )

        self.campo = Campo.objects.create(
            tipo_sport='tennis',
            coperto=False,
            costo=20.00,
            struttura=self.struttura
        )

    def test_ore_libere_no_prenotazioni(self):
        '''
        Controllo che in un giorno senza prenotazioni mi vengano ritornate tutte le ore
        '''
        self.client.login(username='testuser', password='testpass')
        data = timezone.now().date().strftime("%Y-%m-%d")
        response = self.client.get(reverse('core:ore_libere', args=[self.campo.id, data]))
        
        self.assertEqual(response.status_code, 200)
        ore_libere = response.json()
        ore_attese = [f'{hour}:00' for hour in range(10, 22)]
        
        self.assertEqual(ore_libere, ore_attese)