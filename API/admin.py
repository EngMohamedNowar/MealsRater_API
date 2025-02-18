from django.contrib import admin
from .models import Meal, Category, Review

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price','created_at')
    search_fields = ('name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'meal', 'rating', 'created_at')
    search_fields = ('user__username', 'meal__name')
    list_filter = ('rating',)
