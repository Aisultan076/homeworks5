from itertools import product

from rest_framework import serializers
from unicodedata import category

from .models import Category, Product, Review
from django.db.models import Avg, Count
from rest_framework.exceptions import ValidationError
from common.validators import validate_user_is_adult

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('owner',)

    def validate(self, attrs):
        user = self.context['request'].user
        validate_user_is_adult(user.birthday)
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