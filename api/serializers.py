from rest_framework import serializers

from pharma.models import ImitiSet, umutiReportSell, UmutiSold,\
      UmutiEntree, imitiSuggest, Assurance,\
      Client, BonDeCommand, CriticalOperation, Info,\
      PerteMed


class ImitiSetSeriazer(serializers.ModelSerializer):
    class Meta:
        model = ImitiSet
        fields = '__all__'

class umutiReportSellSeriazer(serializers.ModelSerializer):
    class Meta:
        model = umutiReportSell
        fields = '__all__'

class UmutiSoldSeriazer(serializers.ModelSerializer):
    class Meta:
        model = UmutiSold
        fields = '__all__'

class UmutiEntreeSeriazer(serializers.ModelSerializer):
    class Meta:
        model = UmutiEntree
        fields = '__all__'

class imitiSuggestSeria(serializers.ModelSerializer):
    class Meta:
        model = imitiSuggest
        fields = '__all__'

class AssuranceSeria(serializers.ModelSerializer):
    class Meta:
        model = Assurance
        fields = '__all__'


class ClientSeria(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class BonDeCommandSeria(serializers.ModelSerializer):
    class Meta:
        model = BonDeCommand
        fields = '__all__'

class OperationSeria(serializers.ModelSerializer):
    class Meta:
        model = CriticalOperation
        fields = '__all__'

class InfoSeria(serializers.ModelSerializer):
    class Meta:
        model = Info
        fields = '__all__'       

class PerteSeria(serializers.Serializer): 
    nom_med = serializers.CharField(required=True, max_length=75)
    qte = serializers.IntegerField(default=0)
    prix_achat = serializers.IntegerField(default=0)
    prix_vente = serializers.IntegerField(default=0)
    who_did_it = serializers.CharField(required=True, max_length=35)
    motif = serializers.CharField(required=True, max_length=25)
    date_operation = serializers.CharField(required=True, max_length=45)

class ImitiSuggestSeria(serializers.Serializer):
    code_med = serializers.CharField(required=True, max_length=6)
    nom_med = serializers.CharField(required=True)
    quantite_restant = serializers.IntegerField(required=True)

class LastIndexSeria(serializers.Serializer):
    last_umutiEntree = serializers.IntegerField(default=0)
    last_umutiSold = serializers.IntegerField(default=0)

class SyntesiSeria(serializers.Serializer):
    qte = serializers.IntegerField(default=0)
    pa_t = serializers.IntegerField(default=0)
    pv_t = serializers.IntegerField(default=0)
    benefice = serializers.IntegerField(default=0)
    page_number = serializers.IntegerField(default=0)

class SoldAsBonSeria(serializers.Serializer):
    nom_med = serializers.CharField(max_length=30,default="null")
    qte = serializers.IntegerField()
    prix_achat = serializers.IntegerField()
    prix_vente = serializers.IntegerField()
    total = serializers.IntegerField()
    bnf = serializers.IntegerField()
    dette = serializers.IntegerField()
    assu = serializers.CharField(max_length=25,default="null")
    categ = serializers.CharField(max_length=15,default="null")
    date1 = serializers.DateTimeField()
    date2 = serializers.DateTimeField()
    num_du_bon = serializers.CharField(max_length=10,default="0000")


class CollectionSeria(serializers.Serializer):
    nom_med = serializers.CharField(max_length=75, default="med")
    qte = serializers.IntegerField(default=0)
    price = serializers.IntegerField(default=0)
    lot = serializers.CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True)
    

