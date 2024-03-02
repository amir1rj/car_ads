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

    @staticmethod
    def prepare_autocomplete(obj):
        return fix_text(" ".join((obj.description, obj.brand.name, obj.model.title,)))

    def prepare_text(self, obj):
        return ' '.join([
            obj.description,
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
