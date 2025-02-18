from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, pagination
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Meal, Category, Review
from .serializers import MealSerializer, CategorySerializer, ReviewSerializer

# ✅ قاعدة مشتركة لجميع الفئات التي تعتمد على Slug
class BaseSlugView:
    lookup_field = 'slug'

# ✅ إعداد Pagination عام
class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# ===============================
# 🌟 CATEGORY VIEWS
# ===============================
class CategoryListCreateView(BaseSlugView, generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination  # ✅ إضافة Pagination

class CategoryDetailView(BaseSlugView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# ===============================
# 🍽 MEAL VIEWS
# ===============================
class MealListCreateView(BaseSlugView, generics.ListCreateAPIView):
    queryset = Meal.objects.select_related('category').prefetch_related('reviews')
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination  # ✅ إضافة Pagination

class MealDetailView(BaseSlugView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Meal.objects.select_related('category').prefetch_related('reviews')
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# ===============================
# ⭐ REVIEW VIEWS
# ===============================
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination  # ✅ إضافة Pagination

    def get_queryset(self):
        """جلب المراجعات الخاصة بوجبة معينة باستخدام `slug`"""
        meal_slug = self.kwargs['meal_slug']
        return Review.objects.filter(meal__slug=meal_slug).select_related('user', 'meal')

    def perform_create(self, serializer):
        """ضمان أن المستخدم المصادق عليه فقط يمكنه إنشاء مراجعة"""
        if self.request.user.is_anonymous:
            raise PermissionDenied("You must be logged in to submit a review.")
        serializer.save(user=self.request.user)

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        """جلب مراجعة معينة مع التأكد من أنها تخص المستخدم الحالي"""
        review = get_object_or_404(Review, pk=self.kwargs['pk'], user=self.request.user)
        return review
