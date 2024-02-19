from ads.filter import CarFilter
from ads.search_indexes import CarIndex
from rest_framework import viewsets, status
from rest_framework.response import Response
from account.permisions import IsOwnerOrReadOnly
from ads.serializers import AdSerializer
from ads.models import Car
from rest_framework.decorators import action
from ads.pagination import StandardResultSetPagination


class AdViewSets(viewsets.ModelViewSet, StandardResultSetPagination):
    queryset = Car.objects.filter(status="active")
    serializer_class = AdSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def create(self, request, **kwargs):
        serializer = AdSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.validated_data["user"] = request.user
            serializer.save()
            return Response({"response": " your ad was successfully created", }, status.HTTP_201_CREATED)
        return Response({"response": serializer.errors})

    @action(methods=['get',"post"], detail=False)
    def search(self, request):
        """
        Endpoint for searching ads.
        """
        query = request.GET.get('q')
        if not query:
            return Response({"error": "Missing query parameter 'q'."})

        queryset = CarIndex.objects.filter(text__icontains=query)
        car_ids = [obj.pk for obj in queryset]
        cars = self.queryset.filter(pk__in=car_ids)
        filterset = CarFilter(request.POST, queryset=cars)

        # Apply additional filters
        filtered_cars = filterset.qs

        # Paginate filtered results
        result = self.paginate_queryset(filtered_cars)
        serializer = AdSerializer(result, many=True)
        return self.get_paginated_response(serializer.data)
