from django.db import models

# Create your models here.

class Bank(models.Model):
    nazwa_banku = models.CharField(max_length=60)
    sesja_przych1 = models.TimeField(null=True)
    sesja_przych2 = models.TimeField(null=True)
    sesja_przych3 = models.TimeField()
    sesja_wych1 = models.TimeField(null=True)
    sesja_wych2 = models.TimeField(null=True)
    sesja_wych3 = models.TimeField()
    