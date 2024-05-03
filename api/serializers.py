from rest_framework import serializers

from pharma.models import ImitiSet, umutiReportSell


class ImitiSetSeriazer(serializers.ModelSerializer):
    class Meta:
        model = ImitiSet
        fields = '__all__'

class umutiReportSellSeriazer(serializers.ModelSerializer):
    class Meta:
        model = umutiReportSell
        fields = '__all__'