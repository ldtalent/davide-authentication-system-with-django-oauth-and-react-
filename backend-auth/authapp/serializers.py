from PIL import Image
from django.core.files import File
from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class ProfileCreateSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    mobile_number = serializers.CharField(min_length=10, max_length=10, validators=[UniqueValidator(queryset=Profile.objects.all())])
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Profile
        fields = ['user','confirm_password', 'gender', 'mobile_number', 'birth_date', 'profile_picture']

    def validate_mobile_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Mobile number must contain digits only.")
        return value

    def validate(self, attrs):
        user_data = attrs.get('user')
        password = user_data.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        first_name = user_data.pop('first_name')
        last_name = user_data.pop('last_name')

        password = user_data.pop('password')
        confirm_password = validated_data.pop('confirm_password')
        username = user_data['username']
        email = user_data['email']

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        try:
            user = User.objects.get(Q(username=username) | Q(email=email))
            raise serializers.ValidationError("User with this username or email already exists.")
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        profile_picture = validated_data.pop('profile_picture', None)
        profile, created = Profile.objects.get_or_create(user=user, defaults=validated_data)


        if profile_picture:
            # profile, created = Profile.objects.get_or_create(user=user, defaults=validated_data)
            profile.profile_picture = profile_picture  # Assign the uploaded profile picture to the profile
            profile.save()
        else:
            profile.generate_thumbnail()
            initials = f"{first_name[:2]}".upper()
            thumbnail_path = f"profile_pics/thumbnails/{initials}.png"
            validated_data['profile_picture'] = thumbnail_path
            try:
                with Image.open(f"profile_pics/default_thumbnail.png") as default_image:
                    default_image.thumbnail((100, 100))
                    default_image.save(thumbnail_path)

                with open(thumbnail_path, 'rb') as f:
                    profile.profile_picture.save(thumbnail_path, File(f), save=True)

            except FileNotFoundError:
                pass

            for attr, value in validated_data.items():
                setattr(profile, attr, value)

            profile.save()  # Save the profile after updating the fields

        return profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class PasswordUpdateSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True)
    new_password = serializers.CharField(max_length=128, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect old password.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        user.set_password(validated_data['new_password'])
        user.save()
        return user