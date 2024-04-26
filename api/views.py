from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

#importing my models from Pharma
from pharma.models import UmutiEntree

# Create your views here.

class EntrantImiti(viewsets.ViewSet):
    """Manages all the Entrant Operations"""

    @action(methods=['post'], detail=False,\
             permission_classes= [IsAuthenticated])
    def kurangura(self, request):
        dataReceived = request.data
        print(f"The data Received: {dataReceived}")

        return JsonResponse({"Things ":"well"})


