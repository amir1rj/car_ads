from haystack import indexes
from .models import Car, Exhibition
from ftfy import fix_text


class CarIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    brand = indexes.CharField(model_attr='brand__name')
    model = indexes.CharField(model_attr='model__title')
    autocomplete = indexes.EdgeNgramField()

    def get_model(self):
        return Car

    def prepare_text(self, obj):
        # Check if model or brand is None
        if obj.model is None or obj.brand is None:
            return None

        # Provide a fallback for description if it's None or empty
        description = obj.description if obj.description else ''

        return ' '.join([
            description,
            obj.brand.name,
            obj.model.title,
        ])


class ExhibitionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)

    def get_model(self):
        return Exhibition

    def prepare_text(self, obj):
        return ' '.join([
            obj.description,
            obj.company_name,

        ])
