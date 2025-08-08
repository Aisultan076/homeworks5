from django.urls import path
from .views import (
    CategoryListCreateAPIView, CategoryDetailAPIView,
    CategoryWithCountAPIView, ProductListCreateAPIView,
    ProductDetailAPIView, ProductWithReviewsAPIView,
    ReviewListCreateAPIView, ReviewDetailAPIView,
    ModeratorProductListAPIView
)

urlpatterns = [
    path('categories/', CategoryListCreateAPIView.as_view()),
    path('categories/<int:id>/', CategoryDetailAPIView.as_view()),
    path('', ProductListCreateAPIView.as_view()),
    path('<int:id>/', ProductDetailAPIView.as_view()),
    path('reviews/', ReviewListCreateAPIView.as_view()),
    path('reviews/<int:id>/', ReviewDetailAPIView.as_view()),
    path('products/reviews/', ProductWithReviewsAPIView.as_view()),
    path('categories/count/', CategoryWithCountAPIView.as_view()),
    path('my-products/', ModeratorProductListAPIView.as_view()),
]
