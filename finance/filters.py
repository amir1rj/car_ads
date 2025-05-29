from finance.models import SubscriptionPlans
from django_filters import FilterSet


class SubscriptionPlansFilter(FilterSet):
    class Meta:
        model = SubscriptionPlans
        fields = ['type']
