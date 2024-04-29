from rest_framework import serializers

from pharma.models import ImitiSet


class ImitiSetSeriazer(serializers.ModelSerializer):
    class Meta:
        model = ImitiSet
        fields = '__all__'