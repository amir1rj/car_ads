from django.contrib import admin
from .models import Car, Image, Feature, Brand, CarModel


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'brand',
        'model',
        'price',
        "created_at",
        'is_promoted',
    ]
    list_filter = ['brand', 'model', 'year', 'fuel_type', 'status']
    search_fields = ['title', 'description', 'brand__name', 'model']
    readonly_fields = ['vin', 'inspection_date']
    inlines = [ImageInline, FeatureInline]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ["title", "brand"]

