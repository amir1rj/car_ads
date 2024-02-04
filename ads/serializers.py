from rest_framework import serializers

from ads.models import Car, Image, Feature


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("id", "title", "image")


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ("id", "name")


class AdSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True, required=False)
    features = FeatureSerializer(many=True, read_only=True, required=False)
    seller = serializers.SlugRelatedField("username", read_only=True)

    class Meta:
        model = Car
        fields = "__all__"

    def get_images(self, obj):
        serializer = ImageSerializer(instance=obj.images.all(), many=True, )
        return serializer.data

    def get_features(self, obj):
        serializer = FeatureSerializer(instance=obj.features.all(), many=True, )
        return serializer.data
