from django.urls import include, path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    MealListCreateView, MealDetailView,
    ReviewListCreateView, ReviewDetailView ,UserView
)
#import router
from rest_framework import routers

router = routers.DefaultRouter()

router.register('users', UserView)

urlpatterns = [
    # 📌 Categories
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<str:slug>/', CategoryDetailView.as_view(), name='category-detail'),

    # 📌 Meals
    path('meals/', MealListCreateView.as_view(), name='meal-list'),
    path('meals/<str:slug>/', MealDetailView.as_view(), name='meal-detail'),

    # 📌 Reviews
    path('meals/<str:meal_slug>/reviews/', ReviewListCreateView.as_view(), name='review-list'),
    path('reviews/<str:slug>/', ReviewDetailView.as_view(), name='review-detail'),

    # 📌 Users
    path('users/me/', UserView.as_view({'put': 'update', 'delete': 'destroy'}), name='user-me'),

    # API endpoints for the router
    path('', include(router.urls)),
]