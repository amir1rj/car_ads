from rest_framework import serializers

from ads.models import Car, Image, Feature, Brand, CarModel


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class CarModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        fields = "__all__"


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("id", "title", "image")


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ("id", "name")


class AdSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=False, required=False)
    features = FeatureSerializer(many=True, read_only=False, required=False)
    user = serializers.SlugRelatedField("username", read_only=True)
    brand = serializers.CharField(max_length=255)
    model = serializers.CharField(max_length=255)

    class Meta:
        model = Car
        fields = "__all__"

    def get_images(self, obj):
        serializer = ImageSerializer(instance=obj.images.all(), many=True, )
        return serializer.data

    def get_features(self, obj):
        serializer = FeatureSerializer(instance=obj.features.all(), many=True, )
        return serializer.data

    def create(self, validated_data):
        brand = Brand.objects.get(name=validated_data['brand'])
        model = CarModel.objects.get(title=validated_data['model'], brand=brand)
        validated_data['brand'], validated_data["model"] = brand, model
        request = self.context["request"]
        if request.user.is_authenticated:
            validated_data["user"] = request.user
        images_data = validated_data.pop('images', [])
        features_data = validated_data.pop('features', [])

        car = Car.objects.create(**validated_data)

        for image_data in images_data:
            Image.objects.create(ad=car, **image_data)

        for feature in features_data:
            Feature.objects.create(car=car, **feature)
        return car

    def update(self, instance, validated_data):
        brand = Brand.objects.get(name=validated_data['brand'])
        model = CarModel.objects.get(title=validated_data['model'], brand=brand)
        validated_data['brand'], validated_data["model"] = brand, model
        request = self.context["request"]
        if request.user.is_authenticated:
            validated_data["user"] = request.user

        images_data = validated_data.pop('images', [])
        features_data = validated_data.pop('features', [])

        instance = super().update(instance, validated_data)

        for image_data in images_data:
            Image.objects.update_or_create(ad=instance, **image_data)

        for feature_data in features_data:
            Feature.objects.update_or_create(car=instance, **feature_data)

        return instance
