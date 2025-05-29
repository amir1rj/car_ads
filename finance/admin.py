from django.contrib import admin

from finance.models import SubscriptionPlans


# Register your models here.
@admin.register(SubscriptionPlans)
class SubscriptionPlansAdmin(admin.ModelAdmin):
    list_display = ["type", 'name']
