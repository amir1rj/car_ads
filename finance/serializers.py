from rest_framework import serializers

from finance.models import SubscriptionPlans, Subscription


class ZarinpalPaymentRequestSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=255, required=True, help_text="Description of the transaction.")
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True,
                                  help_text="User's phone number (optional).")
    subscription_id = serializers.IntegerField(required=True, help_text="ID of the Subscription.")

    def validate_subscription_plan_id(self, value):
        try:
            subscription_plan = SubscriptionPlans.objects.get(id=value)
        except SubscriptionPlans.DoesNotExist:
            raise serializers.ValidationError("Subscription Plan with this ID does not exist.")
        return value


class SubscriptionPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlans
        fields = ['id', 'type', "amount", "price", 'name', 'description']


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['ad', 'subscription_plan']


class SubscriptionSerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlansSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'ad', 'subscription_plan']
