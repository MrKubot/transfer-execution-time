from django.shortcuts import render, redirect
from .models import Bank
import datetime

# Create your views here.


def home(response):
    banki = Bank.objects.all()
    data = {
        'banki': banki
    }

    return render(response, 'oblicz/home.html', data)


def godzina(response):
    
    bank1_nazwa = response.POST['bank1']
    bank2_nazwa = response.POST['bank2']
    data = response.POST['data']


    bank1 = Bank.objects.get(nazwa_banku=bank1_nazwa)
    bank2 = Bank.objects.get(nazwa_banku=bank2_nazwa)

    dane = {
        'bank1_wyjscie1': bank1.sesja_wych1,
        'bank1_wyjscie2': bank1.sesja_wych2,
        'bank1_wyjscie3': bank1.sesja_wych3,

        'bank2_wejscie1': bank2.sesja_przych1,
        'bank2_wejscie2': bank2.sesja_przych2,
        'bank2_wejscie3': bank2.sesja_przych3,

    }
    

    return render(response, 'oblicz/home.html')



