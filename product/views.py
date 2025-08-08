from django.template.context_processors import request
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Category, Review
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer, ProductDetailSerializer, ReviewValidateSerializer
from .serializers import ProductWithReviewsSerializer, CategoryWithCountSerialzier, ProductValidateSerializer, CategoryValidateSerializer
from django.db.models import Count
from django.db import transaction
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from common.permissions import IsModeratorPermission

class CategoryListCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategoryValidateSerializer
        return CategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = Category.objects.create(name=serializer.validated_data['name'])
        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)


class CategoryDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CategoryValidateSerializer
        return CategorySerializer

    def update(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category.name = serializer.validated_data['name']
        category.save()
        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)

class ProductListCreateAPIView(ListCreateAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsModeratorPermission]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductValidateSerializer
        return ProductSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            product = Product.objects.create(
                title=serializer.validated_data['title'],
                description=serializer.validated_data['description'],
                price=serializer.validated_data['price'],
                category_id=serializer.validated_data['category'],
                moderator=request.user
            )
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

class ModeratorProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(moderator=self.request.user).select_related('category')

class ProductDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    lookup_field = 'id'
    permission_classes = [IsModeratorPermission]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductValidateSerializer
        return ProductDetailSerializer

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product.title = serializer.validated_data['title']
        product.description = serializer.validated_data['description']
        product.price = serializer.validated_data['price']
        product.category_id = serializer.validated_data['category']
        product.save()
        return Response(ProductDetailSerializer(product).data, status=status.HTTP_201_CREATED)

class ReviewListCreateAPIView(ListCreateAPIView):
    queryset = Review.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewValidateSerializer
        return ReviewSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = Review.objects.create(
            text=serializer.validated_data['text'],
            product_id=serializer.validated_data['product'],
            stars=serializer.validated_data['stars']
        )
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

class ReviewDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ReviewValidateSerializer
        return ReviewSerializer

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review.text = serializer.validated_data['text']
        review.product_id = serializer.validated_data['product']
        review.stars = serializer.validated_data['stars']
        review.save()
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

class ProductWithReviewsAPIView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductWithReviewsSerializer


class CategoryWithCountAPIView(ListCreateAPIView):
    serializer_class = CategoryWithCountSerialzier

    def get_queryset(self):
        return Category.objects.annotate(products_count=Count('products'))



@api_view(['GET', 'POST'])
def category_list_create_api_view(request):
    if request.method == 'GET':
       category = Category.objects.all()

       data = CategorySerializer(instance=category, many=True).data

       return Response(
         data=data,
         status=status.HTTP_200_OK
       )
    if request.method == 'POST':
        serializer = CategoryValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)
        name = serializer.validated_data.get('name')

        category = Category.objects.create(
            name=name
        )
        category.save()

        return Response(status=status.HTTP_201_CREATED,
                        data=CategorySerializer(category).data)

@api_view(['GET', 'PUT', 'DELETE'])
def category_detail_api_view(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return Response(data={'error': f'Category with id = {str(id)} does not exist!'},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
      data = CategorySerializer(category).data
      return Response(data=data)
    elif request.method == 'PUT':
        serializer = CategoryValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)
        category.name = serializer.validated_data.get('name')
        category.save()
        return Response(status=status.HTTP_201_CREATED,
                       data=CategorySerializer(category).data)
    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(http_method_names=['GET', 'POST'])
def product_list_api_view(request):
    if request.method == 'GET':
       product = Product.objects.all()

       data = ProductSerializer(instance=product, many=True).data

       return Response(
        data=data,
        status=status.HTTP_200_OK
       )
    if request.method == 'POST':
        serializer = ProductValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)
        title = serializer.validated_data.get('title')
        description = serializer.validated_data.get('description')
        price = serializer.validated_data.get('price')
        category = serializer.validated_data.get('category')

        with transaction.atomic():
         product = Product.objects.create(
            title=title,
            description=description,
            price=price,
            category_id=category
         )
         product.save()

        return Response(status=status.HTTP_201_CREATED,
                        data=ProductSerializer(product).data)

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail_api_view(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response(data={'error': f'Product with id = {str(id)} does not exist!'},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
       data = ProductDetailSerializer(product).data
       return Response(data=data)
    elif request.method == 'PUT':
        serializer = ProductValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)
        product.title = serializer.validated_data.get('title')
        product.description = serializer.validated_data.get('description')
        product.price = serializer.validated_data.get('price')
        product.category_id = serializer.validated_data.get('category')
        product.save()

        return Response(status=status.HTTP_201_CREATED,
                        data=ProductDetailSerializer(product).data)
    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def review_list_api_view(request):
    if request.method == 'GET':

        review = Review.objects.all()

        data = ReviewSerializer(review, many=True).data
        return Response(
        data=data,
        status=status.HTTP_200_OK
        )
    if request.method == 'POST':
        serializer = ReviewValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)
        text = serializer.validated_data.get('text')
        product = serializer.validated_data.get('product')
        stars = serializer.validated_data.get('stars')

        review = Review.objects.create(
            text=text,
            product_id=product,
            stars=stars
        )
        review.save()

        return Response(status=status.HTTP_201_CREATED,
                        data=ReviewSerializer(review).data)

@api_view(['GET', 'PUT', 'DELETE'])
def review_detail_api_view(request, id):
    try:
        review = Review.objects.get(id=id)
    except Review.DoesNotExist:
        return Response(data={'error': f'Review with id = {str(id)} does not exist!'},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
         data = ReviewSerializer(review).data
         return Response(data=data)
    elif request.method == 'PUT':
        serializer = ReviewValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)
        review.text = serializer.validated_data.get('text')
        review.product_id = serializer.validated_data.get('product')
        review.stars = serializer.validated_data.get('stars')
        review.save()

        return Response(status=status.HTTP_201_CREATED,
                        data=ReviewSerializer(review).data)
    elif request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def product_review_list_api_view(request):
    product = Product.objects.all()

    data = ProductWithReviewsSerializer(instance=product, many=True).data

    return Response(
        data=data,
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def category_count_list_api_view(request):
    category = Category.objects.annotate(products_count=Count('products'))

    data = CategoryWithCountSerialzier(instance=category, many=True).data


    return Response(
        data=data,
        status=status.HTTP_200_OK
    )