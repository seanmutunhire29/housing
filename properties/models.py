from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
import uuid

class Property(models.Model):
    PROPERTY_TYPE_CHOICES = (
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('condo', 'Condo'),
        ('studio', 'Studio'),
        ('dorm', 'Dormitory'),
        ('shared', 'Shared Room'),
    )
    
    ROOM_TYPE_CHOICES = (
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('triple', 'Triple Room'),
        ('entire', 'Entire Unit'),
        ('shared', 'Shared Room'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='US')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Pricing
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    utilities_included = models.BooleanField(default=False)
    wifi_included = models.BooleanField(default=False)
    
    # Property details
    bedrooms = models.IntegerField()
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1)
    area_sqft = models.IntegerField(null=True, blank=True)
    furnished = models.BooleanField(default=False)
    has_kitchen = models.BooleanField(default=True)
    has_laundry = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_gym = models.BooleanField(default=False)
    has_pool = models.BooleanField(default=False)
    pet_friendly = models.BooleanField(default=False)
    smoking_allowed = models.BooleanField(default=False)
    
    # University proximity
    nearest_university = models.CharField(max_length=255)
    distance_to_university = models.DecimalField(max_digits=6, decimal_places=2)
    transport_options = models.TextField(blank=True)
    
    # Availability
    available_from = models.DateField()
    available_to = models.DateField(null=True, blank=True)
    minimum_stay_months = models.IntegerField(default=1)
    maximum_occupants = models.IntegerField(default=1)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verification_notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_properties')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Stats
    view_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Properties"
    
    def __str__(self):
        return f"{self.title} - {self.city}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('property_detail', args=[str(self.id)])
    
    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()
    
    @property
    def display_price(self):
        return f"${self.price_per_month:,.2f}/month"
    
    @property
    def amenities_list(self):
        amenities = []
        if self.furnished:
            amenities.append('Furnished')
        if self.has_kitchen:
            amenities.append('Kitchen')
        if self.has_laundry:
            amenities.append('Laundry')
        if self.has_parking:
            amenities.append('Parking')
        if self.has_gym:
            amenities.append('Gym')
        if self.has_pool:
            amenities.append('Pool')
        if self.pet_friendly:
            amenities.append('Pet Friendly')
        if self.utilities_included:
            amenities.append('Utilities Included')
        if self.wifi_included:
            amenities.append('WiFi Included')
        return amenities

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'uploaded_at']

class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='videos')
    video_url = models.URLField()
    thumbnail = models.ImageField(upload_to='video_thumbnails/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Amenity(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='amenities')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name_plural = "Amenities"

class FavoriteProperty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'property']