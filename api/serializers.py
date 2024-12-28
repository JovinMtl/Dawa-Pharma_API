from rest_framework import serializers

from pharma.models import ImitiSet, umutiReportSell, UmutiSold,\
      UmutiEntree, imitiSuggest, Assurance,\
      BonDeCommande


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

class BonCommaSeria(serializers.ModelSerializer):
    class Meta:
        model = BonDeCommande
        fields = '__all__'

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
    nom_med = serializers.CharField(max_length=30,defaut="null")
    qte = serializers.IntegerField(default=0)
    prix_achat = serializers.IntegerField(default=0)
    prix_vente = serializers.IntegerField(default=0)
    total = serializers.IntegerField(default=0)
    bnf = serializers.IntegerField(default=0)
    dette = serializers.IntegerField(default=0)
    assu = serializers.CharField(max_length=25,defaut="null")
    categ = serializers.CharField(max_length=15,defaut="null")
    date1 = serializers.DateTimeField(default=0)
    date2 = serializers.DateTimeField(default=0)
    num_du_bon = serializers.CharField(max_length=10,defaut="0000")



