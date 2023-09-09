from django.shortcuts import render, redirect
from .models import Bank
from bs4 import BeautifulSoup
import requests
import datetime

# Create your views here.


def home(response):
    banki = Bank.objects.all()
    data = {
        'banki': banki
    }

    return render(response, 'oblicz/home.html', data)


def godzina(response):
    
    # saves names of banks
    bank1_nazwa = response.POST['bank1']
    bank2_nazwa = response.POST['bank2']

    # transfer will be done immedietly if both banks are the same
    if bank1_nazwa == bank2_nazwa:
        moment_dotarcia = "Immedietly, because it's the same bank"
    else:
        # takes objects from db
        bank1 = Bank.objects.get(nazwa_banku=bank1_nazwa)
        bank2 = Bank.objects.get(nazwa_banku=bank2_nazwa)

        # saves data of provided banks
        dane = {
            'nazwa1': bank1_nazwa,
            'nazwa2': bank2_nazwa,

            'wyjscia':  {        
                'bank1_wyjscie1': bank1.sesja_wych1,
                'bank1_wyjscie2': bank1.sesja_wych2,
                'bank1_wyjscie3': bank1.sesja_wych3,
                        },

            'wejscia': {
                'bank2_wejscie1': bank2.sesja_przych1,
                'bank2_wejscie2': bank2.sesja_przych2,
                'bank2_wejscie3': bank2.sesja_przych3,
                        },

            'data': response.POST['data']
        }
        
        # little tweaks of string cause I want to use it as datetime module
        data_obiekt = change_to_datetime(dane)

        moment_dotarcia = oblicz_kiedy_dotrze(data_obiekt, dane)
        moment_dotarcia = str(moment_dotarcia)

    return render(response, 'oblicz/wynik.html', {'moment_dotarcia': moment_dotarcia})


def jakie_dni_wolne():
    r = requests.get('https://www.nbp.pl/home.aspx?f=/o_nbp/dni_wolne.html')
    soup = BeautifulSoup(r.text, 'html.parser')

    rok = int(soup.find(class_='bold').text.split(' ')[-1])

    tabela = soup.find(class_='nbptable')
    lista_dni = tabela.find_all('tr')
    lista_td_dni = []
    lista_td_miesiecy = []
    for dni in lista_dni[1:]:
        lista_td_dni.append(dni.text.split(' ')[2])
        lista_td_miesiecy.append(dni.text.split(' ')[3])

    zipped_lists = list(zip(lista_td_dni, lista_td_miesiecy))
    
    return zipped_lists, rok


def change_to_datetime(dane):
    data = dane['data'].split('T')[0]
    godzina = dane['data'].split('T')[1]

    hours = int(godzina.split(':')[0])
    minutes = int(godzina.split(':')[1])

    rok = int(data.split('-')[0])
    miesiac = int(data.split('-')[1])
    dzien = int(data.split('-')[2])

    data_obiekt = datetime.datetime(rok, miesiac, dzien, hours, minutes)
    
    return data_obiekt

def oblicz_kiedy_dotrze(data_obiekt, dane):

    godzina = data_obiekt.time()
    dzien = data_obiekt.weekday()

    dni_wolne, rok = jakie_dni_wolne()

    months_dict = {
        'stycznia': 1,
        'lutego': 2,
        'marca': 3,
        'kwietnia': 4,
        'maja': 5,
        'czerwca': 6,
        'lipca': 7,
        'sierpnia': 8,
        'września': 9,
        'października': 10,
        'listopada': 11,
        'grudnia': 12,
    }
    dni_wolne_objects = []
    miesiac = 1
    for dzien_tuple in dni_wolne:
        miesiac = months_dict[dzien_tuple[1]]
        dni_wolne_objects.append(datetime.date(rok, miesiac, int(dzien_tuple[0])))


    godzina_wyjscia = None
    czas_trwadnia_dni = 0

    # check hour of transfer FROM bank

    # first - "weird banks"...
    if dane['nazwa1'] == 'Bank Pekao SA':
        if godzina < datetime.time(hour=8, minute=30):
            godzina_wyjscia = datetime.time(hour=8, minute=30)
        elif godzina < datetime.time(hour=10, minute=30):
            godzina_wyjscia = datetime.time(hour=12, minute=30)
        elif godzina < datetime.time(hour=14, minute=25):
            godzina_wyjscia = datetime.time(hour=15, minute=0)
            
    elif dane['nazwa1'] == 'BNP Paribas':
        if godzina < datetime.time(hour=8, minute=0):
            godzina_wyjscia = datetime.time(hour=8, minute=0)
        elif godzina < datetime.time(hour=11, minute=15):
            godzina_wyjscia = datetime.time(hour=11, minute=45)
        elif godzina < datetime.time(hour=14, minute=15):
            godzina_wyjscia = datetime.time(hour=14, minute=15)

    elif dane['nazwa1'] == 'BOŚ Bank':
        if godzina < datetime.time(hour=8, minute=30):
            godzina_wyjscia = datetime.time(hour=9, minute=30)
        elif godzina < datetime.time(hour=12, minute=30):
            godzina_wyjscia = datetime.time(hour=13, minute=30)
        elif godzina < datetime.time(hour=15, minute=0):
            godzina_wyjscia = datetime.time(hour=16, minute=0)

    # ...then normal banks
    else:
        for mozliwa_godzina_wyjscia in dane['wyjscia'].values():
            if mozliwa_godzina_wyjscia == None:
                continue
            if godzina < mozliwa_godzina_wyjscia:
                godzina_wyjscia = mozliwa_godzina_wyjscia
                break
    


    # if transfer was made too late, he will be send next day ASAP
    if godzina_wyjscia == None:
        data_obiekt += datetime.timedelta(days=1)
        godzina_wyjscia = dane['wyjscia']['bank1_wyjscie1']

   
    while True:
        dzien = data_obiekt.weekday()
        # if transfer would be send during weekend, day is changed to monday and send ASAP
        if dzien > 4:
            data_obiekt += datetime.timedelta(days=2)
            godzina_wyjscia = dane['wyjscia']['bank1_wyjscie1']
        # if transfer would be send during holidays, it will be send next day ASAP
        elif data_obiekt.date() in dni_wolne_objects:
            data_obiekt += datetime.timedelta(days=1)
            godzina_wyjscia = dane['wyjscia']['bank1_wyjscie1']
        # other cases - proceed
        else:
            break


    # check on which hour will be transfer delivered
    godzina_dotarcia = None
    # first - 'weird' bank
    if dane['nazwa2'] == 'Bank Pekao SA':
        if godzina_wyjscia < datetime.time(hour=11, minute=00):
            godzina_dotarcia = datetime.time(hour=15, minute=0)
        elif godzina_wyjscia < datetime.time(hour=15, minute=00):
            godzina_dotarcia = datetime.time(hour=17, minute=0)
        elif godzina_wyjscia < datetime.time(hour=17, minute=30):
            godzina_dotarcia = datetime.time(hour=20, minute=0)
    # then normal banks
    else:
        for mozliwa_godzina_dotarcia in dane['wejscia'].values():
            if godzina_wyjscia < mozliwa_godzina_dotarcia:
                godzina_dotarcia = mozliwa_godzina_dotarcia
                break

    # if sended too late - next day, ASAP 
    if godzina_dotarcia == None:
        data_obiekt += datetime.timedelta(days=1)
        godzina_dotarcia = dane['wejscia']['bank2_wejscie1']
    
    while True:
        dzien = data_obiekt.weekday()
        # if transfer would be saved during weekend, day is changed to monday and send ASAP
        if dzien > 4:
            data_obiekt += datetime.timedelta(days=2)
            godzina_dotarcia = dane['wejscia']['bank2_wejscie1']
        # if transfer would be saved during holidays, it will be saved next day ASAP
        elif data_obiekt.date() in dni_wolne_objects:
            data_obiekt += datetime.timedelta(days=1)
            godzina_dotarcia = dane['wejscia']['bank2_wejscie1']
        # other cases - proceed
        else:
            break
    

    # replacing hour with proper time
    data_obiekt = data_obiekt.replace(hour=godzina_dotarcia.hour, minute=godzina_dotarcia.minute)  

    return data_obiekt


