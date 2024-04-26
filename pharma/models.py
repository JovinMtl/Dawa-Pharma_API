from django.db import models
from datetime import timezone

# Create your models here.

# All the structure of Pharma operations will be defined here

class UmutiEntree(models.Model):
    date_winjiriyeko = models.DateField(default=timezone.now())
    date_uzohererako = models.DateField(default=timezone.now())
    code_umuti = models.CharField(max_length=8, default='null')  #igizwe na Lettre zitatu hamwe na chiffres zibiri
    name_umuti = models.CharField(max_length=30, default='null')
    description_umuti = models.TextField() #ukwo bawufata n'ico umaze, bizofasha uwutawuzi
    type_umuti = models.CharField(max_length=10, default='null')  #Flacon, plaquette, ...
    type_in  = models.CharField(max_length=10, default='null') #kurangura
    type_out = models.CharField(max_length=10, default='null') #kudetailla
    price_in = models.IntegerField(default=0)  #7: ayo Carton/plaquette yaranguwe
    price_out = models.IntegerField(default=0) #8: ayo plaquette tuyidandaza
    difference = models.IntegerField(default=0) #9: benefice
    quantite_restant = models.IntegerField(default=0) #10: plaquette zisigaye
    location = models.CharField(max_length=10, default='null')  #11: ni nka cote yaho wowusanga vyoroshe


