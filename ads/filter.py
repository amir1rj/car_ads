from django_filters import FilterSet, CharFilter, NumberFilter, RangeFilter
from ads.models import Car


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
        fields = ['brand', 'model', 'price', 'kilometer', 'year',"fuel_type","body_condition","transmission","color"]
