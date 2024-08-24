from rest_framework import serializers
from ads.models import Car, Image, Feature, Brand, CarModel, ExhibitionVideo, Exhibition, SelectedBrand
from ads.utils import is_not_mobile_phone
from rest_framework import exceptions


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class SelectedBrandSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()

    class Meta:
        model = SelectedBrand
        fields = ['parent', 'brand']


class CarModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        fields = "__all__"


class AdImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("id", "image")


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ("id", "name")


class ExhibitionSerializerReadOnly(serializers.ModelSerializer):
    class Meta:
        model = Exhibition
        fields = ['company_name']


class ExhibitionVideoSerializerReadOnly(serializers.ModelSerializer):
    class Meta:
        model = ExhibitionVideo
        exclude = ["exhibition"]


class ExhibitionVideoSerializer(serializers.ModelSerializer):
    exhibition = ExhibitionSerializerReadOnly(read_only=True)

    class Meta:
        model = ExhibitionVideo
        fields = '__all__'


class AdSerializer(serializers.ModelSerializer):
    # autocomplete = serializers.SerializerMethodField()
    images = AdImageSerializer(many=True, read_only=False, required=False)
    features = FeatureSerializer(many=True, read_only=False, required=False)
    user = serializers.SlugRelatedField("username", read_only=True)
    brand = serializers.CharField(max_length=255)
    model = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(source='user.profile.email', read_only=True)

    class Meta:
        model = Car
        fields = "__all__"

    def get_images(self, obj):
        serializer = AdImageSerializer(instance=obj.images.all(), many=True, )
        return serializer.data

    # def get_autocomplete(self, obj):
    #     return CarIndex.prepare_autocomplete(obj)

    def get_features(self, obj):
        serializer = FeatureSerializer(instance=obj.features.all(), many=True, )
        return serializer.data

    def create(self, validated_data):
        if not validated_data.get("model") and not validated_data.get("promoted_model"):
            raise serializers.ValidationError({"model": "This field is required."})
        brand = Brand.objects.get(name=validated_data.get('brand'))
        if validated_data.get("model"):
            model = CarModel.objects.get(title=validated_data.get('model'), brand=brand)
            validated_data["model"] = model
        validated_data['brand'] = brand
        request = self.context["request"]
        if request.user.is_authenticated:
            validated_data["user"] = request.user
        else:
            raise exceptions.AuthenticationFailed("anonymous user is not allowed to create a new add")
        images_data = validated_data.pop('images', [])
        features_data = validated_data.pop('features', [])
        if not validated_data["user"].roles == "EXHIBITOR":
            if validated_data["user"].cars.filter(status="active").count() >= 3:
                raise serializers.ValidationError("you can not have more than 3 ads")

        if validated_data["user"].cars.filter(status="pending").exists():
            raise exceptions.NotAcceptable(
                "Your request is being reviewed. you cant submit another ads until your current one is registered")
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
    videos = ExhibitionVideoSerializerReadOnly(many=True, read_only=False, required=False)
    user = serializers.SlugRelatedField("username", read_only=True)
    cars = serializers.SerializerMethodField(read_only=True, required=False)

    class Meta:
        model = Exhibition
        fields = "__all__"

    def validate_contact_phone(self, value):
        """
        Validates a comma-separated list of Iranian static phone numbers.
        """
        if value:
            phones = value.split(",")
            validated_phones = []
            for phone in phones:
                phone = is_not_mobile_phone(phone.strip())  # Remove leading/trailing whitespaces
                if not phone.isdigit():
                    raise serializers.ValidationError(
                        f"you should only enter numbers not{phone}. (e.g., 2122334567)")
                # Mobile number check (optional, can be removed if not needed)

                validated_phones.append(phone)
            return validated_phones  # Return a list of validated phone numbers
        return value  # Allow empty static_phones

    def validate(self, attrs):
        name = attrs.get('company_name')
        if name is not None:
            if Exhibition.objects.filter(company_name=name).exists():
                raise serializers.ValidationError("your company name is already exists")
        return attrs

    def create(self, validated_data):
        validated_data['contact_phone'] = ", ".join(validated_data['contact_phone'])  # Join back for storage
        videos_data = validated_data.pop('videos', [])
        user = self.context["request"].user

        if user.is_authenticated and user.roles == "EXHIBITOR":
            validated_data["user"] = user
            exhibition = Exhibition.objects.create(**validated_data)
            for video in videos_data:
                ExhibitionVideo.objects.create(exhibition=exhibition, **video)
        else:
            raise exceptions.PermissionDenied("شما دسترسی ثبت نمایشگاه را ندارید")
        return exhibition

    def update(self, instance, validated_data):
        validated_data['contact_phone'] = ", ".join(validated_data['contact_phone'])  # Join back for storage
        request = self.context["request"]
        if request.user.is_authenticated:
            validated_data["user"] = request.user
        videos_data = validated_data.pop('videos', [])
        instance = super().update(instance, validated_data)
        for video in videos_data:
            ExhibitionVideo.objects.update_or_create(exhibition=instance, **video)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        method = request.resolver_match.url_name
        if method in ['exhibition-list', "exhibition-search"]:
            representation.pop('videos')
            representation.pop('cars')
        return representation

    def get_videos(self, obj):
        serializer = ExhibitionVideoSerializerReadOnly(instance=obj.videos.all(), many=True, )
        return serializer.data

    def get_cars(self, obj):
        car_serializer = AdSerializer(instance=obj.cars.filter(status="active"), many=True)
        return car_serializer.data
