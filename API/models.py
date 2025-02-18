from rest_framework.authtoken.models import Token
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator ,MaxLengthValidator

from project import settings

class User(AbstractUser):
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=False,
        blank=False,
        validators=[MinLengthValidator(11),MaxLengthValidator(12)],  # التأكد من أن طول الحقل لا يقل عن 11 حرفًا
        help_text="Phone number must be exactly 11 or 12 characters long."
    )
    
    GENDER_CHOICES = [ 
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    
    def __str__(self):
        return self.username

    

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Meal(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="meals")
    image = models.ImageField(upload_to='meals/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
    def no_of_reviews(self):
        """ Return the number of reviews for this meal """
        review_list = Review.objects.filter(meal=self)
        return review_list.count()

    def average_rating(self):
        """ Calculate and return the average rating for this meal """
        review_list = Review.objects.filter(meal=self)
        if review_list.exists():
            total_rating = sum(review.rating for review in review_list)
            return total_rating / review_list.count()
        return 0


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="reviews")
    slug = models.SlugField(unique=True, blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'meal')  # Prevent duplicate reviews by the same user

    def save(self, *args, **kwargs):
        if self.rating > 5.0:
            raise ValueError("Rating must be between 0 and 5")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.meal.name} ({self.rating}★)"
