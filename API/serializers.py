from rest_framework import serializers
from .models import Meal, Category, Review

# ✅ CATEGORY SERIALIZER
class CategorySerializer(serializers.ModelSerializer):
    total_meals = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['name','slug', 'total_meals']
        read_only_fields = ['slug']
    def get_total_meals(self, obj):
        """هذه الدالة تُعيد عدد الوجبات المرتبطة بكل تصنيف"""
        return obj.meals.count()  # 👈 `meals` هو related_name في `Meal.category`
# ✅ MEAL SERIALIZER
class MealSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)  # عرض اسم الفئة
    category_slug = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug', source='category'
    )  # حفظ التصنيف باستخدام `slug` بدلًا من `id`
    

    class Meta:
        model = Meal
        fields = [
            'slug', 'name', 'description', 'price', 'image', 'category_slug','no_of_reviews', 'average_rating',
            'category', 'created_at',
        ]
        read_only_fields = ['slug',  'created_at']


# ✅ REVIEW SERIALIZER
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')  # عرض اسم المستخدم فقط
    meal_slug = serializers.SlugRelatedField(
        queryset=Meal.objects.all(),
        slug_field='slug',
        source='meal'  # هذا يربط الـ slug بحقل الـ meal في الـ Review
    )

    class Meta:
        model = Review
        fields = ['id', 'user', 'meal_slug', 'rating', 'comment', 'created_at']
        extra_kwargs = {
            'meal': {'write_only': True}  # إخفاء `meal` من الاستجابة
        }

    def validate_rating(self, value):
        """تأكد أن التقييم بين 0 و 5"""
        if value < 0 or value > 5:
            raise serializers.ValidationError("❌ Rating must be between 0 and 5.")
        return value
