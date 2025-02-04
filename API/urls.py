from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    MealListCreateView, MealDetailView,
    ReviewListCreateView, ReviewDetailView
)

urlpatterns = [
    # 📌 Categories
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<str:slug>/', CategoryDetailView.as_view(), name='category-detail'),

    # 📌 Meals
    path('meals/', MealListCreateView.as_view(), name='meal-list'),
    path('meals/<str:slug>/', MealDetailView.as_view(), name='meal-detail'),

    # 📌 Reviews
    path('meals/<str:meal_slug>/reviews/', ReviewListCreateView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),  # ✅ إصلاح المشكلة
]
