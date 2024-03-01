from rest_framework import serializers
from ads.models import Car, Image, Feature, Brand, CarModel, ExhibitionVideo, Exhibition


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
        fields = ("id", "image")


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ("id", "name")


class ExhibitionVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExhibitionVideo
        exclude = ["exhibition"]


class AdSerializer(serializers.ModelSerializer):
    # autocomplete = serializers.SerializerMethodField()
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

    # def get_autocomplete(self, obj):
    #     return CarIndex.prepare_autocomplete(obj)

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


class ExhibitionSerializer(serializers.ModelSerializer):
    videos = ExhibitionVideoSerializer(many=True, read_only=False, required=False)
    user = serializers.SlugRelatedField("username", read_only=True)

    class Meta:
        model = Exhibition
        fields = "__all__"

    def create(self, validated_data):
        print(validated_data)
        videos_data = validated_data.pop('videos', [])
        user = self.context["request"].user
        print(user)
        if user.is_authenticated and user.roles == "EXHIBITOR":
            validated_data["user"] = user
            exhibition = Exhibition.objects.create(**validated_data)
            print(videos_data)
            for video in videos_data:
                ExhibitionVideo.objects.create(exhibition=exhibition, **video)
        else:
            raise serializers.ValidationError("شما دسترسی ثبت نمایشگاه را ندارید")
        return exhibition

    def update(self, instance, validated_data):
        request = self.context["request"]
        if request.user.is_authenticated:
            validated_data["user"] = request.user
        videos_data = validated_data.pop('videos', [])
        instance = super().update(instance, validated_data)
        for video in videos_data:
            ExhibitionVideo.objects.update_or_create(exhibition=instance, **video)
        return instance

    def get_videos(self, obj):
        serializer = ExhibitionVideoSerializer(instance=obj.videos.all(), many=True, )
        return serializer.data
