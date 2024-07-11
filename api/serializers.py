from rest_framework import serializers

from pharma.models import ImitiSet, umutiReportSell, UmutiSold,\
      UmutiEntree, imitiSuggest


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

class ImitiSuggestSeria(serializers.Serializer):
    code_umuti = serializers.CharField(required=True, max_length=6)
    name_umuti = serializers.CharField(required=True)
    quantite_restant = serializers.IntegerField(required=True)

class LastIndexSeria(serializers.Serializer):
    last_umutiEntree = serializers.IntegerField(default=0)
    last_umutiEntree_backup = serializers.IntegerField(default=0)
    last_umutiSold = serializers.IntegerField(default=0)



