from rest_framework import serializers

from pharma.models import ImitiSet, umutiReportSell, UmutiSold,\
      UmutiEntree, imitiSuggest, Assurance


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



