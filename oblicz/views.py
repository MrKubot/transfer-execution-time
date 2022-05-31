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
    pass


