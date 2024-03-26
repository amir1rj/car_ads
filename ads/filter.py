from django_filters import FilterSet, CharFilter, RangeFilter
from ads.models import Car, Exhibition


class CarFilter(FilterSet):
    brand = CharFilter(field_name='brand__name')
    model = CharFilter(field_name='model__name')
    # فیلتر بازه قیمت
    price = RangeFilter()
    # فیلتر بازه کارکرد
    kilometer = RangeFilter()
    # فیلتر بازه سال تولید
    year = RangeFilter()

    class Meta:
        model = Car
        fields = ['brand', "city", 'model', 'price', 'kilometer', 'year', "fuel_type", "body_condition", "transmission",
                  "color", "body_type", "car_type", 'chassis_condition', "weight",
                  "payload_capacity", "wheel_number"]


class ExhibitionFilter(FilterSet):
    class Meta:
        model = Exhibition
        fields = ["city"]
