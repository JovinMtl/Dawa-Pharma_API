from django.db import models
from datetime import datetime
from django.utils import timezone

# Create your models here.

# All the structure of Pharma operations will be defined here

class UmutiEntree(models.Model):
    date_winjiriyeko = models.DateField(default=datetime.now())
    date_uzohererako = models.DateField(default=datetime.now())
    code_umuti = models.CharField(max_length=8, default='null')  #igizwe na Lettre zitatu hamwe na chiffres zibiri
    name_umuti = models.CharField(max_length=30, default='null')
    description_umuti = models.TextField(verbose_name="ukwo bawufata n'ico umaze, bizofasha uwutawuzi")
    type_umuti = models.CharField("Ni Flacon canke plaquette,",max_length=10, default='null')  # ...
    type_in  = models.CharField(max_length=10, default='null') #kurangura
    ratio_type = models.FloatField(default=1) #ari carton ndayidandaza carton
    type_out = models.CharField(max_length=10, default='null') #kudetailla
    price_in = models.IntegerField(default=0)  #7: ayo Carton/plaquette yaranguwe
    price_out = models.IntegerField(default=0) #8: ayo plaquette tuyidandaza
    difference = models.IntegerField(default=0) #9: benefice
    quantite_initial = models.IntegerField(default=0) # izinjiye ubwambere
    quantite_restant = models.IntegerField(default=0) #10: plaquette zisigaye
    location = models.CharField(max_length=10, default='null')  #11: ni nka cote yaho wowusanga vyoroshe
    code_operation = models.CharField(max_length=8, default='null') #code yo kwinjiza uwo muti(miti):commune

    def __str__(self) -> str:
        return f"{self.code_umuti} {(str(self.date_winjiriyeko))[:7]}"

class ImitiSet(models.Model):
    """THis one will contain the unique Umuti and its availability"""
    code_umuti = models.CharField(max_length=8, default='null')  #igizwe na Lettre zitatu hamwe na chiffres zibiri
    name_umuti = models.CharField(max_length=30, default='null')
    description_umuti = models.TextField(verbose_name="ukwo bawufata n'ico umaze, bizofasha uwutawuzi")
    type_umuti = models.CharField("Ni Flacon canke plaquette,",max_length=10, default='null')  # ...
    type_in  = models.CharField(max_length=10, default='null') #kurangura
    ratio_type = models.FloatField(default=1) #ari carton ndayidandaza carton
    type_out = models.CharField(max_length=10, default='null') #kudetailla
    price_in = models.IntegerField(default=0)  #7: ayo Carton/plaquette yaranguwe
    price_out = models.IntegerField(default=0) #8: ayo plaquette tuyidandaza
    difference = models.IntegerField(default=0) #9: benefice ONY ADMIN
    quantite_restant = models.IntegerField(default=0) #10: plaquette zisigaye
    location = models.CharField(max_length=10, default='null')  #11: ni nka cote yaho wowusanga vyoroshe
    lot = models.TextField() #dates izohererako 
    # [
    #    {'date':"2025,04", 'qte':"3", 'code_operation':'12stM'},
    #    {'date':"2025,04", 'qte':"3", 'code_operation':'12stM'},
    # ]

    def __str__(self) -> str:
        return f"{self.code_umuti}:{self.quantite_restant}"
    

class UmutiSold(models.Model):
    """This one will record all the sale and benefit as well"""
    code_umuti = models.CharField(max_length=8, default='null')
    name_umuti = models.CharField(max_length=30, default='null')
    quantity = models.IntegerField(default=1)
    price_out = models.IntegerField(default=0)
    difference = models.IntegerField(default=0) #9: benefice
    code_operation_entrant = models.CharField(max_length=8, default='null') #code operation uyo muti winjiriyeko
    code_operation = models.CharField(max_length=8, default='null') #common with other sold together
    operator = models.CharField(max_length=15, default='null')
    date_operation = models.DateTimeField(default=timezone.now())

