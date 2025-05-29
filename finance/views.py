import json

import requests
from django.shortcuts import get_object_or_404
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from account.models import User
from finance.filters import SubscriptionPlansFilter
from finance.models import Subscription, SubscriptionPlans
from finance.serializers import ZarinpalPaymentRequestSerializer, SubscriptionPlansSerializer, \
    SubscriptionCreateSerializer, SubscriptionSerializer
from finance.models import Payment

# Create your views here.

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
                if response['status']:
                    authority = response.get('authority')
                    Payment.objects.create(user=request.user, subscription=subscription, amount=amount,
                                           authority=authority)
                    # todo : should remove authority form this code block
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
        try:
            authority = request.GET.get('Authority')
            payment = get_object_or_404(Payment, authority=authority)
            # Validate Subscription Plan ID
            subscription = payment.subscription
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
                    payment_qs = Payment.objects.filter(id=payment.id)
                    payment_status = 1 if response['Status'] == 100 else 2
                    payment_qs = payment_qs.update(ref_id=response.get('RefID', ''), status=payment_status)
                    if response['Status'] == 100:
                        # Payment successful, convert user to premium
                        user = payment.user
                        # update user in database
                        payment.apply()
                        # todo :should send sms
                        # send_sms(message_pay, user.phone_number)
                        return Response({"status": "success", "RefID": response['RefID']})
                    else:
                        return Response({'success':False, "code": response['Status']},
                                        status=status.HTTP_400_BAD_REQUEST)

                return Response({'success':False, "message": "Invalid response from ZarinPal"},
                                status=status.HTTP_400_BAD_REQUEST)

            except requests.exceptions.Timeout:
                return Response({'success':False, "message": "Request timed out"}, status=status.HTTP_400_BAD_REQUEST)
            except requests.exceptions.ConnectionError:
                return Response({'success':False, "message": "Connection error"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success':False,'message':'مشکلی وجود دارد'})

@extend_schema(tags=['Subscription & Payments'])
class SubscriptionPlansListView(generics.ListAPIView):
    """ get a list of all subscription plans """
    queryset = SubscriptionPlans.objects.all()
    serializer_class = SubscriptionPlansSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SubscriptionPlansFilter


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
