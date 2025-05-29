from rest_framework import serializers
from account.exceptions import CustomValidationError
from account.logging_config import logger
from ads.models import Car, Image, Feature, Brand, CarModel, ExhibitionVideo, Exhibition, SelectedBrand, Favorite, \
    Color
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
    """
    Serializer for car ads (Car model).

    Handles image and feature data, user information, brand and model validation,
    and additional logic for favorite status, posting restrictions, and color selection.
    """
    images = AdImageSerializer(many=True, required=False)
    features = FeatureSerializer(many=True, required=False)
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    brand = serializers.CharField(max_length=255)
    model = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(source='user.profile.email', read_only=True)
    is_favorited = serializers.SerializerMethodField()
    color = serializers.CharField(max_length=255, required=False)  # Color chosen from available colors
    suggested_color = serializers.CharField(max_length=255, required=False)  # User suggested color

    class Meta:
        model = Car
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at', 'view_count', 'is_promoted', 'is_urgent']

    def create(self, validated_data):
        """
        Handle the creation of a car ad, including color validation logic.
        """

        color = validated_data.get("color")
        suggested_color = validated_data.get("suggested_color")

        if color:
            # Check if the selected color exists in the Color table
            color_obj = Color.objects.filter(name=color)
            if not color_obj.exists():
                raise CustomValidationError({"color": "رنگ انتخاب‌شده موجود نیست"})
            else:
                validated_data['color'] = color_obj.first()
        elif not suggested_color:
            raise CustomValidationError({"color": "باید یا رنگ انتخاب‌شده را انتخاب کنید یا رنگ پیشنهادی را وارد کنید"})
        # Fetch brand and model objects
        brand = Brand.objects.get(name=validated_data.get('brand'))
        if validated_data.get("model"):
            model = CarModel.objects.get(title=validated_data.get('model'), brand=brand)
            validated_data["model"] = model

        validated_data['brand'] = brand

        # Ensure the request user is authenticated
        request = self.context["request"]
        if request.user.is_authenticated:
            validated_data["user"] = request.user
        else:
            raise exceptions.AuthenticationFailed("کاربران ناشناس اجازه قبت اگهی ندارند")

        # Process images and features
        images_data = validated_data.pop('images', [])
        features_data = validated_data.pop('features', [])

        # Limit active ads to 3 for non-exhibitor users
        if validated_data["user"].roles != "EXHIBITOR":
            if request.user.cars.filter(status="active").count() >= 3:
                if request.user.extra_ads < 1:
                    raise exceptions.NotAcceptable("شما نمیتوانید بیشتر از سه اگهی ثبت کنید")
                else:
                    request.user.extra_ads -= 1

        # Prevent new ad creation if a pending request exists
        if validated_data["user"].cars.filter(status="pending").exists():
            raise exceptions.NotAcceptable(
                "درخواست شما در حال برسی است و تا مشخص شدن وضعیت اجازه ثبت اگهی دیگری ندارید")

        # Create the car ad
        car = Car.objects.create(**validated_data)

        # Save related images and features
        for image_data in images_data:
            Image.objects.create(ad=car, **image_data)

        for feature in features_data:
            Feature.objects.create(car=car, **feature)

        return car

    def update(self, instance, validated_data):
        """
        Handle updates to the car ad, including color validation logic.
        """
        # Fetch the brand and model objects
        brand = validated_data.get('brand')
        model = validated_data.get('model')

        if brand:

            brand_obj = Brand.objects.filter(name=brand).first()
            if brand_obj:
                validated_data['brand'] = brand_obj
            else:

                raise CustomValidationError({'brand': "برند موجود نیست"})
        else:

            raise CustomValidationError({'brand': "این فیلد اجباری است"})
        if model:

            model_obj = CarModel.objects.filter(title=model).first()

            if model_obj:
                validated_data['model'] = model_obj
            else:
                raise CustomValidationError({'model': "مدل موجود نیست"})
        else:
            raise CustomValidationError({'model': "این فیلد اجباری است"})

        # Validate color selection during update
        color = validated_data.get("color")

        if color:
            # Check if the selected color exists in the Color table
            if not Color.objects.filter(name=color).exists():
                raise CustomValidationError({"color": "رنگ انتخاب‌شده موجود نیست."})

        # Process images and features
        images_data = validated_data.pop('images', [])
        features_data = validated_data.pop('features', [])
        logger.info(validated_data)
        # Update the car instance
        instance = super().update(instance, validated_data)

        # Update or create related images and features
        for image_data in images_data:
            Image.objects.update_or_create(ad=instance, **image_data)
        for feature_data in features_data:
            Feature.objects.update_or_create(car=instance, **feature_data)

        return instance

    def validate(self, attrs):
        if attrs['city'] == "همه شهر ها":
            raise CustomValidationError({'city': "شما باید یک شهر انتخاب کنید "})
        return attrs

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, car=obj).exists()
        return False


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
                    raise CustomValidationError({
                        'contact_phone': f"کاراکتر غیر مجاز شما فقط میتوانید اعداد وارد کنید{phone}. (e.g., 2122334567)"})

                validated_phones.append(phone)
            return validated_phones  # Return a list of validated phone numbers
        return value  # Allow empty static_phones

    def validate(self, attrs):
        name = attrs.get('company_name')
        if name is not None:
            if Exhibition.objects.filter(company_name=name).exists():
                raise CustomValidationError({'company_name': "نام نمایشگاه شما قبلا ثبت شده است"})
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
        car_serializer = AdSerializer(instance=obj.cars.filter(status="active"), many=True,
                                      context={'request': self.context['request']})
        return car_serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['car', 'added_on']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name']



