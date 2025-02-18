from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions , viewsets ,status ,request
from rest_framework.response import Response

from project import settings
from .pagination import StandardResultsSetPagination
from rest_framework.exceptions import PermissionDenied
from .models import Meal, Category, Review
from .serializers import MealSerializer, CategorySerializer, ReviewSerializer ,UserSerializer
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
#import token
from rest_framework.authtoken.models import Token
#import isauthenticatied
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save



# ✅ قاعدة مشتركة لجميع الفئات التي تعتمد على Slug
class BaseSlugView:
    lookup_field = 'slug'

#class user
class UserView(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Return the data for the user associated with the provided token."""
        auth_header = self.request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            
            # Attempt to get the user associated with the token
            try:
                token = Token.objects.get(key=token_key)
                return get_user_model().objects.filter(id=token.user.id)
            except Token.DoesNotExist:
                return get_user_model().objects.none()

        # If no valid token is provided, return an empty queryset
        return get_user_model().objects.none()

    # Register a user and return their token
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the user
        user = serializer.save()

        # Attempt to create or retrieve the token
        try:
            token, _ = Token.objects.get_or_create(user=user)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'user': serializer.data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        token_key = request.headers.get('Authorization', '').replace('Token ', '')

        try:
            # البحث عن التوكن في قاعدة البيانات
            token = Token.objects.get(key=token_key)
            instance = token.user  # المستخدم المرتبط بالتوكن

            # دعم التحديث الجزئي (PATCH)
            partial = kwargs.pop('partial', False)

            # إنشاء Serializer مع البيانات الجديدة
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)  # التحقق من صحة البيانات

            # تنفيذ التحديث
            self.perform_update(serializer)

            # إرجاع استجابة ناجحة
            return Response({
                'message': 'Successfully updated',
                'user': serializer.data
            }, status=status.HTTP_200_OK)

        except Token.DoesNotExist:
            return Response({'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)
    # Delete a user
    def destroy(self, request, *args, **kwargs):
        token_key = request.headers.get('Authorization', '').replace('Token ', '')

        try:
            # البحث عن التوكن في قاعدة البيانات
            token = Token.objects.get(key=token_key)
            user = token.user  # المستخدم المرتبط بالتوكن

            # حذف المستخدم
            self.perform_destroy(user)
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        except Token.DoesNotExist:
            return Response({'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)

    # List users (forbidden by default)
    def list(self, request, *args, **kwargs):

        token_key = self.request.headers.get('Authorization', '').replace('Token ', '')

        try:
            # Get the user associated with the token
            token = Token.objects.get(key=token_key)
            user = token.user

            # Serialize and return the user's data
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Token.DoesNotExist:
            return Response({'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)

    # Custom permissions based on the action
    def get_permissions(self):
        if self.action in ['destroy', 'list', 'update']:
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()



# ✅ إعداد Pagination عام

# ===============================
# 🌟 CATEGORY VIEWS
# ===============================
class CategoryListCreateView(BaseSlugView, generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    # pagination_class = StandardResultsSetPagination
    # authentication_classes = [TokenAuthentication]

class CategoryDetailView(BaseSlugView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

# ===============================
# 🍽 MEAL VIEWS
# ===============================
class MealListCreateView(BaseSlugView, generics.ListCreateAPIView):
    queryset = Meal.objects.select_related('category').prefetch_related('reviews')
    serializer_class = MealSerializer
    # permission_classes = [permissions.IsAuthenticated]  # Allow read access but restrict write
    # authentication_classes = [TokenAuthentication]
    pagination_class = StandardResultsSetPagination

class MealDetailView(BaseSlugView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Meal.objects.select_related('category').prefetch_related('reviews')
    serializer_class = MealSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

# ===============================
# ⭐ REVIEW VIEWS
# ===============================
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # authentication_classes = [TokenAuthentication]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Get reviews for a specific meal using `slug`."""
        meal_slug = self.kwargs['meal_slug']
        return Review.objects.filter(meal__slug=meal_slug).select_related('user', 'meal')

    def perform_create(self, serializer):
        print(f"User: {self.request.user}, Is Authenticated: {self.request.user.is_authenticated}")
        if self.request.user.is_anonymous:
            raise PermissionDenied("You must be logged in to submit a review.")
        serializer.save(user=self.request.user)

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    # permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can retrieve or update
    # authentication_classes = [TokenAuthentication]
    def get_object(self):
        """البحث عن مراجعة باستخدام meal__slug."""
        review = get_object_or_404(Review, meal__slug=self.kwargs['slug'], user=self.request.user)
        return review

