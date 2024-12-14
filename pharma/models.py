from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.

# All the structure of Pharma operations will be defined here

class UmutiEntree(models.Model):
    date_winjiriyeko = models.DateTimeField(default=timezone.now())
    date_uzohererako = models.DateField(default=datetime.now())
    code_umuti = models.CharField(max_length=8, default='null')  #igizwe na Lettre zitatu hamwe na chiffres zibiri
    name_umuti = models.CharField(max_length=30, default='null')
    description_umuti = models.TextField(verbose_name="ukwo bawufata n'ico umaze, bizofasha uwutawuzi")
    type_umuti = models.CharField("Ni Flacon canke plaquette,",max_length=10, default='null')  # ...
    type_in  = models.CharField(max_length=10, default='null') #kurangura  carton
    ratio_type = models.FloatField(default=1) #ari carton ndayidandaza carton
    type_out = models.CharField(max_length=10, default='null') #kudetailla
    price_in = models.IntegerField(default=0)  #7: ayo Carton/plaquette yaranguwe
    price_out = models.IntegerField(default=0) #8: ayo plaquette tuyidandaza
    price_in_usd = models.FloatField(default=0)  #7: ayo Carton/plaquette yaranguwe muri usd
    price_out_usd = models.FloatField(default=0) #8: ayo plaquette tuyidandaza muri usd
    quantite_initial = models.IntegerField(default=0) # izinjiye ubwambere
    quantite_restant = models.IntegerField(default=0) #10: plaquette zisigaye
    location = models.CharField(max_length=10, default='null')  #11: ni nka cote yaho wowusanga vyoroshe
    code_operation = models.CharField(max_length=12, default='null') #code yo kwinjiza uwo muti(miti):commune
    operator = models.CharField(max_length=15, default='null')

    def __str__(self) -> str:
        return f"{self.code_umuti} {(str(self.date_winjiriyeko))[:7]}"

class UmutiEntreeBackup(models.Model):
    date_winjiriyeko = models.DateTimeField(default=timezone.now())
    date_uzohererako = models.DateField(default=datetime.now())
    code_umuti = models.CharField(max_length=8, default='null')  #igizwe na Lettre zitatu hamwe na chiffres zibiri
    name_umuti = models.CharField(max_length=30, default='null')
    description_umuti = models.TextField(verbose_name="ukwo bawufata n'ico umaze, bizofasha uwutawuzi")
    type_umuti = models.CharField("Ni Flacon canke plaquette,",max_length=10, default='null')  # ...
    type_in  = models.CharField(max_length=10, default='null') #kurangura  carton
    ratio_type = models.FloatField(default=1) #ari carton ndayidandaza carton
    type_out = models.CharField(max_length=10, default='null') #kudetailla
    price_in = models.IntegerField(default=0)  #7: ayo Carton/plaquette yaranguwe
    price_out = models.IntegerField(default=0) #8: ayo plaquette tuyidandaza
    price_in_usd = models.FloatField(default=0)  #7: ayo Carton/plaquette yaranguwe muri usd
    price_out_usd = models.FloatField(default=0) #8: ayo plaquette tuyidandaza muri usd
    quantite_initial = models.IntegerField(default=0) # izinjiye ubwambere
    quantite_restant = models.IntegerField(default=0) #10: plaquette zisigaye
    location = models.CharField(max_length=10, default='null')  #11: ni nka cote yaho wowusanga vyoroshe
    code_operation = models.CharField(max_length=12, default='null') #code yo kwinjiza uwo muti(miti):commune
    operator = models.CharField(max_length=15, default='null')

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
    price_out_usd = models.FloatField(default=0) #8: ayo plaquette tuyidandaza muri usd
    difference = models.IntegerField(default=0) #9: benefice ONY ADMIN
    quantite_restant = models.IntegerField(default=0) #10: plaquette zisigaye
    location = models.CharField(max_length=10, default='null')  #11: ni nka cote yaho wowusanga vyoroshe
    lot = models.TextField() #dates izohererako 
    # [
    #    {'date':"2025,04", 'qte':"3", 'code_operation':'12stM'},
    #    {'date':"2025,04", 'qte':"3", 'code_operation':'12stM'},
    # ]
    qte_entrant_big = models.IntegerField(default=0) #twisunga mukugira rapport y'iyisigaye
    date_last_vente = models.DateTimeField(default=timezone.now()) #aho uwo muti uheruka gusohoka ku murwayi
    checked_imiti = models.TextField() # for tracking imitiEntree checked(array of code_operation)
    checked_qte = models.TextField() # for tracking qte on each umutiEntree

    def __str__(self) -> str:
        return f"{self.code_umuti}:{self.quantite_restant}"


class Assurance(models.Model):
    name = models.CharField(max_length=25, default='null')
    rate_assure = models.PositiveIntegerField("Le Taux d'assurer le Malade",\
                        default=0, validators=[MinValueValidator(0),\
                                               MaxValueValidator(100)])

    def __str__(self):
        return f"{self.name}"

class BonDeCommande(models.Model):
    beneficiaire = models.CharField(max_length=25, default='inconnu')
    organization = models.ForeignKey(Assurance, on_delete=models.CASCADE,\
                                     default=1)
    num_beneficiaire = models.CharField(max_length=10, default="0000")
    num_du_bon = models.CharField(max_length=10, default="0000")
    date_du_bon = models.DateField(default=timezone.now)
    date_served = models.DateField(default=timezone.now)
    montant_dette = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.beneficiaire}" 

def getBonDeCommandeInstance():
    new_bon = None
    try:
        new_bon = BonDeCommande.objects.first()
    except BonDeCommande.DoesNotExist:
        new_bon = BonDeCommande.objects.create()
        new_bon.save()
    
    return new_bon

class UmutiSold(models.Model):
    """This one will record all the sale and benefit as well"""
    code_umuti = models.CharField(max_length=8, default='null')
    name_umuti = models.CharField(max_length=30, default='null')
    quantity = models.IntegerField(default=1) #quantity sold
    price_out = models.IntegerField(default=0) #unit price
    price_total = models.IntegerField(default=1) # q * p
    price_in = models.IntegerField(default=1)
    difference = models.IntegerField(default=0) #9: benefice
    code_operation_entrant = models.CharField(max_length=12, default='null') #code operation uyo muti winjiriyeko
    code_operation = models.CharField(max_length=12, default='null') #common with other sold together
    operator = models.CharField(max_length=15, default='null')
    date_operation = models.DateTimeField(default=timezone.now())
    bon_de_commande = models.ForeignKey(BonDeCommande,\
            on_delete=models.CASCADE, default=1)

class umutiReportSell(models.Model):
    """THis will contain report of its sale in a given period of time"""
    code_umuti = models.CharField(max_length=8, default='null')
    name_umuti = models.CharField(max_length=30, default='null')
    nb_vente = models.IntegerField(default=0)
    px_T_vente = models.IntegerField(default=0)
    benefice = models.IntegerField(default=0)
    nb_rest = models.IntegerField(default=0)
    px_T_rest = models.IntegerField(default=0)

class imitiSuggest(models.Model):
    """This table contains temporary imiti suggestion. 
    on each completion of endpoint's execution, it gets reinitialized.
    """
    code_umuti = models.CharField(max_length=8, default='null')
    name_umuti = models.CharField(max_length=30, default='null')
    qte = models.IntegerField(default=0)
    p_achat = models.IntegerField(default=0)
    p_vente = models.IntegerField(default=0)
    benefice = models.IntegerField(default=0)
    previous_date = models.DateTimeField(default=timezone.now())
    qte_big = models.IntegerField(default=0)
    qte_restant = models.IntegerField(default=0)


class UsdToBif(models.Model):
    """This table will contain only one field indicating the actual value
    of Usd into Bif.
    """
    actualExchangeRate = models.IntegerField(default=0)
    effect_date = models.DateTimeField(default=timezone.now())

    def __str__(self) -> str:
        return f"1$ = {self.actualExchangeRate} Bif. From {str(self.effect_date)[:7]}."

class InfoClient(models.Model):
    name = models.CharField(max_length=25, default='inconnu')
    phone_number = models.CharField(max_length=12, default='1111')
    assureur = models.ForeignKey(Assurance,on_delete=models.CASCADE)
    date_bon = models.DateField("Date yatangiweko", default=timezone.now)
