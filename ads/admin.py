from django.contrib import admin
from .models import Car, Image, Feature, Brand, CarModel, ExhibitionVideo, Exhibition


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1


class VideoInline(admin.StackedInline):
    model = ExhibitionVideo
    extra = 1


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = [
        'brand','model','price',"created_at",
        'is_promoted','status',"view_count","created_at",
    ]
    list_filter = ['brand', 'model', 'fuel_type', 'status']
    search_fields = ['year', 'description', ]
    inlines = [ImageInline, FeatureInline]
    list_editable = ["is_promoted", "status",]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ["title", "brand"]


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ["company_name","user","city","view_count",]
    list_filter = ['city']
    search_fields = ["company_name","user","address"]
    inlines = [VideoInline]

