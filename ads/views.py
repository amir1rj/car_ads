from ads.filter import CarFilter, ExhibitionFilter
from ads.search_indexes import CarIndex, ExhibitionIndex
from rest_framework import viewsets, status
from rest_framework.response import Response
from account.permisions import IsOwnerOrReadOnly
from ads.serializers import AdSerializer, ExhibitionSerializer
from ads.models import Car, View, Exhibition, ExhView
from rest_framework.decorators import action
from ads.pagination import StandardResultSetPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


class AdViewSets(viewsets.ModelViewSet, StandardResultSetPagination):
    queryset = Car.objects.filter(status="active")
    serializer_class = AdSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if user has already viewed this ad
        if request.user.is_authenticated:
            viewed = View.objects.filter(user=request.user, ad=instance).exists()

            # If not viewed, create a new View record and increment view count (optional)
            if not viewed:
                View.objects.create(user=request.user, ad=instance)
                instance.view_count += 1
                instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        description="Search for ads based on various filters.",
        parameters=[
            OpenApiParameter(name='brand', description='Filter by car brand.', required=False, type=str),
            OpenApiParameter(name='car_type', description='Filter by car car type.', required=False, type=str),
            OpenApiParameter(name='body type', description='Filter by car body type.', required=False, type=str),

            OpenApiParameter(name='model', description='Filter by car model.', required=False, type=str),
            OpenApiParameter(name='color', description='Filter by car color', required=False, type=str),
            OpenApiParameter(name='transmission', description='Filter by car transmission', required=False, type=str),
            OpenApiParameter(name='body_condition', description='Filter by car body_condition', required=False,
                             type=str),
            OpenApiParameter(name='city', description='Filter by car city',
                             required=False, type=str,
                             examples=[
                                 OpenApiExample(
                                     'Example 1',
                                     summary='Filter for all cities',
                                     description='if we dont need to filter by city',
                                     value='همه شهر ها'
                                 ),
                                 OpenApiExample(
                                     'Example 2',
                                     summary='filter by"اصفهان" in cities ',
                                     description='',
                                     value='اصفهان'
                                 ),
                             ]
                             ),
            OpenApiParameter(
                name='price',
                type=str,
                description='Filter by price range (format: "min,max").',
                examples=[
                    OpenApiExample(
                        'Example 1',
                        summary='Filter for ads with prices between 5000 and 10000',
                        description='you should use price_min and price_max',
                        value='5000,10000'
                    ),
                ]
            ),
            OpenApiParameter(
                name='kilometer',
                type=str,
                description='Filter by kilometer range (format: "min,max").',
                examples=[
                    OpenApiExample(
                        'Example 1',
                        summary='Filter for ads with kilometers between 10000 and 50000',
                        description='you should use kilometer_min and kilometer_max',
                        value='10000,50000'
                    ),
                ]
            ),
            OpenApiParameter(
                name='year',
                type=str,
                description='Filter by year range (format: "min,max").',
                examples=[
                    OpenApiExample(
                        'Example 1',
                        summary='Filter for ads from years 2015 to 2020',
                        description='you should use year_min and year_max',
                        value='2015,2020'
                    ),
                ]
            ),

        ],

    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        modified_get = request.GET.copy()
        if not modified_get.get("city"):
            modified_get["city"] = self.request.user.profile.city
        if modified_get.get("city") == "همه شهر ها":
            del modified_get["city"]
        filter_set = CarFilter(modified_get, queryset=queryset)
        filtered_queryset = filter_set.qs
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)

    def create(self, request, **kwargs):
        serializer = AdSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.validated_data["user"] = request.user
            serializer.save()
            return Response({"response": " your ad was successfully created", }, status.HTTP_201_CREATED)
        return Response({"response": serializer.errors})

    @extend_schema(
        description="Search for ads based on various filters.",
        parameters=[
            OpenApiParameter(name='brand', description='Filter by car brand.', required=False, type=str),
            OpenApiParameter(name='model', description='Filter by car model.', required=False, type=str),
            OpenApiParameter(name='color', description='Filter by car color', required=False, type=str),
            OpenApiParameter(name='transmission', description='Filter by car transmission', required=False, type=str),
            OpenApiParameter(name='body_condition', description='Filter by car body_condition', required=False,
                             type=str),
            OpenApiParameter(name='car_type', description='Filter by car car type.', required=False, type=str),
            OpenApiParameter(name='body type', description='Filter by car body type.', required=False, type=str),
            OpenApiParameter(
                name='price',
                type=str,
                description='Filter by price range (format: "min,max").',
                examples=[
                    OpenApiExample(
                        'Example 1',
                        summary='Filter for ads with prices between 5000 and 10000',
                        description='you should use price_min and price_max',
                        value='5000,10000'
                    ),
                ]
            ),
            OpenApiParameter(
                name='kilometer',
                type=str,
                description='Filter by kilometer range (format: "min,max").',
                examples=[
                    OpenApiExample(
                        'Example 1',
                        summary='Filter for ads with kilometers between 10000 and 50000',
                        description='you should use kilometer_min and kilometer_max',
                        value='10000,50000'
                    ),
                ]
            ),
            OpenApiParameter(
                name='year',
                type=str,
                description='Filter by year range (format: "min,max").',
                examples=[
                    OpenApiExample(
                        'Example 1',
                        summary='Filter for ads from years 2015 to 2020',
                        description='you should use year_min and year_max',
                        value='2015,2020'
                    ),
                ]
            ),
            OpenApiParameter(
                name='q',
                description="Search query. Supports full-text search and filtering by brand, model, and description.",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        'Example 1',
                        summary='Search for cars with "BMW" in brand or model',
                        description='',
                        value='BMW'
                    ),
                    OpenApiExample(
                        'Example 2',
                        summary='Search for cars with "fast" in description ',
                        description='',
                        value='fast'
                    ),
                ]
            ),

        ],

    )
    @action(methods=['get'], detail=False)
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
        filter_set = CarFilter(request.GET, queryset=cars)

        # Apply additional filters
        filtered_cars = filter_set.qs

        # Paginate filtered results
        result = self.paginate_queryset(filtered_cars)
        serializer = AdSerializer(result, many=True)
        return self.get_paginated_response(serializer.data)


class ExhibitionViewSet(viewsets.ModelViewSet, StandardResultSetPagination):
    queryset = Exhibition.objects.all()
    serializer_class = ExhibitionSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def update(self, request, pk=None, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        data = request.data.copy()
        if data.get('company_name') == instance.company_name:
            del request.data['company_name']
        serializer = ExhibitionSerializer(data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.update(instance=instance, validated_data=serializer.validated_data)
            return Response({"response": " your exhibition updated"}, status.HTTP_200_OK)
        return Response({"response": serializer.errors})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if user has already viewed this ad
        if request.user.is_authenticated:
            viewed = ExhView.objects.filter(user=request.user, exh=instance).exists()

            # If not viewed, create a new View record and increment view count (optional)
            if not viewed:
                ExhView.objects.create(user=request.user, exh=instance)
                instance.view_count += 1
                instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        description="Search for ads based on various filters.",
        parameters=[
            OpenApiParameter(name='city', description='Filter by car city.', required=False, type=str),

        ],

    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        filter_set = ExhibitionFilter(request.GET, queryset=queryset)
        filtered_queryset = filter_set.qs
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Search for ads based on various filters.",
        parameters=[
            OpenApiParameter(name='city', description='Filter by car city.', required=False, type=str),

            OpenApiParameter(
                name='q',
                description="Search query. Supports full-text search and company name and description.",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        'Example 1',
                        summary='Search for cars with "امیر " in brand or model',
                        description='',
                        value='امیر'
                    ),
                    OpenApiExample(
                        'Example 2',
                        summary='Search for cars with "معتبر" in description ',
                        description='',
                        value='معتبر'
                    ),
                ]
            ),

        ],

    )
    @action(methods=['get'], detail=False)
    def search(self, request):
        """
        Endpoint for searching ads.
        """
        query = request.GET.get('q')
        if not query:
            return Response({"error": "Missing query parameter 'q'."})

        queryset = ExhibitionIndex.objects.filter(text__icontains=query)
        exhibition_ids = [obj.pk for obj in queryset]
        exhibitions = self.queryset.filter(pk__in=exhibition_ids)
        filter_set = ExhibitionFilter(request.GET, queryset=exhibitions)

        # Apply additional filters
        filtered_exh = filter_set.qs

        # Paginate filtered results
        result = self.paginate_queryset(filtered_exh)
        serializer = ExhibitionSerializer(result, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)
