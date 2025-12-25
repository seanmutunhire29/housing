from django import forms
from .models import Property, PropertyImage, Amenity
from django.core.validators import MinValueValidator
import datetime

class PropertyForm(forms.ModelForm):
    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False
    )
    amenities = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter amenities separated by commas'}),
        required=False
    )
    
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'room_type',
            'address', 'city', 'state', 'zip_code', 'country',
            'nearest_university', 'distance_to_university', 'transport_options',
            'bedrooms', 'bathrooms', 'area_sqft', 'maximum_occupants',
            'minimum_stay_months', 'price_per_month', 'security_deposit',
            'available_from', 'available_to',
            'furnished', 'has_kitchen', 'has_laundry', 'has_parking',
            'has_gym', 'has_pool', 'pet_friendly', 'smoking_allowed',
            'utilities_included', 'wifi_included'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'transport_options': forms.Textarea(attrs={'rows': 3}),
            'available_from': forms.DateInput(attrs={'type': 'date'}),
            'available_to': forms.DateInput(attrs={'type': 'date'}),
            'price_per_month': forms.NumberInput(attrs={'min': 0}),
            'security_deposit': forms.NumberInput(attrs={'min': 0}),
            'distance_to_university': forms.NumberInput(attrs={'min': 0, 'step': 0.1}),
            'bathrooms': forms.NumberInput(attrs={'min': 0, 'step': 0.5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date for available_from to today
        self.fields['available_from'].widget.attrs['min'] = datetime.date.today().isoformat()
        if self.fields.get('available_to'):
            self.fields['available_to'].widget.attrs['min'] = datetime.date.today().isoformat()
    
    def clean(self):
        cleaned_data = super().clean()
        available_from = cleaned_data.get('available_from')
        available_to = cleaned_data.get('available_to')
        
        if available_to and available_from and available_to < available_from:
            self.add_error('available_to', 'Available to date must be after available from date.')
        
        return cleaned_data

class PropertySearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search properties...',
        'class': 'w-full'
    }))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'City',
        'class': 'w-full'
    }))
    min_price = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={
        'placeholder': 'Min Price',
        'class': 'w-full'
    }))
    max_price = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={
        'placeholder': 'Max Price',
        'class': 'w-full'
    }))
    property_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Type')] + list(Property.PROPERTY_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'w-full'})
    )
    room_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Room')] + list(Property.ROOM_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'w-full'})
    )
    bedrooms = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs={
        'placeholder': 'Bedrooms',
        'class': 'w-full'
    }))
    furnished = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    pet_friendly = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    utilities_included = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    has_parking = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            self.add_error('max_price', 'Maximum price must be greater than minimum price.')
        
        return cleaned_data