from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from account.permisions import IsOwnerOrReadOnly
from ads.serializers import AdSerializer
from ads.models import Car


# Create your views here.
class AdViewSets(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsOwnerOrReadOnly]
    def create(self, request, **kwargs):
        serializer = AdSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.validated_data["user"] = request.user
            serializer.save()
            return Response({"response": " your ad was successfully created",},status.HTTP_201_CREATED)
        return Response({"response": serializer.errors})