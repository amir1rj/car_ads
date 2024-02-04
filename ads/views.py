from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from account.permisions import IsOwnerOrReadOnly
from ads.serializers import AdSerializer
from ads.models import Car


# Create your views here.
class AdViewSets(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = AdSerializer
    permission_classes = [AllowAny]