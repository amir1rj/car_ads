from django.contrib import admin
from .models import Car, Image, Feature, SubscriptionPlans, Brand, CarModel, ExhibitionVideo, Exhibition, SelectedBrand, \
    Color
from .tasks import toggle_ad_status


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1


class VideoInline(admin.StackedInline):
    model = ExhibitionVideo
    extra = 1


admin.site.register(Color)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 'price', "created_at",
        'is_promoted', 'status', "view_count", "created_at",
    ]
    list_filter = ['is_promoted', 'status', 'fuel_type']
    search_fields = ['year', 'description']
    inlines = [ImageInline, FeatureInline]
    list_editable = ["is_promoted", "status", ]
    actions = ["make_ads_active", "make_ads_inactive"]
    fieldsets = (
        ('اطلاعات کلی اگهی', {
            'fields': (
                'user', 'exhibition', 'description', 'price', 'is_negotiable', 'city', 'sale_or_rent')
        }),
        ('اطلاعات خودرو', {
            'fields': ('brand', 'model', 'promoted_model', 'year', 'kilometer', 'body_type', 'suggested_color', 'color',
                       'fuel_type', 'upholstery_condition', 'tire_condition', "insurance")
        }),
        ('ماشین سواری', {
            'fields': ('transmission', 'body_condition', 'front_chassis_condition', 'behind_chassis_condition')
        }),
        ('ماشین سنگین (اختیاری)', {
            'fields': ('weight', 'payload_capacity', 'wheel_number')
        }),
        ('اطلاعات تماس', {
            'fields': ('phone_numbers', 'address')
        }),
        ('وضعیت اگهی', {
            'fields': ('status', 'is_urgent', 'is_promoted', 'view_count')
        }),
    )

    @admin.action(description="فعال کردن خودروهای انتخاب شده")
    def make_ads_active(self, request, queryset):
        ad_ids = list(queryset.values_list('id', flat=True))
        toggle_ad_status.delay(ad_ids, 'active')

    @admin.action(description="غیرفعال کردن خودروهای انتخاب شده")
    def make_ads_inactive(self, request, queryset):
        ad_ids = list(queryset.values_list('id', flat=True))
        toggle_ad_status.delay(ad_ids, 'inactive')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ["title", "brand"]


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ["company_name", "user", "city", "view_count", ]
    list_filter = ['city']
    search_fields = ["company_name", "user", "address"]
    inlines = [VideoInline]


class SelectedBrandAdmin(admin.ModelAdmin):
    list_display = ('brand', 'parent')
    search_fields = ('parent', 'brand__name')
    list_filter = ('parent', 'brand')


admin.site.register(SelectedBrand, SelectedBrandAdmin)


@admin.register(SubscriptionPlans)
class SubscriptionPlansAdmin(admin.ModelAdmin):
    list_display = ["type",'name']
