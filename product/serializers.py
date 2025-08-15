from itertools import product

from rest_framework import serializers
from unicodedata import category

from .models import Category, Product, Review
from django.db.models import Avg, Count
from rest_framework.exceptions import ValidationError
from common.validators import validate_user_is_adult
from .models import Product
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('owner',)

    def _get_birthday_from_token(self):
        request = self.context['request']
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token_str = auth_header.split(' ')[1]
        try:
            access_token = AccessToken(token_str)
            birthday_str = access_token.get('birthday')
            if birthday_str and birthday_str != "None":
                return datetime.strptime(birthday_str, "%Y-%m-%d").date()
            return None
        except Exception:
            return None

    def validate(self, attrs):
        birthday = self._get_birthday_from_token()
        validate_user_is_adult(birthday)
        return attrs

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'stars']

class ProductWithReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'reviews', 'rating']

    def get_rating(self, obj):
        return obj.reviews.aggregate(Avg('stars'))['stars__avg']

class CategoryWithCountSerialzier(serializers.ModelSerializer):
    products_count = serializers.IntegerField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']


class ProductValidateSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False)
    price = serializers.IntegerField()
    category = serializers.IntegerField()


    def validate(self, attrs):
        category = attrs["category"]
        try:
            Category.objects.get(id=category)
        except Category.DoesNotExist:
            raise ValidationError('Category does not exist!')
        return attrs

class CategoryValidateSerializer(serializers.Serializer):
    name = serializers.CharField()


class ReviewValidateSerializer(serializers.Serializer):
    text = serializers.CharField(required=False)
    product = serializers.IntegerField()
    stars = serializers.FloatField(min_value=1, max_value=11)

    def validate(self, attrs):
        product = attrs['product']
        try:
            Product.objects.get(id=product)
        except Product.DoesNotExist:
            raise ValidationError('Product does not exist!')
        return attrs