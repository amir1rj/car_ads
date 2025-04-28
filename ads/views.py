import json

import requests
from django.conf import settings
from django.db.models import Min, Max
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError, NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import PermissionDenied
from account.exceptions import CustomValidationError
from account.logging_config import logger
from account.models import User
from ads.filter import CarFilter, ExhibitionFilter
from ads.search_indexes import CarIndex, ExhibitionIndex
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from account.permisions import IsOwnerOrReadOnly, IsOwnerOfCar
from ads.serializers import AdSerializer, ExhibitionSerializer, ExhibitionVideoSerializer, ImageSerializer, \
    BrandSerializer, CarModelSerializer, SelectedBrandSerializer, FavoriteSerializer, ColorSerializer, \
    ZarinpalPaymentRequestSerializer, SubscriptionPlansSerializer, SubscriptionSerializer, SubscriptionCreateSerializer
from ads.models import Car, View, Exhibition, ExhView, ExhibitionVideo, Image, Brand, CarModel, SelectedBrand, Favorite, \
    Color, SubscriptionPlans, TransactionLog, Subscription
from rest_framework.decorators import action
from ads.pagination import StandardResultSetPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view
from rest_framework import generics
from rest_framework.views import APIView

sandbox = 'www'
domain = settings.DOMAIN
ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"


@extend_schema(tags=['Subscription & Payments'])
class ZarinpalPaymentView(APIView):
    serializer_class = ZarinpalPaymentRequestSerializer

    def post(self, request):
        """ send subscription plan id and des if needed and get Payment gateway """
        try:
            serializer = ZarinpalPaymentRequestSerializer(data=request.data)
            if serializer.is_valid():
                # amount = serializer.validated_data['amount']
                subscription_id = serializer.validated_data['subscription_id']
                subscription = Subscription.objects.get(id=subscription_id)
                subscription_plan = subscription.subscription_plan
                amount = subscription_plan.price
                description = serializer.validated_data['description']
                phone = serializer.validated_data.get('phone', '')

                data = {
                    "MerchantID": settings.MERCHANT,
                    "Amount": amount,
                    "Description": description,
                    "Phone": phone,
                    "CallbackURL": f"{domain}/ads/verify-payment/?subscription_plan_id={subscription_id}&user_id={self.request.user.id}",
                }
                # return Response(data)
                response = self.send_request(data)
                logger.info(response)
                if response['status']:
                    return Response({"url": response['url'], "authority": response['authority']})
                else:
                    return Response({"error": "Payment request failed", "code": response['code']}, status=400)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, "message": 'مشکلی پیش آمده لطفا با پشتیبانی تماس بگیرید'},
                            status=status.HTTP_400_BAD_REQUEST)

    def send_request(self, data):
        headers = {'content-type': 'application/json', 'content-length': str(len(json.dumps(data)))}
        try:
            response = requests.post(ZP_API_REQUEST, data=json.dumps(data), headers=headers, timeout=10)
            logger.info(ZP_API_REQUEST)
            if response.status_code == 200:
                response = response.json()
                if response['Status'] == 100:
                    return {'status': True, 'url': ZP_API_STARTPAY + str(response['Authority']),
                            'authority': response['Authority']}
                else:
                    return {'status': False, 'code': str(response['Status'])}
            return {'status': False, 'code': 'invalid response'}
        except requests.exceptions.Timeout:
            return {'status': False, 'code': 'timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': False, 'code': 'connection error'}


@extend_schema(tags=['Subscription & Payments'])
class ZarinpalPaymentVerifyView(APIView):

    def get(self, request):
        """callback url for zarin pall"""
        authority = request.GET.get('Authority')
        subscription_id = request.GET.get('subscription_id')
        transaction_user_id = request.GET.get('user_id')
        transaction_user = User.objects.get(id=transaction_user_id)

        # Validate Subscription Plan ID
        subscription = get_object_or_404(Subscription, id=int(subscription_id))
        subscription_plan = subscription.subscription_plan
        amount = subscription_plan.price

        # Prepare data for verification request
        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": amount,
            "Authority": authority,
        }
        headers = {'content-type': 'application/json', 'content-length': str(len(json.dumps(data)))}

        try:
            response = requests.post(ZP_API_VERIFY, data=json.dumps(data), headers=headers, timeout=10)

            if response.status_code == 200:
                response = response.json()
                # Log the transaction
                transaction = TransactionLog.objects.create(
                    subscription=subscription,
                    amount=amount,
                    ref_id=response.get('RefID', ''),
                    status='Success' if response['Status'] == 100 else 'Failed'
                )
                if response['Status'] == 100:
                    # Payment successful, convert user to premium
                    user = transaction_user
                    # update user in database
                    transaction.apply()
                    # todo :should send sms

                    # user.profile.buy_subscription(days=subscription_plan.day,
                    #                               subscription_type=subscription_plan.type)
                    # send_sms(message_pay, user.phone_number)
                    return Response({"status": "success", "RefID": response['RefID']})
                else:
                    return Response({"status": "failed", "code": response['Status']},
                                    status=status.HTTP_400_BAD_REQUEST)

            return Response({"status": "failed", "message": "Invalid response from ZarinPal"},
                            status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.Timeout:
            return Response({"status": "failed", "message": "Request timed out"}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.ConnectionError:
            return Response({"status": "failed", "message": "Connection error"}, status=status.HTTP_400_BAD_REQUEST)


class AdViewSets(viewsets.ModelViewSet):
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
            OpenApiParameter(name='chassis_condition', description='Filter by car chassis_condition.', required=False,
                             type=str),
            OpenApiParameter(name='payload_capacity ',
                             description='Filter by car payload_capacity.( this argument is required only for heavy weight machins)',
                             required=False,
                             type=str),
            OpenApiParameter(name='weight',
                             description='Filter by car weight( this argument is required only for heavy weight machins)',
                             required=False, type=str),
            OpenApiParameter(name='wheel_number',
                             description='Filter by car wheel_number( this argument is required only for heavy weight machins)',
                             required=False, type=str),
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
            OpenApiParameter(name='order_by', description='sort data',
                             required=False, type=str,
                             examples=[
                                 OpenApiExample(
                                     'Example 1',
                                     summary='sort bu newest',
                                     description='it will sort data from newest',
                                     value="جدیدترین"
                                 ), OpenApiExample(
                                     'Example 2',
                                     summary='sort bu oldest',
                                     description='it will sort data from oldest',
                                     value="قدیمی ترین"
                                 ), OpenApiExample(
                                     'Example 3',
                                     summary='sort bu highest_price',
                                     description='it will sort data from newest',
                                     value="گران ترین"
                                 ),
                                 OpenApiExample(
                                     'Example 4',
                                     summary='sort bu lowest_price',
                                     description='it will sort data from lowest_price',
                                     value="ارزان ترین"
                                 ),
                                 OpenApiExample(
                                     'Example 5',
                                     summary='sort bu kilometer(low to high)',
                                     description='it will sort data from kilometer(low to high)',
                                     value="کم کار کرده ترین"
                                 ), OpenApiExample(
                                     'Example 6',
                                     summary='sort bu kilometer(high to low )',
                                     description='it will sort data from kilometer(high to low )',
                                     value='زیاد کار رده ترین'
                                 ), OpenApiExample(
                                     'Example 7',
                                     summary='sort bu year(new to old)',
                                     description='it will sort data from year(new to old)',
                                     value="نو ترین"
                                 ),
                                 OpenApiExample(
                                     'Example 8',
                                     summary='sort bu year(old to new )',
                                     description='it will sort data from year(old to new )',
                                     value="کهنه ترین"
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
        queryset = self.get_queryset().select_related('user__profile', 'brand', 'model').prefetch_related('images',
                                                                                                          'features')

        # Filter by city if not provided and user is authenticated
        city = request.query_params.get('city') or (request.user.is_authenticated and request.user.profile.city)
        if city and city != "همه شهر ها":
            queryset = queryset.filter(city=city)

        # Order by specified parameter
        order_by = {
            'جدیدترین': '-created_at',
            'قدیمی ترین': 'created_at',
            'گران ترین': '-price',
            'ارزان ترین': 'price',
            'کم کار کرده ترین': 'kilometer',
            'زیاد کار رفته ترین': '-kilometer',
            'نو ترین': '-year',
            'کهنه ترین': 'year',
        }.get(request.query_params.get('order_by'), '-created_at')

        queryset = queryset.order_by(order_by)
        filtered_queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(filtered_queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        description="""
    **Required Fields:**

    * `user` (ForeignKey): This field links the ad to the registered user who is submitting it.
    * `description` (TextField): Provide a detailed description of the car, highlighting its features and condition.
    * `price` (PositiveIntegerField): Enter the asking price of the car.
    * `is_negotiable` (BooleanField): Indicate whether the price is negotiable (default: True).
    * `city` (CharField, choices=PROVINCES): Select the city where the car is located from the provided choices.
    * `car_type` (CharField, choices=CAR_TYPE_CHOICES): Choose the type of car (e.g., Passenger Car, Heavy Machinery).
    * `year` (PositiveIntegerField): Specify the year the car was manufactured.
    * `kilometer` (PositiveIntegerField): Enter the car's current mileage.
    * `fuel_type` (CharField, choices=FUEL_TYPE_CHOICES): Select the car's fuel type (e.g., Gasoline, Diesel).
    * `phone_numbers` (CharField, max_length=12): Provide your phone number(s) for potential buyers to contact you.
    * `address` (CharField, max_length=255): Enter the car's location (optional, but recommended for serious inquiries).

    **Optional Fields:**

    * `exhibition` (ForeignKey, null=True, blank=True): Link the ad to an exhibition if it's part of one (only applicable for users with "EXHIBITOR" role).
    * `brand` (ForeignKey, null=True, blank=True): Specify the car's brand (e.g., Toyota, Honda).
    * `model` (ForeignKey, null=True, blank=True): If known, enter the car's specific model (e.g., Camry, Accord).
    * `promoted_model` (CharField, max_length=255, null=True, blank=True): Provide a custom model name if the brand and model are unknown.
    * `body_type` (CharField, choices=BODY_TYPE_CHOICES): Select the car's body type (e.g., Sedan, SUV).
    * `color` (CharField, max_length=255, null=True, blank=True): Indicate the car's exterior color.
    * `color_description` (TextField, blank=True, null=True): If the body condition is "رنگ شدگی" (painted), provide details about the paint job.
    * `transmission` (CharField, choices=TRANSMISSION_CHOICES): Specify the car's transmission type (applicable to Passenger Cars).
    * `body_condition` (CharField, choices=BODY_CONDITION_CHOICES): Choose the condition of the car's body.
    * `chassis_condition` (CharField, choices=CHASSIS_CONDITION_CHOICES): Select the condition of the car's chassis (default: "سالم" - healthy).
    * `weight` (IntegerField, null=True, blank=True): Enter the weight of the car (applicable to Heavy Machinery).
    * `payload_capacity` (IntegerField, null=True, blank=True): Specify the maximum weight the car can carry (applicable to Heavy Machinery).
    * `wheel_number` (SmallIntegerField, default=4): Indicate the number of wheels (default: 4).

    **Validation Rules:**



    * Color Description: If the body condition is "رنگ شدگی" (painted), then `color_description` must be provided.
    * Exhibition: Only users with the "EXHIBITOR" role can link their ads to an exhibition.
    * Brand/Model or Promoted Model: At least one of brand, model, or promoted_model must be filled.
    * Number of Active Ads (Non-EXHIBITOR Users): A user can have a maximum of 3 active car ads if they don't have the "EXHIBITOR" role.
    * Heavy Machinery Fields: If `car_type` is "ماشین‌آلات سنگین" (Heavy Machinery), then `weight`, `payload_capacity`, and `wheel_number` must be provided.
    * A user can only have one pending ad at a time. If a user tries to submit another ad while they already have one pending ad, they will receive a 406 error code.
    """,
    )
    def create(self, request, **kwargs):
        serializer = AdSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data["user"] = request.user
            serializer.save()
            return Response({'success': True, "message": serializer.data},
                            status.HTTP_201_CREATED)

    @extend_schema(
        description="Search for ads based on various filters.",
        parameters=[
            OpenApiParameter(name='brand', description='Filter by car brand.', required=False, type=str),
            OpenApiParameter(name='model', description='Filter by car model.', required=False, type=str),
            OpenApiParameter(name='color', description='Filter by car color', required=False, type=str),
            OpenApiParameter(name='transmission', description='Filter by car transmission', required=False, type=str),
            OpenApiParameter(name='body_condition', description='Filter by car body_condition', required=False,
                             type=str),
            OpenApiParameter(name='chassis_condition', description='Filter by car chassis_condition.', required=False,
                             type=str),
            OpenApiParameter(name='payload_capacity ',
                             description='Filter by car payload_capacity.( this argument is required only for heavy weight machins)',
                             required=False,
                             type=str),
            OpenApiParameter(name='weight',
                             description='Filter by car weight( this argument is required only for heavy weight machins)',
                             required=False, type=str),
            OpenApiParameter(name='wheel_number',
                             description='Filter by car wheel_number( this argument is required only for heavy weight machins)',
                             required=False, type=str),
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
            raise CustomValidationError({'q': 'No query provided.'})

        queryset = CarIndex.objects.filter(text__icontains=query)
        car_ids = [obj.pk for obj in queryset]
        cars = self.queryset.filter(pk__in=car_ids)
        filter_set = CarFilter(request.GET, queryset=cars)

        # Apply additional filters
        filtered_cars = filter_set.qs

        # Paginate filtered results
        result = self.paginate_queryset(filtered_cars)
        serializer = AdSerializer(result, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=['Exhibitions']),
    retrieve=extend_schema(tags=['Exhibitions']),
    create=extend_schema(tags=['Exhibitions']),
    update=extend_schema(tags=['Exhibitions']),
    partial_update=extend_schema(tags=['Exhibitions']),
    destroy=extend_schema(tags=['Exhibitions']),
    search=extend_schema(tags=['Exhibitions']),
)
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
        if serializer.is_valid(raise_exception=True):
            serializer.update(instance=instance, validated_data=serializer.validated_data)
            return Response({'success': True, "message": " your exhibition updated"}, status.HTTP_200_OK)

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
            OpenApiParameter(name='sells_chinese_cars', description='Filter by exhibitions selling Chinese cars.',
                             required=False, type=bool),
            OpenApiParameter(name='sells_foreign_cars', description='Filter by exhibitions selling foreign cars.',
                             required=False, type=bool),
            OpenApiParameter(name='sells_domestic_cars', description='Filter by exhibitions selling domestic cars.',
                             required=False, type=bool),

        ],

    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        filter_set = ExhibitionFilter(request.GET, queryset=queryset, )
        filtered_queryset = filter_set.qs
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(filtered_queryset, many=True, context={"request": request})
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
            raise CustomValidationError({'q': 'No query provided.'})

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


class LatestVideosList(generics.ListAPIView):
    queryset = ExhibitionVideo.objects.all().order_by('-uploaded_at')
    serializer_class = ExhibitionVideoSerializer


@extend_schema_view(
    list=extend_schema(tags=['Exhibitions']),
    retrieve=extend_schema(tags=['Exhibitions']),
    update=extend_schema(tags=['Exhibitions']),
    create=extend_schema(tags=['Exhibitions']),
    partial_update=extend_schema(tags=['Exhibitions']),
    destroy=extend_schema(tags=['Exhibitions']),

)
class ExhibitionVideoViewSet(viewsets.ModelViewSet):
    queryset = ExhibitionVideo.objects.all()
    serializer_class = ExhibitionVideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        exhibition_id = self.kwargs.get('exhibition_pk')
        if exhibition_id:
            return self.queryset.filter(exhibition_id=exhibition_id)
        return self.queryset

    def create(self, request, *args, **kwargs):
        exhibition_id = self.kwargs.get('exhibition_pk')
        if not Exhibition.objects.filter(id=exhibition_id).exists():
            return Response({"success": False, 'message': 'Exhibition not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exhibition = Exhibition.objects.get(id=exhibition_id)
        serializer.save(exhibition=exhibition)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfCar]

    def get_queryset(self):
        car_id = self.kwargs.get('car_pk')
        if car_id:
            return self.queryset.filter(ad_id=car_id)
        return self.queryset

    # def create(self, request, *args, **kwargs):
    #     car_id = self.kwargs.get('car_pk')
    #     car = Car.objects.filter(id=car_id)
    #
    #     if not car.exists():
    #         return Response({"success": False, 'message': 'اگهی پیدا نشد'}, status=status.HTTP_404_NOT_FOUND)
    #     if car.first().user != request.user:
    #         return Response({"success": False, "error": " شما مجاز به انجام این کار نیستید"},
    #                         status=status.HTTP_403_FORBIDDEN)
    #
    #     request.data['ad'] = car_id
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        car_id = self.kwargs.get('car_pk')
        car = Car.objects.filter(id=car_id)

        if not car.exists():
            return Response({"success": False, 'message': 'اگهی پیدا نشد'}, status=status.HTTP_404_NOT_FOUND)

        if car.first().user != request.user:
            return Response({"success": False, "error": " شما مجاز به انجام این کار نیستید"},
                            status=status.HTTP_403_FORBIDDEN)

        if 'images' not in request.FILES:
            return Response({"success": False, "error": "کلید 'images' یافت نشد."},
                            status=status.HTTP_400_BAD_REQUEST)

        images = request.FILES.getlist('images')  # لیست تصاویر

        if not images:
            return Response({"success": False, "error": "هیچ تصویری ارسال نشده است."},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(images) > 6:
            return Response({"success": False, "error": "شما فقط می‌توانید تا سقف ۶ عکس آپلود کنید"},
                            status=status.HTTP_400_BAD_REQUEST)

        created_images = []
        for image in images:
            if not image.content_type.startswith('image/'):
                return Response({"success": False,
                                 "error": f"فایل '{image.name}' معتبر نیست. لطفا فقط فایل‌های تصویری ارسال کنید."},
                                status=status.HTTP_400_BAD_REQUEST)

            data = {
                'ad': car_id,
                'image': image
            }
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            created_images.append(serializer.data)

        return Response({"success": True, "images": created_images}, status=status.HTTP_201_CREATED)


class BrandModelsView(APIView):
    @extend_schema(
        description="get models from brands example ,you should enter a json with "
                    "a key of 'brands' that get a list of brands ",
        request={
            "application/json": {
                "type": "object",
            },
        }, )
    def post(self, request):
        brands = request.data.get('brands', [])
        queryset = CarModel.objects.filter(brand__name__in=brands)
        serializer = CarModelSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BrandListView(generics.ListAPIView):
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CarPriceStatsView(APIView):

    def get(self, request, format=None):
        min_price = Car.objects.aggregate(Min('price'))['price__min']
        max_price = Car.objects.aggregate(Max('price'))['price__max']
        return Response({'min_price': min_price, 'max_price': max_price}, status=status.HTTP_200_OK)


class SelectedBrandListView(APIView):
    def get(self, request, parent, *args, **kwargs):
        brands = Brand.objects.filter(selected_brand__parent=parent)
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckSubmitAddAuthorization(APIView):
    """check user authorization for submit add"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if not user.roles == "EXHIBITOR":
            if user.cars.filter(status="active").count() >= 3 and user.extra_ads < 1:
                raise CustomValidationError({
                    '': "شما نمیتوانید بیشتر از سه ماشین ثبت کنید"})
        if user.cars.filter(status="pending").exists():
            raise CustomValidationError(
                {
                    '': "درخواست شما  در حال برسی است تا مشخص شدن وضعیت درخواست شما اجازه ثبت اگهی دیگری ندارید"})
        return Response({"success": True, "message": "authorized"}, status=status.HTTP_202_ACCEPTED)


@extend_schema_view(
    add_to_favorites=extend_schema(tags=['Favorites']),
    remove_from_favorites=extend_schema(tags=['Favorites']),
    list_favorites=extend_schema(tags=['Favorites']),
)
class FavoriteViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='add')
    def add_to_favorites(self, request, pk=None):
        """add car to favorite"""
        user = request.user
        car = get_object_or_404(Car, pk=pk)
        favorite, created = Favorite.objects.get_or_create(user=user, car=car)
        if created:
            return Response({"success": True, "message": "آگهی به لیست علاقه‌مندی‌ها اضافه شد."},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "message": "این آگهی قبلاً در لیست علاقه‌مندی‌ها موجود بود."},
                            status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='remove')
    def remove_from_favorites(self, request, pk=None):
        """remove car from favorite"""
        user = request.user
        favorite = get_object_or_404(Favorite, user=user, car_id=pk)
        favorite.delete()
        return Response({"success": True, "message": "آگهی از لیست علاقه‌مندی‌ها حذف شد."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='list')
    def list_favorites(self, request):
        """list of favorite ads of users"""
        user = request.user
        favorites = Favorite.objects.filter(user=user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RenewAd(APIView):
    """an api for renew ad one month more"""

    def get(self, request, id, *args, **kwargs):
        car = get_object_or_404(Car, pk=id)
        if car.user == request.user:
            car.renew()
            return Response({"success": True, "message": 'اگهی با موفقیت تمدید شد'})
        else:
            raise PermissionDenied


class ColorListView(generics.ListAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(name='type', description='Filter brands  by type.', required=True, type=str),

    ],

)
class BrandByTypeAPIView(APIView):
    """get brands base on body type"""

    def get(self, request, *args, **kwargs):
        brand_type = request.query_params.get('type')
        if not brand_type:
            return Response({"success": False, "message": "نوع ماشین اجباری است"}, status=status.HTTP_400_BAD_REQUEST)

        brands = Brand.objects.filter(type=brand_type)
        if not brands.exists():
            return Response({"success": False, "message": "هیچ برندی با نوع ماشینی که شما دادید یافت نشد"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Subscription & Payments'])
class SubscriptionPlansListView(generics.ListAPIView):
    """ get a list of all subscription plans """
    queryset = SubscriptionPlans.objects.all()
    serializer_class = SubscriptionPlansSerializer


@extend_schema(tags=['Subscription & Payments'])
class SubscriptionCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionCreateSerializer

    def post(self, request):
        """create a subscription for user with ad and sub pan and return it """
        user = request.user
        serializer = SubscriptionCreateSerializer(data=request.data)

        if serializer.is_valid():
            subscription = serializer.save(user=user)
            response_serializer = SubscriptionSerializer(subscription)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
