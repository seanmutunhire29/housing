from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('landlord', 'Landlord'),
        ('admin', 'Admin'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    university = models.CharField(max_length=255, blank=True)
    student_id = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='verification_docs/', null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preferred_location = models.CharField(max_length=255, blank=True)
    room_type_preference = models.CharField(max_length=50, blank=True)
    move_in_date = models.DateField(null=True, blank=True)
    special_requirements = models.TextField(blank=True)
    
    def __str__(self):
        return f"Student Profile: {self.user.username}"

class LandlordProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord_profile')
    company_name = models.CharField(max_length=255, blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_listings = models.IntegerField(default=0)
    verified_since = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Landlord Profile: {self.user.username}"