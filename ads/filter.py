from django_filters import FilterSet, CharFilter, RangeFilter
from ads.models import Car, Exhibition
import django_filters
from django_filters import FilterSet, CharFilter, RangeFilter, BaseInFilter, NumberFilter


class CharInFilter(BaseInFilter, CharFilter):
    pass


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class CarFilter(FilterSet):
    brand = CharInFilter(field_name='brand__name', lookup_expr='in')
    model = CharInFilter(field_name='model__title', lookup_expr='in')
    price = RangeFilter()
    kilometer = RangeFilter()
    year = RangeFilter()
    city = CharInFilter(field_name='city', lookup_expr='in')
    fuel_type = CharInFilter(field_name='fuel_type', lookup_expr='in')
    body_condition = CharInFilter(field_name='body_condition', lookup_expr='in')
    transmission = CharInFilter(field_name='transmission', lookup_expr='in')
    color = CharInFilter(field_name='color', lookup_expr='in')
    body_type = CharInFilter(field_name='body_type', lookup_expr='in')
    car_type = CharInFilter(field_name='car_type', lookup_expr='in')
    chassis_condition = CharInFilter(field_name='chassis_condition', lookup_expr='in')
    sale_or_rent = CharInFilter(field_name='sale_or_rent', lookup_expr='in')
    upholstery_condition = CharInFilter(field_name='upholstery_condition', lookup_expr='in')
    tire_condition = CharInFilter(field_name='tire_condition', lookup_expr='in')

    class Meta:
        model = Car
        fields = ['brand', 'city', 'model', 'price', 'kilometer', 'year', 'fuel_type', 'body_condition', 'transmission',
                  'color', 'body_type', 'car_type', 'chassis_condition', 'sale_or_rent', 'upholstery_condition',
                  'tire_condition']


class ExhibitionFilter(FilterSet):
    city = CharInFilter(field_name='city', lookup_expr='in')

    class Meta:
        model = Exhibition
        fields = ["city", "sells_chinese_cars", "sells_foreign_cars", "sells_domestic_cars"]
