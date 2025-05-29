from django.urls import path

from finance.views import ZarinpalPaymentView, SubscriptionPlansListView, ZarinpalPaymentVerifyView, \
    SubscriptionCreateView

urlpatterns = [
    path('payment/', ZarinpalPaymentView.as_view(), name='zarinpal_payment'),
    path('subscription-plans/', SubscriptionPlansListView.as_view(), name='subscription-plans-list'),
    path('subscription-create/', SubscriptionCreateView.as_view(), name='subscription-create'),
    path('verify-payment', ZarinpalPaymentVerifyView.as_view(), name='zarinpal_payment_verify'),
]
